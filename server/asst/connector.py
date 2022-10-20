# Copyright © 2022 Nikolay Shishov. All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging
import re
from dataclasses import dataclass
from pathlib import Path

import paramiko
from paramiko import SSHClient, client


class ConnectionHandler:
    def __init__(self, conn_params: dataclass):
        self.workdir = Path(__file__).parent.absolute()
        self.log = logging.getLogger(__name__)

        if not conn_params.ready():
            msg = "connection params missed"
            self.log.exception(msg)
            raise ValueError(msg)

        # --- Params ---
        self.ip_ha = conn_params.ssh_ip
        self.hostname = conn_params.ssh_hostname
        self.port = conn_params.ssh_port
        self.username = conn_params.ssh_user
        self.password = conn_params.ssh_pass
        # --- End of params block ---
        self.session_ha = self._ha_init(
            self.ip_ha, self.port, self.username, self.password
        )
        self.is_proxy = True

        cur_srv = str(self._ssh_execute(self.session_ha, "hostname")[1][0])
        if not self.hostname or cur_srv == self.hostname:
            self.session_srv = self.session_ha
            self.is_proxy = False
        else:
            try:
                self.session_srv = self._srv_init(
                    self.session_ha, self.hostname, self.port
                )
            except Exception as e:
                self.session_ha.close()
                msg = f"jump server not found: {e}"
                self.log.exception(msg)
                raise ConnectionError(msg)

    def _ha_init(self, ssh_ip: str, ssh_port: str, ssh_user: str, ssh_passw: str):
        """Init SSH session to HA

        Arguments:
            ssh_ip {str} -- server's ip
            ssh_port {str} -- server's port
            ssh_user {str} -- username for ssh connection
            ssh_passw {str} -- password for ssh connection

        Returns:
            object -- SSHClient()
        """
        try:
            ssh = SSHClient()
            # ssh.load_system_host_keys()
            ssh.set_missing_host_key_policy(client.AutoAddPolicy)
            ssh.connect(
                ssh_ip,
                port=ssh_port,
                username=ssh_user,
                password=ssh_passw,
                timeout=120,
            )
            return ssh
        except paramiko.AuthenticationException:
            self.log.exception("Authentication failed, please verify your credentials.")
            raise
        except paramiko.BadHostKeyException as badHostKeyException:
            self.log.exception(
                "Unable to verify server's host key:",
                badHostKeyException,
            )
            raise
        except paramiko.SSHException as sshException:
            self.log.exception("Unable to establish SSH connection:", sshException)
            raise
        except TimeoutError:
            self.log.exception("Host not properly respond")
            raise

    def _srv_init(self, session_ha: object, hostname: str, port: int):
        """Init SSH connection from local to server with ha as proxy

        Arguments:
            session_ha {object} -- connection to the ha
            hostname {str} -- target jump server name

        Returns:
            object -- ssh connection
        """
        transport = session_ha.get_transport()
        dest_ip = (hostname, port)
        local_ip = ("127.0.0.1", port)
        channel = transport.open_channel("direct-tcpip", dest_ip, local_ip)

        ssh = SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(client.AutoAddPolicy)
        if hostname:
            try:
                ssh.connect(
                    "127.0.0.1",
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    sock=channel,
                )
            except Exception as e:
                self.session_ha.close()
                self.log.exception("Connecting with proxy:", e)
                raise
        else:
            self.session_ha.close()
            msg = "Wrong target name when connect with proxy"
            self.log.exception(msg)
            raise ConnectionError(msg)
        return ssh

    def _ssh_execute(self, ssh: object, cmd: str) -> tuple:
        """Inner SSH exec linked to ssh object

        Arguments:
            cmd {str} -- command to execute
            ssh {object} -- ssh object

        Returns:
            str -- response code
            str -- output message
        """
        chan = ssh.get_transport().open_session()
        if chan:
            try:
                chan.get_pty()
                chan.exec_command(cmd)
                response_code = chan.recv_exit_status()
            except Exception as e:
                chan.close()
                self.log.exception("Channel Error:", e)
                raise
        else:
            msg = "SSH channel not establish"
            self.log.exception(msg)
            raise ConnectionError(msg)
        output = chan.makefile().readlines()
        output = [line.strip() for line in output]
        self.log.debug("cmd: {}; rc: {}; out: {}".format(cmd, response_code, output))
        if response_code != 0:
            self.log.debug(
                "WARNING - RC NOT 0 >> cmd: {}; rc: {}; out: {}".format(
                    cmd, response_code, output
                )
            )
        return response_code, output

    def _sending_file(self, ssh: object, src: str, dst: str):
        """Send file to the server

        Arguments:
            src {str} -- path to local file inside backend directory
            dst {str} -- path to the remote server with '/' at the end
        """
        sftp = ssh.open_sftp()
        filename = re.search(r"[A-Za-z0-9_-]+\.?[A-Za-z0-9]+$", src)[0]
        lfile = Path(self.workdir, src)
        rfile = dst + filename
        if lfile.exists():
            try:
                sftp.put(lfile, rfile)
            except Exception as e:
                sftp.close()
                self.log.exception("SFTP Error:", e)
                raise
        else:
            sftp.close()
            msg = "Source file not found"
            self.log.exception(msg)
            raise FileNotFoundError(msg)
        sftp.close()

    def _downloading_file(self, ssh: object, src: str):
        """Download file from the server

        Arguments:
            src {str} -- path to remote file inside server directory
            dst {str} -- path to the local server with '/' at the end
        """
        sftp = ssh.open_sftp()
        filename = re.search(r"[A-Za-z0-9_-]+\.?[A-Za-z0-9]+$", src)[0]
        rfile = src
        lfile = Path(self.workdir, filename)
        # todo: needed remote server check if remote file exist
        if rfile:
            try:
                sftp.get(rfile, lfile)
            except Exception as e:
                sftp.close()
                self.log.exception("SFTP Error:", e)
                raise
        else:
            sftp.close()
            msg = "Source file not found"
            self.log.exception(msg)
            raise FileNotFoundError(msg)
        sftp.close()

    def exec(self, cmd: str):
        """Execute SSH command on server

        Arguments:
            cmd {str} -- command to execute
        """
        return self._ssh_execute(self.session_srv, cmd)

    def ha_exec(self, cmd: str):
        """Execute SSH command on HA server

        Arguments:
            cmd {str} -- command to execute
        """
        if not self.is_proxy:
            self.log.debug("WARNING: No session_ha. HA always a target.")

        return self._ssh_execute(self.session_ha, cmd)

    def send_file(self, src: str, dst: str):
        """Send file to server

        Arguments:
            src {str} -- path to local file inside backend directory
            dst {str} -- path to the remote server with '/' at the end
        """
        return self._sending_file(self.session_srv, src, dst)

    def ha_send_file(self, src: str, dst: str):
        """Send file to HA server

        Arguments:
            src {str} -- path to local file inside backend directory
            dst {str} -- path to the remote server with '/' at the end
        """
        if not self.is_proxy:
            self.log.debug("WARNING: No session_ha. HA always a target.")

        return self._sending_file(self.session_ha, src, dst)

    def download_file(self, src: str):
        """Send file to server

        Arguments:
            src {str} -- path to local file inside backend directory
            dst {str} -- path to the remote server with '/' at the end
        """
        return self._downloading_file(self.session_srv, src)

    def ha_download_file(self, src: str):
        """Send file to HA server

        Arguments:
            src {str} -- path to local file inside backend directory
            dst {str} -- path to the remote server with '/' at the end
        """
        if not self.is_proxy:
            self.log.debug("WARNING: No session_ha. HA always a target.")

        return self._downloading_file(self.session_ha, src)

    def close(self):
        """Close SSH session"""
        if self.is_proxy:
            self.session_srv.close()
            self.session_ha.close()
        else:
            self.session_ha.close()
        self.log.info("SSH connections closed")
