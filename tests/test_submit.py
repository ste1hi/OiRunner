# -*- coding: utf-8 -*-
import unittest
import os
import sys
from OiRunner.submit import Submit
from .util import GARBAGE, clean


class TestSubmit(unittest.TestCase):

    def setUp(self):
        if os.getcwd().split(os.sep)[-1] != "data":
            os.chdir(os.path.join("tests", "data"))

    def tearDown(self):
        clean(GARBAGE)

    @unittest.mock.patch.dict(os.environ, {"__client_id": "test_client_id", "_uid": "test_uid"})
    @unittest.mock.patch("OiRunner.submit.Submit._get_csrf_token", return_value="MockCsrfToken")
    def test_init(self, mock_get_csrf_token):
        submit = Submit()

        mock_get_csrf_token.assert_called_once()
        self.assertEqual(submit._cookies["__client_id"], "test_client_id")
        self.assertEqual(submit._cookies["_uid"], "test_uid")
        self.assertEqual(submit._csrf_token, "MockCsrfToken")

    @unittest.mock.patch.dict(os.environ, {}, clear=True)
    def test_init_without_env(self):
        with self.assertRaises(SystemExit) as exit_code:
            out = sys.stdout
            with open("~temp", "w") as f:
                sys.stdout = f
                Submit()

        with open("~temp", "r") as f:
            self.assertEqual(f.read(), "Missing the required environment variable.('__client_id' or '_uid')\n")
        self.assertEqual(exit_code.exception.code, 12)

        sys.stdout = out
