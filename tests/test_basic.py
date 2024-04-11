import unittest
import os
import sys
import shutil
from unittest import mock
from OiRunner import BetterRunner

PY_FILE_PATH = "../../OiRunner/BetterRunner.py"
FILEOUT = "#1:\nfile1\n#2:\nfile2\n#3:\nfile3\n"
GARBAGE = ["a.out", "a.exe", "~temp", "~err_temp", "~out"]


def clean(filelist):
    for filename in filelist:
        if os.path.exists(filename):
            os.remove(filename)


class TestRunner(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        if os.getcwd().split(os.sep)[-1] != "data":
            os.chdir("tests/data")

    def setUp(self):
        self.runner = BetterRunner.BetterRunner()
        self.runner.args = mock.Mock(filename="", name="")

    def tearDown(self):
        clean(GARBAGE)

    def test_success_compile(self):
        self.runner.args.filename = "success"
        self.runner.args.name = "a.out"

        out = sys.stdout
        with open("~temp", "w") as f:
            sys.stdout = f
            self.runner.compile()
        sys.stdout = out

        with open("~temp", "r") as f:
            self.assertEqual(f.read(), "编译成功\n")
        os.remove("~temp")

    def test_fail_compile(self):
        self.runner.args.filename = "fail"
        self.runner.args.name = "a.out"

        out = sys.stdout
        with self.assertRaises(SystemExit):
            with open("~temp", "w") as f:
                sys.stdout = f

                def wait():
                    return -1

                new_mock = mock.Mock(wait=wait)
                new_mock.return_value = -1
                with mock.patch("subprocess.Popen", return_value=new_mock):
                    self.runner.compile()

        sys.stdout = out

        with open("~temp", "r") as f:
            self.assertEqual(f.read(), "编译失败\n")


class TestParser(unittest.TestCase):

    def setUp(self):
        self.runner = BetterRunner.BetterRunner()

    def tearDown(self):
        clean(GARBAGE)

    def short(self, pla):
        self.assertEqual(self.runner.args.filename, "test")

        if pla == "linux":
            self.assertEqual(self.runner.args.name, "./run.out")
        elif pla == "win32":
            self.assertEqual(self.runner.args.name, "run.exe")

        self.assertTrue(self.runner.args.judge)
        self.assertTrue(self.runner.args.print)
        self.assertTrue(self.runner.args.gdb)

        self.assertEqual(self.runner.args.inputfile, "in")
        self.assertEqual(self.runner.args.outputfile, "out")
        self.assertEqual(self.runner.args.answerfile, "ans")

    def test_short_parser(self):
        sys.argv = ["BetterRunner.py", "test", "-if", "in", "-of", "out", "-j",
                    "-af", "ans", "-n", "run", "-p", "-g"]

        sys.platform = "linux"
        self.runner.cmd_parse()
        self.short("linux")

        sys.platform = "win32"
        self.runner.cmd_parse()
        self.short("win32")

    def test_default(self):
        sys.argv = ["BetterRunner.py", "test"]

        def test(self, plt):
            self.assertFalse(self.runner.args.judge)
            self.assertFalse(self.runner.args.print)
            self.assertFalse(self.runner.args.gdb)
            self.assertFalse(self.runner.args.directgdb)
            self.assertFalse(self.runner.args.onlyinput)
            self.assertFalse(self.runner.args.onlyoutput)

            if plt == "linux":
                self.assertEqual(self.runner.args.name, "./a.out")
            elif plt == "win32":
                self.assertEqual(self.runner.args.name, "a.exe")

            self.assertEqual(self.runner.args.inputfile, "in.txt")
            self.assertEqual(self.runner.args.outputfile, "out.txt")
            self.assertEqual(self.runner.args.answerfile, "ans.txt")

        sys.platform = "linux"
        self.runner.cmd_parse()
        test(self, "linux")

        sys.platform = "win32"
        self.runner.cmd_parse()
        test(self, "win32")

    def test_long_parser(self):
        sys.argv = ["BetterRunner.py", "test", "--inputfile", "in", "--outputfile", "out",
                    "--answerfile", "ans", "--name", "run", "--judge", "--print", "--gdb",
                    "--directgdb", "--onlyinput", "--onlyoutput"]

        sys.platform = "linux"
        self.runner.cmd_parse()
        self.short("linux")

        sys.platform = "win32"
        self.runner.cmd_parse()
        self.short("win32")

        self.assertTrue(self.runner.args.directgdb)
        self.assertTrue(self.runner.args.onlyinput)
        self.assertTrue(self.runner.args.onlyoutput)


class TestFunction(unittest.TestCase):

    def setUp(self):
        self.func = BetterRunner.Functions()
        if os.getcwd().split(os.sep)[-1] != "data":
            os.chdir("tests/data")

    def tearDown(self):
        clean(GARBAGE)

    def test_modify_file(self):
        for i in range(1, 3):
            out = sys.stdout
            with self.assertRaises(SystemExit):
                with open("~temp", "w") as f:
                    sys.stdout = f
                    self.func._modify_file(f"empty{i}.in", "in")
            self.assertFalse(os.path.exists("~tmp"))
            with open("~temp", "r") as f:
                self.assertEqual(f.read(), f"error:empty{i}.in文件为空\n")
            sys.stdout = out

        ret_code = self.func._modify_file("a.in", "in")
        self.assertEqual(ret_code, 3)
        self.assertTrue(os.path.exists("~tmp"))
        for i in range(1, 4):
            self.assertTrue(os.path.exists(f"~tmp{os.sep}{i}.in"))
        for i in range(1, 4):
            with open(f"~tmp{os.sep}{i}.in", "r") as f:
                self.assertEqual(f.read(), f"file{i}\n")

    def test_output(self):
        for i in range(1, 4):
            os.rename(f"~tmp{os.sep}{i}.in", f"~tmp{os.sep}{i}.out")
        self.func._output(3, "~out")

        with open("~out", "r") as f:
            self.assertEqual(f.read(), FILEOUT)

        shutil.rmtree("~tmp")


class TestCheck(unittest.TestCase):

    def setUp(self):
        self.runner = BetterRunner.BetterRunner()
        if os.getcwd().split(os.sep)[-1] != "data":
            os.chdir("tests/data")

    def tearDown(self):
        clean(GARBAGE)

    # def test_pass(self):
    #     out = sys.stdout
    #     with open("~temp", "w") as f:
    #         sys.stdout = f
    #         self.runner._check("check_data/1.out", "check_data/1.in", "check_data/1.ans", 1, "check.cpp")

    #     sys.stdout = out
