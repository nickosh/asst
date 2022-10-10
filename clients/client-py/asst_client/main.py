# Automation Support Service Client [EXAMPLE]

# This realisation is only example how client can be builded.
# Here I tried to implement ClientWrapper which methods dynamically generated from ASST
# server's commands that allow to work with ASST server in easy and trancparent way.

# Copyright © 2022 Nikolay Shishov. All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from client import ClientWrapper
from logger import LoggerHandler

# Init of simple logger wrapper
log = LoggerHandler.new(__name__)
# Init of client wrapper. There some magic inside -this object will request
# avaliable commands from ASST server and dynamicly build a class which automatically
# handle client-server communication in proper format.
do = ClientWrapper(asst_ip="http://localhost:5000")

# To send command to ASST server and then receive answer first we need to init ssh connection.
# So, in this example, first we sent to ASST server our ssh connection params.
# Then we will send backend commands and will wait for the answers from ASST server.
try:
    # Test that command without ssh init do not broke up anything.
    do.show_uptime()  # will be error here - need ssh_init first

    # Here we send backend ssh server's params and ASST server keep it for our session.
    do.ssh_init({"ssh_ip": "server1", "ssh_user": "user", "ssh_pass": "password"})
    # Next, commands which ASST server can process (ASST server receive it from 'job' imports).
    # ASST server will connect to our backend server with params which we sent in ssh_init func,
    # will do what we want and will return answer. ClientWrapper will automatically wait for ASST answer.
    srv1_hostname = do.show_hostname()
    srv1_uptime = do.show_uptime()

    # For now, ASST server keeps only one backend ssh params for client's session.
    # If we will send new ssh params, old ones will be replaced with new ones.
    do.ssh_init({"ssh_ip": "server2", "ssh_user": "user", "ssh_pass": "password"})
    srv2_hostname = do.show_hostname()
    srv2_uptime = do.show_uptime()

    print(f"SERVER 1 INFO: {srv1_hostname[1]}, {srv1_uptime[1]}")
    print(f"SERVER 2 INFO: {srv2_hostname[1]}, {srv2_uptime[1]}")
except Exception as e:
    log.error(e)
    raise
finally:
    do.exit()

# do.client.serverlog is client's list which keeps all server's log messages.
# We can check or parse this log if we need to.
log.debug("--- Server full messages log ---")
for msg in do.client.serverlog:
    log.debug(msg)
