# -*- coding: utf-8 -*-
from contextlib import redirect_stdout
import io
import unittest
import os
import unittest.mock
from OiRunner.submit import Submit
from .util import GARBAGE, HTML_CORRECT, HTML_WITHOUT_META_TAG, HTML_WITHOUT_CONTENT, \
                  WAITING_DATA, RECORD_DATA_WITHOUT_SUBTASKS, \
                  RECORD_DATA_WITH_SUBTASKS, DETAILS_OUTPUT, clean


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
            with io.StringIO() as buf, redirect_stdout(buf):
                Submit()
                output = buf.getvalue()
                self.assertEqual(output, "Missing the required environment variable.('__client_id' or '_uid')\n")
                self.assertEqual(exit_code.exception.code, 12)

    @unittest.mock.patch.dict(os.environ, {"__client_id": "test_client_id", "_uid": "test_uid"})
    @unittest.mock.patch('requests.Session.get')
    def test_get_csrf_token(self, mock_get):
        mock_response = unittest.mock.Mock()
        mock_response.text = HTML_CORRECT
        mock_get.return_value = mock_response
        submit = Submit()
        self.assertEqual(submit._csrf_token, "test_csrf_token")
        mock_get.assert_called_once()

    @unittest.mock.patch.dict(os.environ, {"__client_id": "test_client_id", "_uid": "test_uid"})
    @unittest.mock.patch('requests.Session.get')
    def test_get_csrf_toke_failed(self, mock_get):
        wrong_response = [HTML_WITHOUT_META_TAG, HTML_WITHOUT_CONTENT]
        wrong_output = [
            "The server returned anomalous data (which does not contain meta tag).\n",
            "The server returned anomalous data (which does not contain 'content' in meta tag).\n"
            ]
        wrong_code = [21, 22]
        for times in range(2):
            mock_response = unittest.mock.Mock()
            mock_response.text = wrong_response[times]
            mock_get.return_value = mock_response
            with self.assertRaises(SystemExit) as sys_exit:
                with io.StringIO() as buf, redirect_stdout(buf):
                    Submit()
                    output = buf.getvalue()
                    self.assertEqual(output, wrong_output[times])
                    self.assertEqual(sys_exit.exception.code, wrong_code[times])

    @unittest.mock.patch.dict(os.environ, {"__client_id": "test_client_id", "_uid": "test_uid"})
    @unittest.mock.patch('OiRunner.submit.Submit._get_csrf_token', return_value="test")
    @unittest.mock.patch('requests.Session.post')
    def test_upload(self, mock_post, _):
        submit = Submit()
        with open("success.cpp", "r") as f:
            code = f.read()
        test_data = {
            "enableO2": True,
            "lang": 11,
            "code": code
        }
        url = "https://www.luogu.com.cn/fe/api/problem/submit/test"
        mock_response = unittest.mock.Mock()
        mock_response.json.return_value = {"rid": 123456}
        mock_post.return_value = mock_response
        submit.upload_answer("test", "success.cpp")
        mock_post.assert_called_with(url=url, json=test_data)

    @unittest.mock.patch.dict(os.environ, {"__client_id": "test_client_id", "_uid": "test_uid"})
    @unittest.mock.patch('OiRunner.submit.Submit._get_csrf_token', return_value="test")
    @unittest.mock.patch('requests.Session.post')
    def test_upload_fail(self, mock_post, _):
        submit = Submit()
        mock_response = unittest.mock.Mock()
        mock_response.json.return_value = {"fail": 123456}
        mock_post.return_value = mock_response
        with io.StringIO() as buf, redirect_stdout(buf):
            with self.assertRaises(SystemExit) as sys_exit:
                submit.upload_answer("test", "success.cpp")

        self.assertEqual(sys_exit.exception.code, 24)

    @unittest.mock.patch.dict(os.environ, {"__client_id": "test_client_id", "_uid": "test_uid"})
    @unittest.mock.patch('OiRunner.submit.Submit._get_csrf_token', return_value="test")
    @unittest.mock.patch('requests.Session.get')
    def test_get_record_retry_count(self, mock_get, _):
        submit = Submit()
        mock_get.return_value.json.return_value = WAITING_DATA
        submit.get_record("test", 0.1, 2)
        self.assertEqual(mock_get.call_count, 2)

    @unittest.mock.patch.dict(os.environ, {"__client_id": "test_client_id", "_uid": "test_uid"})
    @unittest.mock.patch('OiRunner.submit.Submit._get_csrf_token', return_value="test")
    @unittest.mock.patch('requests.Session.get')
    def test_get_record_without_subtasks(self, mock_get, _):
        submit = Submit()
        mock_get.return_value.json.return_value = RECORD_DATA_WITHOUT_SUBTASKS
        with io.StringIO() as buf, redirect_stdout(buf):
            submit.get_record("test")
            output = buf.getvalue()
            self.assertEqual(output, "summary:\n100\nAC|AC\n")

        with io.StringIO() as buf, redirect_stdout(buf):
            submit.get_record("test", if_show_details=True)
            output = buf.getvalue()
            self.assertEqual(output, DETAILS_OUTPUT)

    @unittest.mock.patch.dict(os.environ, {"__client_id": "test_client_id", "_uid": "test_uid"})
    @unittest.mock.patch('OiRunner.submit.Submit._get_csrf_token', return_value="test")
    @unittest.mock.patch('requests.Session.get')
    def test_get_record_with_subtasks(self, mock_get, _):
        submit = Submit()
        mock_get.return_value.json.return_value = RECORD_DATA_WITH_SUBTASKS
        with io.StringIO() as buf, redirect_stdout(buf):
            submit.get_record("test")
            output = buf.getvalue()
            self.assertEqual(output, "summary:\n100\nAC|AC\n")

        with io.StringIO() as buf, redirect_stdout(buf):
            submit.get_record("test", if_show_details=True)
            output = buf.getvalue()
            self.assertEqual(output, DETAILS_OUTPUT)
