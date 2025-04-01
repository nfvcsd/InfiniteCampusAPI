from .classes.auth import Auth
from .classes.Students import Students
from .classes.Student import Student
from .classes.Teachers import Teachers
import requests


class InfiniteCampus:
    access_token: str
    url: str

    def __init__(self, token_url, key, secret, base_url):
        credentials = Auth(
            token_url,
            key,
            secret,
            base_url,
        )
        self.access_token = credentials.access_token
        self.url = credentials.base_url
        self.students = Students(api_call=self.api_call)
        self.student = Student(api_call=self.api_call)
        self.teachers = Teachers(api_call=self.api_call)

    def api_call(self, endpoint):
        token = self.access_token
        headers = {"Authorization": f"Bearer {token}"}
        r = requests.get(f"{self.url}{endpoint}?limit=5000", headers=headers)
        if r.status_code != 200:
            print(f"API Call returned {r.status_code} status")
        return r.json()
