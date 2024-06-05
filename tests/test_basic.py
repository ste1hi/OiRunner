# -*- coding: utf-8 -*-
from contextlib import redirect_stdout
import io
import unittest
import os
import sys
from unittest import mock

from OiRunner import BetterRunner
from .util import GARBAGE, clean


class TestRunner(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        if os.getcwd().split(os.sep)[-1] != "data":
            os.chdir(os.path.join("tests", "data"))

    def setUp(self):
        self.runner = BetterRunner.BetterRunner()
        self.runner.args = mock.Mock(filename="", name="")

    def tearDown(self):
        clean(GARBAGE)

    def test_success_compile(self):
        self.runner.args.filename = "success"
        self.runner.args.name = "a.out"

        with io.StringIO() as buf, redirect_stdout(buf):
            self.runner.compile()
            output = buf.getvalue()
            self.assertEqual(output, "Compilation successful.\n")

    def test_fail_compile(self):
        self.runner.args.filename = "fail"
        self.runner.args.name = "a.out"

        with self.assertRaises(SystemExit):
            with io.StringIO() as buf, redirect_stdout(buf):
                def wait():
                    return -1

                new_mock = mock.Mock(wait=wait)
                new_mock.return_value = -1
                with mock.patch("subprocess.Popen", return_value=new_mock):
                    self.runner.compile()
                output = buf.getvalue()
                self.assertEqual(output, "Compilation failed.\n")


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
        self.assertTrue(self.runner.args.directgdb)

        self.assertEqual(self.runner.args.inputfile, "in")
        self.assertEqual(self.runner.args.outputfile, "out")
        self.assertEqual(self.runner.args.answerfile, "ans")

    def test_short_parser(self):
        sys.argv = ["BetterRunner.py", "test", "-if", "in", "-of", "out", "-j",
                    "-af", "ans", "-n", "run", "-p", "-g", "-d"]

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


class TestCheck(unittest.TestCase):

    def setUp(self):
        self.runner = BetterRunner.BetterRunner()
        if os.getcwd().split(os.sep)[-1] != "data":
            os.chdir(os.path.join("tests", "data"))

    def tearDown(self):
        clean(GARBAGE)

    def run_check(self, filename, if_print=False, if_pass=True):
        in_file = os.path.join("check_data", f"{filename}.in")
        out_file = os.path.join("check_data", f"{filename}.out")
        ans_file = os.path.join("check_data", f"{filename}.ans")
        with io.StringIO() as buf, redirect_stdout(buf):
            sys.argv = ["BetterRunner.py", "test"]
            self.runner.cmd_parse()
            self.runner.args.if_print = False
            if sys.platform == "win32":
                self.runner.args.name = os.path.join("..", "..", "tests", "data", "check.exe")
            else:
                self.runner.args.name = os.path.join("..", "..", "tests", "data", "check.out")

            if not if_print:
                passed = self.runner._check(out_file, in_file, ans_file, 1)
            else:
                passed = self.runner._check(out_file, in_file, ans_file, 1, if_print=if_print)

            if if_pass:
                self.assertTrue(passed)
            else:
                self.assertFalse(passed)
            output = buf.getvalue()
            return output

    def test_pass(self):
        output = self.run_check("1")
        self.assertEqual(output, "#1:\nCorrect answer.\n")

        output = self.run_check("1", True)
        self.assertIn("Correct answer, takes", output)  # We don't know the exact running time.

    def test_retval(self):
        output = self.run_check("3", if_pass=False)
        self.assertIn("#1:\nThe return value is 1. There may be issues with the program running.\n", output)

    def test_fail(self):
        output = self.run_check("2", if_pass=False)
        self.assertEqual(output, "#1:\nWrong answer.\n")

        output = self.run_check("2", True, False)
        self.assertEqual("#1:\nStandard answer:['wrong_answer']\nYour answer:['2']\n"
                         "Wrong answer.\nError data:\n2\n\n", output)

    def test_large(self):
        output = self.run_check("large", True, False)

        self.assertIn("The number of answer lines is too large.", output)
        self.assertIn("The number of data words is too large.", output)


class Testrun(unittest.TestCase):

    def setUp(self):
        self.runner = BetterRunner.BetterRunner()
        if os.getcwd().split(os.sep)[-1] != "data":
            os.chdir(os.path.join("tests", "data"))

    def tearDown(self):
        clean(GARBAGE)

    def test_directgdb(self):
        sys.argv = ["BetterRunner.py", "test", "--directgdb"]
        self.runner.cmd_parse()
        self.runner.args.directgdb = True

        with self.assertRaises(SystemExit):
            def wait():
                return 0

            new_mock = mock.Mock(wait=wait)
            new_mock.return_value = 0
            with mock.patch("subprocess.Popen", return_value=new_mock):
                self.runner.run()

    def test_not_judge(self):
        sys.argv = ["BetterRunner.py", "test"]
        self.runner.cmd_parse()
        self.runner.args.onlyinput = True
        self.runner.input_file = os.path.join("..", "..", "tests", "data", "check_data", "1.out")

        def wait():
            print("1")
            return 0

        new_mock = mock.Mock(wait=wait, returncode=0)
        new_mock.return_value = 0
        with mock.patch("subprocess.Popen", return_value=new_mock):
            with io.StringIO() as buf, redirect_stdout(buf):
                self.runner.run()
                output = buf.getvalue()
                self.assertEqual("The file has been executed.\n1\n", output)

        self.runner.args.onlyinput = False
        self.runner.args.onlyoutput = True
        self.runner.output_file = os.path.join("..", "..", "tests", "data", "check_data", "1.out")

        new_mock = mock.Mock(wait=wait, returncode=1)
        new_mock.return_value = 0
        with mock.patch("subprocess.Popen", return_value=new_mock):
            with io.StringIO() as buf, redirect_stdout(buf):
                self.runner.run()
                output = buf.getvalue()
                self.assertEqual("1\nThe return value is 1. There may be issues with the program running.\n", output)

        self.runner.args.onlyinput = False
        self.runner.args.onlyoutput = False

        new_mock = mock.Mock(wait=wait, returncode=1)
        new_mock.return_value = 0
        with mock.patch("subprocess.Popen", return_value=new_mock):
            with io.StringIO() as buf, redirect_stdout(buf):
                self.runner.run()
                output = buf.getvalue()
                self.assertEqual("1\nThe return value is 1. There may be issues with the program running.\n", output)

    def test_judge(self):
        sys.argv = ["BetterRunner.py", "test"]
        self.runner.cmd_parse()
        self.runner.args.judge = True
        os.mkdir("~tmp")

        def mock_new_dir(a, b):
            os.mkdir("~tmp")
        with mock.patch("OiRunner.BetterRunner.Functions._modify_file", return_value=3):
            with mock.patch("OiRunner.BetterRunner.Functions._output", side_effect=mock_new_dir):
                with mock.patch("OiRunner.BetterRunner.BetterRunner._check", return_value=True):
                    with io.StringIO() as buf, redirect_stdout(buf):
                        self.runner.run()
                        output = buf.getvalue()
                        self.assertEqual("#final:Accuracy 100.00%\n", output)
                        self.assertFalse(os.path.exists("~tmp"))

                with mock.patch("OiRunner.BetterRunner.BetterRunner._check", return_value=False):
                    with io.StringIO() as buf, redirect_stdout(buf):
                        self.runner.run()
                        output = buf.getvalue()
                        self.assertEqual("#final:Accuracy 0.00%\n", output)
                        self.assertFalse(os.path.exists("~tmp"))

    @mock.patch("subprocess.Popen")
    def test_gdb(self, mock_sp):
        sys.argv = ["BetterRunner.py", "test"]
        self.runner.cmd_parse()
        self.runner.args.judge = True
        self.runner.args.gdb = True
        self.runner.args.name = "test"

        def mock_new_dir(a, b):
            os.mkdir("~tmp")

        out = sys.stdout
        sys.stdout = None
        with mock.patch("OiRunner.BetterRunner.Functions._modify_file", return_value=3):
            with mock.patch("OiRunner.BetterRunner.Functions._output", side_effect=mock_new_dir):
                with mock.patch("OiRunner.BetterRunner.BetterRunner._check", return_value=False):
                    self.runner.run()
                    mock_sp.assert_called_once_with(["gdb", "test"])
        sys.stdout = out

    @mock.patch("OiRunner.BetterRunner.Functions.delete_freopen")
    @mock.patch("subprocess.Popen")
    def test_call_delete_freopen(self, mock_sp, mock_delete_freopen):
        sys.argv = ["BetterRunner.py", "test"]
        self.runner.cmd_parse()
        self.runner.args.judge = False
        self.runner.args.freopen = True

        with io.StringIO() as buf, redirect_stdout(buf):
            self.runner.run()

        def mock_new_dir(a, b):
            os.mkdir("~tmp")

        self.runner.args.judge = True
        with mock.patch("OiRunner.BetterRunner.Functions._modify_file", return_value=3):
            with mock.patch("OiRunner.BetterRunner.Functions._output", side_effect=mock_new_dir):
                with mock.patch("OiRunner.BetterRunner.BetterRunner._check", return_value=True):
                    with io.StringIO() as buf, redirect_stdout(buf):
                        self.runner.run()
        self.assertEqual(mock_delete_freopen.call_count, 2)
        mock_delete_freopen.assert_called_with("test.cpp")

    @mock.patch.dict(os.environ, {"__client_id": "test_client_id", "_uid": "test_uid"})
    @mock.patch("OiRunner.submit.Submit.upload_answer", return_value="test")
    @mock.patch("OiRunner.submit.Submit.get_record")
    @mock.patch("OiRunner.submit.Submit._get_csrf_token")
    @mock.patch("subprocess.Popen")
    def test_remote_judge(self, _, _get_token, get_record, upload):
        sys.argv = ["BetterRunner.py", "test"]
        self.runner.cmd_parse()
        self.runner.args.remote = "test"
        self.runner.args.judge = False

        with io.StringIO() as buf, redirect_stdout(buf):
            self.runner.run()

        def mock_new_dir(a, b):
            os.mkdir("~tmp")

        self.runner.args.judge = True
        with mock.patch("OiRunner.BetterRunner.Functions._modify_file", return_value=3):
            with mock.patch("OiRunner.BetterRunner.Functions._output", side_effect=mock_new_dir):
                with mock.patch("OiRunner.BetterRunner.BetterRunner._check", return_value=True):
                    with io.StringIO() as buf, redirect_stdout(buf):
                        self.runner.run()

        self.assertEqual(upload.call_count, 2)
        self.assertEqual(get_record.call_count, 2)
        upload.assert_called_with("test", "test.cpp", True, 11)
        get_record.assert_called_with("test", if_show_details=False)


class TestMisc(unittest.TestCase):

    @mock.patch("OiRunner.BetterRunner.BetterRunner.cmd_parse")
    @mock.patch("OiRunner.BetterRunner.BetterRunner.compile")
    @mock.patch("OiRunner.BetterRunner.BetterRunner.run")
    def test_main_call(self, mock_run, mock_compile, mock_parse):
        BetterRunner.main()
        mock_compile.assert_called_once()
        mock_parse.assert_called_once()
        mock_run.assert_called_once()
