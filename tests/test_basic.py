import unittest
import os
import sys
from unittest import mock
from OiRunner import BetterRunner

PY_FILE_PATH = '../../OiRunner/BetterRunner.py'


class TestRunner(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        os.chdir("tests/data")

    def setUp(self):
        self.runner = BetterRunner.BetterRunner()
        self.runner.args = mock.Mock(filename='', name='')

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

    def test_success_compile(self):
        self.runner.args.filename = 'success'
        self.runner.args.name = 'a.out'

        out = sys.stdout
        with open("~temp", "w") as f:
            sys.stdout = f
            self.runner.compile()
        sys.stdout = out

        with open("~temp", "r") as f:
            self.assertEqual(f.read(), "编译成功\n")
        os.remove("~temp")

    def test_fail_compile(self):
        self.runner.args.filename = 'fail'
        self.runner.args.name = 'a.out'

        out = sys.stdout
        with self.assertRaises(SystemExit):
            with open("~temp", "w") as f:
                sys.stdout = f

                def wait():
                    return -1

                new_mock = mock.Mock(wait=wait)
                new_mock.return_value = -1
                with mock.patch('subprocess.Popen', return_value=new_mock):
                    self.runner.compile()

        sys.stdout = out

        with open("~temp", "r") as f:
            self.assertEqual(f.read(), "编译失败\n")

    @mock.patch('builtins.KeyboardInterrupt')
    def test_exit_manully(self, interrupt):
        self.runner.args.filename = 'success'
        self.runner.args.name = 'a.out'

        out = sys.stdout
        with self.assertRaises(SystemExit):
            with open("~temp", "w") as f:
                sys.stdout = f
                with interrupt:
                    self.runner.compile()

        sys.stdout = out
        with open("~temp", "r") as f:
            self.assertEqual(f.read(), "\n手动退出，祝AC~(^v^)\n")