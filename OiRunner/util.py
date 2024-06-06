# -*- coding: utf-8 -*-
BAD_URL = r"https://www.luogu.com.cn/404"
SUBMIT_URL = r"https://www.luogu.com.cn/fe/api/problem/submit/"
QUESTION_URL = r"https://www.luogu.com.cn/problem/"
RECORD_URL = r"https://www.luogu.com.cn/record/"


USER_AGENT = ("Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit"
              "/537.36 (KHTML, like Gecko) Chrome/94.0.4606.54 Safari/537.36")

MATE_TAG_PAT = r'<meta name="csrf-token" (([\s\S])*?)>'
CONTENT_PAT = r'content="(([\s\S])*?)"'
CONTENT_VALUE_PAT = r'"(([\s\S])*?)"'

ACCEPT = "application/json, text/plain, */*"
CONTENT_TYPE = "application/json"
PARAMS = {'_contentOnly': '1'}

STATUS_CODE = {
    12: "AC",
    5: "TLE",
    7: "RE",
    6: "WA"
    }
