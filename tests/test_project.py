# -*- coding: utf-8 -*-
import io
import json
import os
import sys
import shutil
import unittest
from contextlib import redirect_stdout
from unittest import mock

from OiRunner import Exceptions, OiRunner
from OiRunner.util import HOOK_FILE_NAME
from .util import GARBAGE, clean

SET_DEFAULT = {
    "name": "test",
    "question_number": 1,
    "questions": {
        "1": {
            "id": 1,
            "name": "T1",
            "input_file": "in.txt",
            "output_file": "out.txt",
            "answer_file": "ans.txt"
        }
    }
}
SET_CHANGED = {
    "name": "test",
    "question_number": 1,
    "questions": {
        "1": {
            "id": 1,
            "name": "T1",
            "input_file": "T1.in",
            "output_file": "T1.out",
            "answer_file": "T1.ans",
            "cpp": "T1.cpp"
        }
    }
}


class TestProject(unittest.TestCase):

    def setUp(self):
        self.oirunner = OiRunner.OiRunner()
        if os.getcwd().split(os.sep)[-1] != "data":
            os.chdir(os.path.join("tests", "data"))
        self.work_path = os.getcwd()
        # Work directory is OiRunner/tests/data/test_setting/create.
        if not os.path.exists(os.path.join("test_setting", "create")):
            os.mkdir(os.path.join("test_setting", "create"))
        os.chdir(os.path.join("test_setting", "create"))

    def tearDown(self):
        os.chdir(self.work_path)
        os.chdir("test_setting")
        shutil.rmtree("create")
        os.mkdir("create")
        os.chdir("..")
        clean(GARBAGE)

    @mock.patch("argparse.ArgumentParser.print_help")
    @mock.patch("argparse.ArgumentParser.error")
    def test_parse(self, error, help):
        sys.argv = ["OiRunner.py"]  # Miss required arguments.

        self.oirunner.cmd_parse()
        error.assert_called_with("The subcommand is required.")
        help.assert_called_once()

    # It's a regression test. See details:https://github.com/ste1hi/OiRunner/issues/23
    def test_create_project_more_than_one_question(self):
        self.oirunner.make("test", 2, False, False)
        self.assertTrue(os.path.exists("T1"))
        self.assertTrue(os.path.exists("T2"))
        self.assertTrue(os.path.exists(".OiRunner"))

    def test_make(self):
        os.chdir("..")  # In test_setting, .OiRunner folder already exist.
        with self.assertRaises(Exceptions.ProjectAlreadyExists):
            self.oirunner.make("test", 1, False, False)
        os.chdir("create")

        self.oirunner.make("test", 1, False, False)
        settings_file = os.path.join(".OiRunner", "settings.json")
        self.assertTrue(os.path.exists(settings_file))

        self.assertTrue(os.path.exists(os.path.join(".OiRunner", "hooks")))

        os.chdir(os.path.join(".OiRunner", "hooks"))

        for file_name in HOOK_FILE_NAME:
            file_name += ".bak"
            self.assertTrue(os.path.exists(file_name))

        os.chdir(os.path.join("..", ".."))

        self.assertTrue(os.path.exists("T1"))
        self.assertTrue(os.path.exists(os.path.join("T1", "in.txt")))
        self.assertTrue(os.path.exists(os.path.join("T1", "out.txt")))
        self.assertTrue(os.path.exists(os.path.join("T1", "ans.txt")))
        self.assertFalse(os.path.exists(os.path.join("T1", "test.cpp")))

        with open(settings_file, "r") as f:
            settings = json.load(f)

        self.assertEqual(settings, SET_DEFAULT)

        # Reset the create folder.
        os.chdir("..")
        shutil.rmtree("create")
        os.mkdir("create")
        os.chdir("create")

        self.oirunner.make("test", 1, True, True)
        settings_file = os.path.join(".OiRunner", "settings.json")
        self.assertTrue(os.path.exists(settings_file))
        self.assertTrue(os.path.exists("T1"))
        self.assertTrue(os.path.exists(os.path.join("T1", "T1.in")))
        self.assertTrue(os.path.exists(os.path.join("T1", "T1.out")))
        self.assertTrue(os.path.exists(os.path.join("T1", "T1.ans")))
        self.assertTrue(os.path.exists(os.path.join("T1", "T1.cpp")))

        with open(settings_file, "r") as f:
            settings = json.load(f)

        self.assertEqual(settings, SET_CHANGED)

    def test_set_hook(self):
        with self.assertRaises(Exceptions.EnableHookError):
            self.oirunner.sethook(HOOK_FILE_NAME[0])
        self.oirunner._create_file(HOOK_FILE_NAME[0] + ".bak")
        self.oirunner.sethook(HOOK_FILE_NAME[0])
        self.assertFalse(os.path.exists(HOOK_FILE_NAME[0] + ".bak"))
        self.assertTrue(os.path.exists(HOOK_FILE_NAME[0]))

    @mock.patch("OiRunner.OiRunner.OiRunner.make")
    def test_run_make(self, make):
        sys.argv = ["OiRunner.py", "make", "test", "-q", "1"]
        self.oirunner.run()
        make.assert_called_with("test", 1, False, False)

    @mock.patch("OiRunner.OiRunner.OiRunner.sethook")
    def test_run_sethook(self, make):
        sys.argv = ["OiRunner.py", "sethook", HOOK_FILE_NAME[0]]
        self.oirunner.run()
        make.assert_called_with(HOOK_FILE_NAME[0])

    def test_run_fail(self):
        sys.argv = ["OiRunner.py", "make", "test", "-q", "1"]

        def side_effect(a, b, c, d):  # Mock make method effect when create project failed.
            raise Exceptions.ProjectAlreadyExists

        with mock.patch("OiRunner.OiRunner.OiRunner.make", side_effect=side_effect):
            with self.assertRaises(SystemExit) as exc:
                with io.StringIO() as buf, redirect_stdout(buf):
                    self.oirunner.run()
                    output = buf.getvalue()
                    self.assertEqual(output, "error:There is already a project in this directory.\n")
                    self.assertEqual(exc.exception.code, 31)

    def test_run_already_exists_files(self):
        sys.argv = ["OiRunner.py", "make", "test", "-q", "1"]

        def side_effect(a, b, c, d):  # Mock make method effect when create files failed.
            raise OSError

        with mock.patch("OiRunner.OiRunner.OiRunner.make", side_effect=side_effect):
            with self.assertRaises(SystemExit) as exc:
                with io.StringIO() as buf, redirect_stdout(buf):
                    self.oirunner.run()
                    output = buf.getvalue()
                    self.assertEqual(output, "error:This directory already have existed some files.\n")
                    self.assertEqual(exc.exception.code, 32)

    def test_run_enable_hook_error(self):
        sys.argv = ["OiRunner.py", "sethook", HOOK_FILE_NAME[0]]

        def side_effect(a):  # Mock make method effect when enable hook file failed.
            raise Exceptions.EnableHookError

        with mock.patch("OiRunner.OiRunner.OiRunner.sethook", side_effect=side_effect):
            with self.assertRaises(SystemExit) as exc:
                with io.StringIO() as buf, redirect_stdout(buf):
                    self.oirunner.run()
                    output = buf.getvalue()
                    self.assertEqual(output, "error:Hook file not exist.\n")
                    self.assertEqual(exc.exception.code, 33)
