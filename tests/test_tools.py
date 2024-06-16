# -*- coding: utf-8 -*-
import unittest
import os
import unittest.mock

from OiRunner import tools
from .util import GARBAGE, clean


class TestTools(unittest.TestCase):

    def setUp(self):
        if os.getcwd().split(os.sep)[-1] != "data":
            os.chdir(os.path.join("tests", "data"))

    def tearDown(self):
        clean(GARBAGE)

    @unittest.mock.patch("logging.basicConfig")
    def test_encoding_argument_under_python38(self, mock_config):
        with unittest.mock.patch("sys.version_info", (3, 8)):
            tools.log.init_logging()
            format_string = "[%(asctime)s][%(levelname)s][%(name)s-%(filename)s-%(funcName)s-%(lineno)d]:%(message)s"
            mock_config.assert_called_with(filename="OiRunner.log",
                                           level=10,
                                           format=format_string,
                                           datefmt="%Y/%m/%d %H:%M:%S"
                                           )
        with unittest.mock.patch("sys.version_info", (3, 9)):
            tools.log.init_logging()
            format_string = "[%(asctime)s][%(levelname)s][%(name)s-%(filename)s-%(funcName)s-%(lineno)d]:%(message)s"
            mock_config.assert_called_with(filename="OiRunner.log",
                                           level=10,
                                           encoding="utf-8",
                                           format=format_string,
                                           datefmt="%Y/%m/%d %H:%M:%S"
                                           )
