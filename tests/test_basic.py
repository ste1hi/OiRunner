import unittest
import os
import sys
import subprocess
from unittest import mock
from OiRunner import BetterRunner

PY_FILE_PATH = '../../OiRunner/BetterRunner.py'


class TestRunner(unittest.TestCase):

    def setUp(self):
        os.chdir("tests/data")

    def clean(self, filename, filetype=None):
        if filetype == "executable":
            if sys.platform == "linux":
                if os.path.exists(filename + ".out"):
                    os.remove(filename + ".out")
            elif sys.platform == "win32":
                if os.path.exists(filename + ".exe"):
                    os.remove(filename + ".exe")
        else:
            if os.path.exists(filename):
                os.remove(filename)

    def tearDown(self):
        self.clean("a", "executable")
        self.clean("~temp")
        self.clean("~err_temp")

    def test_compile(self):
        runner = BetterRunner.BetterRunner()
        runner.args = mock.Mock(filename='', name='')
        runner.args.filename = 'success'
        runner.args.name = 'a.out'

        out = sys.stdout
        with open("~temp", "w") as f:
            sys.stdout = f
            runner.compile()
        sys.stdout = out

        with open("~temp", "r") as f:
            self.assertEqual(f.read(), "编译成功\n")
        os.remove("~temp")

        runner.args.filename = 'fail'
        runner.args.name = 'a.out'

        out = sys.stdout
        with self.assertRaises(SystemExit):
            with open("~temp", "w") as f:
                sys.stdout = f

                def wait():
                    return -1

                subprocess.Popen = mock.Mock()
                subprocess.Popen.return_value = mock.Mock(wait=wait)
                runner.compile()
        sys.stdout = out

        with open("~temp", "r") as f:
            self.assertEqual(f.read(), "编译失败\n")
