# -*- coding: utf-8 -*-
import logging

def init_logging():
    _logger = logging.getLogger("OiRunner")
    loglevel = logging.DEBUG

    logging.basicConfig(filename="OiRunner.log",
                        encoding="utf-8",
                        level=loglevel,
                        format="[%(asctime)s][%(levelname)s][%(name)s-%(filename)s-%(funcName)s-%(lineno)d]:%(message)s",
                        datefmt="%Y/%m/%d %H:%M:%S"
                        )
    
    return _logger

logger = init_logging()
