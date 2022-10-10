# Copyright © 2022 Nikolay Shishov. All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

from main import log


def show_uptime(conn, args):
    log.debug("I'm query server's uptime for you.")
    return conn.exec("uptime")


def show_hostname(conn, args):
    log.debug("I'm query server's hostname for you.")
    return conn.exec("hostname")
