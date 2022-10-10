# Copyright © 2022 Nikolay Shishov. All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger("paramiko").setLevel(logging.WARNING)


def singleton(cls, *args, **kw):
    instances = {}

    def _singleton(*args, **kw):
        if cls not in instances:
            instances[cls] = cls(*args, **kw)
        return instances[cls]

    return _singleton


@singleton
class LoggerHandler(object):
    def __init__(self, name: str = "mainlogger", level: str = "debug", sio=None):
        """Create new logger object.
        Args:
            name (str): name of logger.
            level (str): set lever for logger, can be "info", "warn", "error" or "debug".
            parent (str): set parent dearpygui window
        Raises:
            ValueError: if logger level is unknown.
        Returns:
            obj: return logger object.
        """
        self.pylog = logging.getLogger(name)
        if sio:
            self.servlog = sio
        if level == "info":
            self.pylog.setLevel(logging.INFO)
        elif level == "warn":
            self.pylog.setLevel(logging.WARNING)
        elif level == "error":
            self.pylog.setLevel(logging.ERROR)
        elif level == "debug":
            self.pylog.setLevel(logging.DEBUG)
        else:
            raise ValueError("Unknown logger level")

    def debug(self, message: str, sid: str = None):
        message = f"[{sid}] {message}" if sid else message
        self.pylog.debug(message)
        self.servlog.emit("server_log", f"[DEBUG] {message}")

    def info(self, message: str, sid: str = None):
        message = f"[{sid}] {message}" if sid else message
        self.pylog.info(message)
        self.servlog.emit("server_log", f"[INFO] {message}")

    def warning(self, message: str, sid: str = None):
        message = f"[{sid}] {message}" if sid else message
        self.pylog.warning(message)
        self.servlog.emit("server_log", f"[WARNING] {message}")

    def error(self, message: str, sid: str = None):
        message = f"[{sid}] {message}" if sid else message
        self.pylog.error(message)
        self.servlog.emit("server_log", f"[ERROR] {message}")

    def critical(self, message: str, sid: str = None):
        message = f"[{sid}] {message}" if sid else message
        self.pylog.critical(message)
        self.servlog.emit("server_log", f"[CRITICAL] {message}")
