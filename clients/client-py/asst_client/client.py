# Copyright © 2022 Nikolay Shishov. All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import json
from functools import partial

import socketio
from logger import LoggerHandler

log = LoggerHandler.new(__name__)
serverlog = []


class Client:
    sio = socketio.Client()

    def __init__(self, asst_ip: str) -> None:
        self.sio.connect(asst_ip)
        self.serverlog = serverlog

    @sio.event
    def connect():
        log.info("connection established")

    @sio.event
    def exec(self, data):
        out = None

        def callback(*data):
            nonlocal out
            out = data

        log.info(f"command sended: {data}")
        self.sio.emit("message", data, callback=callback)
        while not out:
            pass
        return json.loads(out[0])

    @sio.event
    def server_log(data):
        serverlog.append(data)
        if "[DEBUG]" in data:
            log.debug(f"server said: {str(data)}")
        if "[INFO]" in data:
            log.info(f"server said: {str(data)}")
        if "[WARNING]" in data:
            log.warning(f"server said: {str(data)}")
        if "[ERROR]" in data:
            log.error(f"server said: {str(data)}")
        if "[CRITICAL]" in data:
            log.critical(f"server said: {str(data)}")

    @sio.event
    def disconnect(self):
        log.info("disconnected from server")


class ClientWrapper:
    @staticmethod
    def mkfunc(name):
        def func(client, func, *args):
            result = client.exec(
                {
                    "type": "module",
                    "job": "ssh",
                    "func": func,
                    "params": args,
                }
            )
            match result:
                case [var1] if var1 is False:
                    log.warning("server not return any positive result")
                case [var1, var2] if var1 == 0:
                    log.debug(f"Result received from server: {var2}")
                case [var1, var2] if var1 != 0:
                    log.warning(f"RC: {var1} | {var2}")
                case []:
                    log.error("no answer from server")
            return result

        return func

    def __init__(self, asst_ip: str):
        self.client = Client(asst_ip)
        commands = self.client.exec(
            {"type": "system", "job": "get_server_command_list"}
        )
        log.debug(f"Server's commands: {commands}")
        for command in commands:
            func = partial(self.mkfunc(command), self.client, command)
            setattr(self.__class__, command, staticmethod(func))

    def ssh_init(self, params):
        result = self.client.exec(
            {"type": "system", "job": "ssh_connection_init", "params": params}
        )
        if result:
            log.info("server set SSH connection data successfuly")

    def server_log(self, data):
        self.client.server_log(data)

    def exit(self):
        self.client.disconnect()
