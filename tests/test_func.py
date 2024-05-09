# -*- coding: utf-8 -*-
import unittest
import os
import sys
import shutil
from OiRunner import BetterRunner
from .util import GARBAGE, FILEOUT, FREOPEN, clean


class TestFunction(unittest.TestCase):

    def setUp(self):
        self.func = BetterRunner.Functions()
        if os.getcwd().split(os.sep)[-1] != "data":
            os.chdir(os.path.join("tests", "data"))

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
                self.assertEqual(f.read(), f"error:empty{i}.in is empty.\n")
            sys.stdout = out

        ret_code = self.func._modify_file("a.in", "in")
        self.assertEqual(ret_code, 3)
        self.assertTrue(os.path.exists("~tmp"))

        for i in range(1, 4):
            file_path = os.path.join("~tmp", f"{i}.in")
            self.assertEqual(file_path, f"~tmp{os.sep}{i}.in")

            self.assertTrue(os.path.exists(file_path))

        for i in range(1, 4):
            file_path = os.path.join("~tmp", f"{i}.in")
            with open(file_path, "r") as f:
                self.assertEqual(f.read(), f"file{i}\n")

    def test_output(self):
        for i in range(1, 4):
            in_file = os.path.join("~tmp", f"{i}.in")
            out_file = os.path.join("~tmp", f"{i}.out")

            os.rename(in_file, out_file)
        self.func._output(3, "~out")

        with open("~out", "r") as f:
            self.assertEqual(f.read(), FILEOUT)

        shutil.rmtree("~tmp")

    def test_delete_freopen(self):
        origin_path = os.path.join("test_freopen", "test_freopen.cpp.bak")
        file_path = os.path.join("test_freopen", "test.cpp")
        back_path = os.path.join("test_freopen", "test.cpp.bak")
        shutil.copy2(origin_path, file_path)
        with open(file_path, "r") as f:
            self.assertIn(FREOPEN, f.read())

        self.func.delete_freopen(file_path)

        self.assertTrue(os.path.exists(back_path))
        with open(file_path, "r") as f:
            self.assertNotIn(FREOPEN, f.read())
        with open(back_path, "r") as f:
            self.assertIn(FREOPEN, f.read())

        with self.assertRaises(ValueError):
            self.func.delete_freopen("Not exists.")

        clean([file_path, back_path])
