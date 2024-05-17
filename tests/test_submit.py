# -*- coding: utf-8 -*-
import unittest
import os
import sys
import shutil
from OiRunner import BetterRunner
from .util import GARBAGE, clean


class TestSubmit(unittest.TestCase):

    def setUp(self):
        self.func = BetterRunner.Functions()
        if os.getcwd().split(os.sep)[-1] != "data":
            os.chdir(os.path.join("tests", "data"))

    def tearDown(self):
        clean(GARBAGE)

    