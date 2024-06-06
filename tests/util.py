# -*- coding: utf-8 -*-
import os

FILEOUT = "#1:\nfile1\n\n#2:\nfile2\n\n#3:\nfile3\n\n"
GARBAGE = ["a.out", "a.exe", "~temp", "~err_temp", "~out", ]
FREOPEN = 'freopen \n        ("in", "r"  , stdin),\n    freopen("out" , "w", stdout);'
HTML_WITHOUT_META_TAG = '<html><meta name="not_csrf" content></meta></html>'
HTML_WITHOUT_CONTENT = '<html><meta name="csrf-token" ></meta></html>'
HTML_CORRECT = '<html><meta name="csrf-token" content="test_csrf_token"></meta></html>'

WAITING_DATA = {"currentData": {
    "record": {
        "detail": {
            "judgeResult": {
                "finishedCaseCount": 1
            }
        }
    },
    "testCaseGroup": [
      [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
    ]
}}
RECORD_DATA_WITHOUT_SUBTASKS = {"currentData": {
    "record": {
        "detail": {
            "judgeResult": {
                "subtasks": [
                    {
                        "id": 0,
                        "score": 100,
                        "testCases": {
                            "0": {
                                "status": 12,
                                "score": 50,
                                "description": "ok accepted"
                            },
                            "1": {
                                "status": 12,
                                "score": 50,
                                "description": "ok accepted"
                            }
                        }
                    }
                ],
                "finishedCaseCount": 2
            }
        }
    },
    "testCaseGroup": [
      [0, 1]
    ]
}}
RECORD_DATA_WITH_SUBTASKS = {"currentData": {
    "record": {
        "detail": {
            "judgeResult": {
                "subtasks": {
                    "1": {
                        "id": 1,
                        "score": 50,
                        "testCases": [
                            {
                                "id": 0,
                                "status": 12,
                                "score": 50,
                                "description": "ok accepted"
                            }
                        ]
                    },
                    "2": {
                        "id": 2,
                        "score": 50,
                        "testCases": {
                            "1": {
                                "id": 1,
                                "status": 12,
                                "score": 50,
                                "description": "ok accepted"
                            }
                        }
                    }
                },
                "finishedCaseCount": 2
            }
        }
    },
    "testCaseGroup": {
        "1": [
            0
        ],
        "2": [
            1
        ]
    }
}}
DETAILS_OUTPUT = "\ndetails:\nCase:1\nscore:50\nstatus:AC\ndescription:"\
    "ok accepted\n\nCase:2\nscore:50\nstatus:AC\ndescription:ok accepted\n\nsummary:\n100\n\n"


def clean(filelist):
    for filename in filelist:
        if os.path.exists(filename):
            os.remove(filename)
