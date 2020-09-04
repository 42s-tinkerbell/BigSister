import socket
import requests as req
import json
from time import sleep
import os

ENDPOINT = 'https://api.intra.42.fr'

SEOUL = '29'
C_PISCINE = '9'
piscine_project = {
	'shell-00' : 1255,
	'shell-01' : 1256,
	'c-00' : 1257,
	'c-01' : 1258,
	'c-02' : 1259,
    'c-03' : 1260,
    'c-04' : 1261,
    'c-05' : 1262,
    'c-06' : 1263,
    'c-07' : 1270,
    'c-08' : 1264,
    'c-09' : 1265,
    'c-10' : 1266,
    'c-11' : 1267,
    'c-12' : 1268,
    'c-13' : 1271,
    'exam-00' : 1301,
    'exam-01' : 1302,
    'exam-02' : 1303,
    'exam-final' : 1304,
    'rush-00' : 1308,
    'rush-01' : 1310,
    'rush-02' : 1309,
    'bsq' : 1305
}

u = os.environ["UID42"]
s = os.environ["SECRET42"]


class HttpRequest(object):

    def __init__(self, target: str, session, **kwargs):
        self.url = f"{ENDPOINT}{target}"
        self.session = session
        if "filter" in kwargs:
            self.filter = kwargs["filter"]
        else:
            self.filter = {}
        if "page" in kwargs:
            self.page = kwargs["page"]
        else:
            self.page = {"size": 100, "number": 1}  # MAX size
        if "sort" in kwargs:
            self.sort = kwargs["sort"]
        else:
            self.sort = ""
        if "range" in kwargs:
            self.range = kwargs["range"]
        else:
            self.range = ""
        # Needs to handle kwargs into different parameters

    def parse_params(self):
        if self.filter:
            filtering = '&'.join([f"filter[{key}]={value}" for key, value in self.filter.items()]) + '&'
        else:
            filtering = ""
        page = '&'.join([f"page[{key}]={value}" for key, value in self.page.items()])
        parsed_param = filtering + page
        if self.sort:
            parsed_param += f"&sort={self.sort}"
        if self.range:
            ranges = '&'.join([f"range[{key}]={value}" for key, value in self.range.items()])
        else:
            ranges = ""
        if self.range:
            parsed_param = parsed_param + '&' + ranges
        return f"?{parsed_param}"

    def get(self):
        print(self.url + self.parse_params())
        resp = self.session.get(self.url + self.parse_params())
        try:
            resp.raise_for_status()
        except req.exceptions.HTTPError as e:
            print(resp.content)
        return resp.json()

    def put(self, data: json):
        resp = self.session.put(self.url, json=data)
        try:
            resp.raise_for_status()
        except req.exceptions.HTTPError as e:
            print(resp.content)
        return resp

    def post(self, data: json):
        resp = self.session.post(self.url, json=data)
        try:
            resp.raise_for_status()
        except req.exceptions.HTTPError as e:
            print(resp.content)
        return resp

    def patch(self, data: json):
        resp = self.session.patch(self.url, json=data)
        try:
            resp.raise_for_status()
        except req.exceptions.HTTPError as e:
            print(resp.content)
        return resp

    def delete(self):
        resp = self.session.delete(self.url)
        resp.raise_for_status()
        return resp


class Api(object):

    def __init__(self, uid: str, secret: str, req_code: str = None,
                 redirect: str = None, token: str = None):
        self.uid = uid
        self.secret = secret
        self.req_code = req_code
        self.__token = token
        self.redirect = redirect
        if self.__token is None:
            self.__token = self.Authenticate()
        self.session = req.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.__token}"})

    def Authenticate(self):
        if self.req_code:
            # 3 legged authentication
            auth_data = {
                "grant_type": "authorization_code",
                "client_id": self.uid,
                "client_secret": self.secret,
                "code": self.req_code,
                "redirect_uri": self.redirect
            }
        else:
            # 2 legged authentication
            auth_data = {
                "grant_type": "client_credentials",
                "client_id": self.uid,
		"scope": "public profile projects tig",
                "client_secret": self.secret
            }

        resp = req.post("https://api.intra.42.fr/oauth/token", data=auth_data)
        resp.raise_for_status()
        parsed_resp = resp.json()
        print("token generated. Expires in:", parsed_resp["expires_in"], "seconds")
        return parsed_resp["access_token"]

    def path(self, path: str, **kwargs):
        target = f"/v2/{path}"
        return HttpRequest(target, self.session, **kwargs)
    
    def full_path(self, path: str, **kwargs):
        target = path
        return HttpRequest(target, self.session, **kwargs)

    def pisciners(self, piscine_year: str, piscine_month: str): #return list()
        target = f"/v2/campus/{SEOUL}/users"
        filter={"pool_year": piscine_year, "pool_month": piscine_month}
        idx = 1
        user_data = []
        while True:
            resp = HttpRequest(target, self.session, filter=filter, page={"size": 100, "number": idx}).get()
            if len(resp) < 1:
                break
            user_data = user_data + resp
            idx += 1
            sleep(0.5)
        return user_data

