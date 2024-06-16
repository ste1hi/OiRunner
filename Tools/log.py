# -*- coding: utf-8 -*-
import logging
import sys

def init_logging():
    _logger = logging.getLogger("OiRunner")
    loglevel = logging.DEBUG

    # Python 3.8 didn't support encoding argument.
    # See at https://docs.python.org/3/howto/logging.html#logging-to-a-file.
    if sys.version_info == (3, 8):
        logging.basicConfig(filename="OiRunner.log",
                            level=loglevel,
                            format="[%(asctime)s][%(levelname)s][%(name)s-%(filename)s-%(funcName)s-%(lineno)d]:%(message)s",
                            datefmt="%Y/%m/%d %H:%M:%S"
                            )
    else:
        logging.basicConfig(filename="OiRunner.log",
                            encoding="utf-8",
                            level=loglevel,
                            format="[%(asctime)s][%(levelname)s][%(name)s-%(filename)s-%(funcName)s-%(lineno)d]:%(message)s",
                            datefmt="%Y/%m/%d %H:%M:%S"
                            )
    
    return _logger

logger = init_logging()
