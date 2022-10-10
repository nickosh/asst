# Copyright © 2022 Nikolay Shishov. All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)


class LoggerHandler:
    def new(name: str, level: str = "debug"):
        """Create new logger object.

        Args:
            name (str): name of logger.
            level (str): set lever for logger, can be "info", "warn", "error" or "debug".

        Raises:
            ValueError: if logger level is unknown.

        Returns:
            obj: return logger object.
        """
        logger = logging.getLogger(name)
        if level == "info":
            logger.setLevel(logging.INFO)
        elif level == "warn":
            logger.setLevel(logging.WARNING)
        elif level == "error":
            logger.setLevel(logging.ERROR)
        elif level == "debug":
            logger.setLevel(logging.DEBUG)
        else:
            raise ValueError("Unknown logger level")
        return logger
