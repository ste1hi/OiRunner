# -*- coding: utf-8 -*-
import json
import os
import sys
import shutil
import unittest
from unittest import mock

from OiRunner import Exceptions, OiRunner
from .util import GARBAGE, clean

SET_DEFAULT = {
    "name": "test",
    "input_file": "in.txt",
    "output_file": "out.txt",
    "answer_file": "ans.txt"
}
SET_CHANGED = {
    "name": "test",
    "input_file": "test.in",
    "output_file": "test.out",
    "answer_file": "test.ans"
}


class TestProject(unittest.TestCase):

    def setUp(self):
        self.oirunner = OiRunner.OiRunner()
        if os.getcwd().split(os.sep)[-1] != "data":
            os.chdir(os.path.join("tests", "data"))
        os.chdir(os.path.join("test_setting", "create"))

    def tearDown(self):
        os.chdir("..")
        shutil.rmtree("create")
        os.mkdir("create")
        os.chdir("create")
        os.chdir(os.path.join("..", ".."))
        clean(GARBAGE)

    @mock.patch("argparse.ArgumentParser.print_help")
    @mock.patch("argparse.ArgumentParser.error")
    def test_parse(self, error, help):
        sys.argv = ["OiRunner.py"]

        self.oirunner.cmd_parse()
        error.assert_called_with("The subcommand is required.")
        help.assert_called_once()

    def test_make(self):
        os.chdir("..")
        with self.assertRaises(Exceptions.ProjectAlreadyExists):
            self.oirunner.make("test", False, False)
        os.chdir("create")

        self.oirunner.make("test", False, False)
        settings_file = os.path.join(".OiRunner", "settings.json")
        self.assertTrue(os.path.exists(settings_file))
        self.assertTrue(os.path.exists("in.txt"))
        self.assertTrue(os.path.exists("out.txt"))
        self.assertTrue(os.path.exists("ans.txt"))
        self.assertFalse(os.path.exists("test.cpp"))

        with open(settings_file, "r") as f:
            settings = json.load(f)

        for key in SET_DEFAULT.keys():
            self.assertEqual(settings[key], SET_DEFAULT[key])

        os.chdir("..")
        shutil.rmtree("create")
        os.mkdir("create")
        os.chdir("create")

        self.oirunner.make("test", True, True)
        settings_file = os.path.join(".OiRunner", "settings.json")
        self.assertTrue(os.path.exists(settings_file))
        self.assertTrue(os.path.exists("test.in"))
        self.assertTrue(os.path.exists("test.out"))
        self.assertTrue(os.path.exists("test.ans"))
        self.assertTrue(os.path.exists("test.cpp"))

        with open(settings_file, "r") as f:
            settings = json.load(f)

        for key in SET_CHANGED.keys():
            self.assertEqual(settings[key], SET_CHANGED[key])

    @mock.patch("OiRunner.OiRunner.OiRunner.make")
    def test_run_correct(self, make):
        sys.argv = ["OiRunner.py", "make", "test"]
        self.oirunner.run()
        make.assert_called_with("test", False, False)

    def test_run_fail(self):
        sys.argv = ["OiRunner.py", "make", "test"]

        def side_effect(a, b, c):
            raise Exceptions.ProjectAlreadyExists

        with mock.patch("OiRunner.OiRunner.OiRunner.make", side_effect=side_effect):
            with self.assertRaises(SystemExit):
                out = sys.stdout
                with open("~temp", "w") as f:
                    sys.stdout = f
                    self.oirunner.run()
            with open("~temp", "r") as f:
                self.assertMultiLineEqual("error:There is already a project in this directory.\n", f.read())
            sys.stdout = out
