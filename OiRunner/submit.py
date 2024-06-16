# -*- coding: utf-8 -*-
import os
import re
import sys
import time
from typing import Dict, MutableMapping, Union

import requests

from Tools import log
from .util import ACCEPT, BAD_URL, CONTENT_PAT, CONTENT_TYPE, CONTENT_VALUE_PAT, MATE_TAG_PAT
from .util import PARAMS, QUESTION_URL, RECORD_URL, STATUS_CODE, SUBMIT_URL, USER_AGENT


class Submit:
    def __init__(self) -> None:
        '''
        Initialization Submit class.

        Raise:
            SystemExit -- Missing the required environment variable.

            Exitcode `12` means missing the required environment variable.
        '''
        client_id = os.getenv("__client_id")
        uid = os.getenv("_uid")
        log.logger.debug("Get environment variable.")

        if client_id is None or uid is None:
            print("Missing the required environment variable.('__client_id' or '_uid')")
            log.logger.critical("Missing the required environment variable.('__client_id' or '_uid')")
            sys.exit(12)

        self._cookies = {
            '__client_id': client_id,
            '_uid': uid
            }
        log.logger.debug(f"Set cookies {self._cookies}.")
        self.session = requests.Session()
        self.headers: MutableMapping[str, Union[str, bytes]] = {"User-Agent": USER_AGENT}
        log.logger.debug("Get csrf token.")
        self._csrf_token = self._get_csrf_token()
        self.headers["Accept"] = ACCEPT
        self.headers["content-type"] = CONTENT_TYPE
        log.logger.debug(f"Set headers {self.headers}.")

    def _get_csrf_token(self) -> str:
        '''
        Get csrf-token from `luogu`.

        Return:
            token -- Csrf-token.

            SystemExit -- Something was wrong during web connection.

            - Exitcode `21` means the server returned data doesn't contain meta tag.
            - Exitcode `22` means there is no content in meta tag.
            - Exitcode `23` means there is no value in content attribute.

        '''
        self.session.headers = self.headers
        self.session.cookies.update(self._cookies)
        html_content = self.session.get(BAD_URL).text
        log.logger.debug(f"Request {BAD_URL} to get csrf-token.")
        log.logger.debug(f"It returned {html_content}.")

        # Get csrf-token meta tag in html file.
        meta_tag_pat = re.compile(MATE_TAG_PAT)
        meta_tag = re.search(meta_tag_pat, html_content)

        if meta_tag is None:
            print("The server returned anomalous data (which does not contain meta tag).")
            log.logger.critical("The server returned anomalous data (which does not contain meta tag).")
            sys.exit(21)

        # Get content attribute in meta tag.
        meta = meta_tag.group()
        log.logger.debug(f"Meta tag is {meta}")
        content_pat = re.compile(CONTENT_PAT)
        content_result = re.search(content_pat, meta)
        if content_result is None:
            print("The server returned anomalous data (which does not contain 'content' in meta tag).")
            log.logger.critical("The server returned anomalous data (which does not contain 'content' in meta tag).")
            sys.exit(22)
        content = content_result.group()
        log.logger.debug(f"The content of meta tag is {content}")

        # Get the value of content attribute.
        content_value_pat = re.compile(CONTENT_VALUE_PAT)
        content_value_result = re.search(content_value_pat, content)
        # It must include a quote mark.
        if content_value_result is None:  # pragma: no cover
            print("The server returned anomalous data (which does not contain anything in the content attribute of meta tag).")
            log.logger.critical("The server returned anomalous data "
                                "(which does not contain anything in the content attribute of meta tag).")
            sys.exit(23)
        content_value = content_value_result.group()
        log.logger.debug(f"Content value is {content_value}")

        token = content_value.strip('"')  # Remove quotes before and after strings

        return token

    def upload_answer(self, question: str, file_path: str,
                      enableO2: bool = True, lang: int = 11) -> str:
        '''
        Upload answer to `luogu`.

        Args:
            question -- The question id in `luogu`.

            file_path -- The program file which is to be uploaded.

            enableO2 -- Whether to use `O2` flag during compiling.

            lang -- The programming language which is included in the program file.

        Return:
            rid -- The `rid` of its record.

        Raise:
            SystemExit -- An error occurred while uploading the answer.

            Exitcode `24` means an error occurred while uploading the answer.
        '''
        question_url = QUESTION_URL + question
        self.headers["x-csrf-token"] = self._csrf_token
        self.headers["referer"] = question_url
        url = SUBMIT_URL + question
        log.logger.debug(f"Request url is {url}.")
        log.logger.debug(f"Request headers are {self.headers}.")

        with open(file_path, "r") as code_file:
            code = code_file.read()

        data = {
            "enableO2": enableO2,
            "lang": lang,
            "code": code
        }
        log.logger.info("Request api.")
        response = self.session.post(url=url, json=data)

        try:
            return str(response.json()["rid"])
        except KeyError:
            print(f"An error occurred while uploading the answer, with the server returning: \n {response.text}")
            log.logger.critical(f"An error occurred while uploading the answer, with the server returning: \n {response.text}")
            sys.exit(24)

    def get_record(self, rid: str, retry_interval: float = 1,
                   retry_count: int = -1, if_show_details: bool = False) -> None:
        '''
        Get the judge result from the `rid`.

        Args:
            rid -- The record id.

            retry_interval -- The delay time between two request. The unit is second.

            retry_count -- Maximum number of retries.

            if_show_details -- Whether to show the details of record.
        '''
        record_url = RECORD_URL + rid
        log.logger.debug(f"Record url is {record_url}.")
        self.headers.pop("referer", None)
        self.headers.pop("content-type", None)

        counter = 0
        while True:
            counter += 1
            log.logger.debug(f"Retry count {counter}.")
            time.sleep(retry_interval)
            if retry_count != -1 and counter > retry_count:
                return None

            record = self.session.get(url=record_url, params=PARAMS)
            log.logger.debug(f"Record is {record}.")
            data = record.json()["currentData"]
            judge_result: Dict[str, dict] = data["record"]["detail"]["judgeResult"]
            test_case_groups: dict = data["testCaseGroup"]
            case_counter = 0
            finished_test = judge_result["finishedCaseCount"]

            for test_case_group in test_case_groups:
                case_counter += len(test_case_group)

            if case_counter == finished_test:
                log.logger.debug("All tests are finished.")
                break
            log.logger.debug(f"The number of tests is {case_counter}, already have finished {finished_test}.")

        total_score = 0
        if type(judge_result["subtasks"]) is list:
            subtasks: Union[list, dict] = judge_result["subtasks"]
        else:
            subtasks = list(judge_result["subtasks"].values())
        for subtask in subtasks:
            total_score += subtask["score"]
        log.logger.debug(f"Subtasks are {subtasks}.")

        if if_show_details:
            print("\ndetails:")
        summary = ""
        for subtask in subtasks:
            testcases = subtask["testCases"]
            subtask_id = subtask["id"]
            if type(test_case_groups) is list:
                subtask_cases_id = test_case_groups[subtask_id]
            else:
                subtask_cases_id = test_case_groups[str(subtask_id)]

            if subtask_id == 1:  # If the id of subtask is 1, the testcases in this subtask are in a list.
                for i in range(len(subtask_cases_id)):
                    score = testcases[i]["score"]
                    description = testcases[i]["description"]
                    status = testcases[i]["status"]
                    if if_show_details:
                        print(f"Case:{i+1}\nscore:{score}\nstatus:{STATUS_CODE[status]}\ndescription:{description}\n")
                    else:
                        summary += f"{STATUS_CODE[status]}|"
            else:
                for i in subtask_cases_id:
                    score = testcases[str(i)]["score"]
                    description = testcases[str(i)]["description"]
                    status = testcases[str(i)]["status"]
                    if if_show_details:
                        print(f"Case:{i+1}\nscore:{score}\nstatus:{STATUS_CODE[status]}\ndescription:{description}\n")
                    else:
                        summary += f"{STATUS_CODE[status]}|"
        summary = summary[:-1]
        print("summary:")
        print(total_score)
        print(summary)
