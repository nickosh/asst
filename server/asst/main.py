# Automation Support Service Template

# Template of automation server which can be used to handle various automation scenarious.
# It can be used in various scopes: from microservises to the main automation node.
# Powered with SocketIO so client's programming languages not limited strictly.
# You can check supported languages for clients here: https://socket.io/docs/
# Some client's examples provided in this repository as well.

# Copyright © 2022 Nikolay Shishov. All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import configparser
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import eventlet
import socketio
from connector import ConnectionHandler
from logger import LoggerHandler

# SocketIO initialization
sio = socketio.Server()
app = socketio.WSGIApp(sio)
# First init of logger singleton
log = LoggerHandler(name=__name__, sio=sio)
# Global dict to keep all ssh connections params from clients
ssh_connects: dict = {}
app_workdir = Path(__file__).cwd()

# Config init
def config_init(workdir: Path):
    config = configparser.ConfigParser()
    config_path = Path(workdir, "config.ini")
    if config_path.exists():
        config.read(config_path)
        return config
    else:
        msg = "Can't start server because no config file was found"
        log.error(msg)
        raise EnvironmentError(msg)


app_config = config_init(app_workdir)

# App params
try:
    SERVER_IP: str = app_config["server"]["ip"]
    SERVER_PORT: int = app_config["server"].getint("port")
except Exception as e:
    log.error(f"Fail to load app params: {e}")

# Data class for client's ssh params.
@dataclass
class SshParams:
    ssh_ip: Optional[str]
    ssh_hostname: Optional[str]
    ssh_user: Optional[str]
    ssh_pass: Optional[str]
    ssh_port: int = 22

    def ready(self):
        if self.ssh_ip and self.ssh_user and self.ssh_pass and self.ssh_port:
            return True
        else:
            return False


# This function executed when new client connected.
@sio.event
def connect(sid, _):
    # Lets create new SshParams object for connected client and store it into our global params list.
    # With empty params for now. Because we do not force client to connect ssh from start.
    # And client can change ssh params on the fly in any moment.
    ssh_connects[sid] = SshParams(None, None, None, None)
    log.info(f"{sid} connected")


# Main function to maintain client-server messages exchange.
@sio.event
def message(sid, data):
    msg_result = None
    log.info(f"server received command: {str(data)}", sid)
    # Lets check what client wants from us.
    # Structure of client's messages ('data' variable):
    # # type: str - can be 'system' or 'module' so far
    # # job: str - name of the job for server to looking for inside
    # # func: str - name of the function to execute inside module
    # # params: str - addition variables for function

    # TODO: Standartization and validation of client's message

    # 'System' type for server's system stuff, like various connections
    if "system" in data["type"]:
        # If client requests server command list
        if "get_server_command_list" in data["job"]:
            # jobs modules import must be inside message func
            from jobs import server

            msg_result = [
                func
                for func in dir(server)
                if callable(getattr(server, func)) and not func.startswith("__")
            ]
        # If client want to set params for ssh connection
        if "ssh_connection_init" in data["job"]:
            check_conn = [
                conn
                for conn in ssh_connects.values()
                if conn.ssh_ip == data["params"]["ssh_ip"]
            ]
            if len(check_conn) > 0:
                if (
                    ssh_connects[sid]
                    and ssh_connects[sid].ssh_ip == data["params"]["ssh_ip"]
                ):
                    log.warning("Your already use same SSH connection params", sid)
                else:
                    log.error("Oops, somebody already works with same ip", sid)
                    log.warning(
                        "Your SSH connection params dropped off. Please reinit.", sid
                    )
                    msg_result = {"result": False}
                    ssh_connects[sid] = SshParams(None, None, None, None)
            else:
                try:
                    ssh_connects[sid].ssh_ip = data["params"]["ssh_ip"]
                    if "ssh_hostname" in data["params"]:
                        ssh_connects[sid]["ssh_hostname"] = data["params"][
                            "ssh_hostname"
                        ]
                    ssh_connects[sid].ssh_user = data["params"]["ssh_user"]
                    ssh_connects[sid].ssh_pass = data["params"]["ssh_pass"]
                    if "ssh_port" in data["params"]:
                        ssh_connects[sid].ssh_port = data["params"]["ssh_port"]
                    msg_result = {"result": True}
                except Exception as e:
                    log.error(f"server can't set SSH connection data: {e}", sid)
                    msg_result = {"result": False}
    # 'Module' type for calling varios server's modules
    elif "module" in data["type"]:
        # TODO: 'Job' is part of this func right now. Will good to rework it.
        # if clinet want to work with SSH jobs
        if "ssh" in data["job"]:
            # jobs modules import must be inside message func
            from jobs import server

            try:
                conn = ConnectionHandler(ssh_connects[sid])
                if data["job"] == "ssh":
                    func = getattr(server, data["func"])
                    result = func(conn, data["params"])
                    conn.close()
                    msg_result = result
            except Exception as e:
                log.error(f"server did't init SSH connection: {e}", sid)
                msg_result = {"result": False}
    # return of answer in json format
    return json.dumps(msg_result)


# This function executed when client disconnected.
@sio.event
def disconnect(sid):
    # Lets remove client's connection params from global list
    ssh_connects.pop(sid)
    log.info(f"{sid} disconnected")


if __name__ == "__main__":
    eventlet.wsgi.server(eventlet.listen((SERVER_IP, SERVER_PORT)), app)
