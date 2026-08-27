from .classes.auth import Auth
from .classes.Students import Students
from .classes.Student import Student
from .classes.Teachers import Teachers
from .classes.Schools import Schools
from .classes.Demographics import Demographics
from .classes.AcademicSessions import AcademicSessions
from .classes.Courses import Courses
from .classes.Enrollments import Enrollments
from .classes.GradingPeriods import GradingPeriods
from .classes.Orgs import Orgs
from .classes.Terms import Terms
from .classes.Users import Users
from .exceptions import APIError, ResponseDecodeError, TransportError
import requests


class InfiniteCampus:
    """Python Object for Interacting with Infinite Campus.
    Requires token_url, key, secret, and base_url"""

    url: str

    def __init__(self, token_url, key, secret, base_url, session=None, timeout=30):
        self.session = session if session is not None else requests.Session()
        self.timeout = timeout
        self.auth = Auth(
            token_url,
            key,
            secret,
            base_url,
            session=self.session,
            timeout=self.timeout,
        )
        self.url = self.auth.base_url
        self.students = Students(api_call=self.api_call)
        self.student = Student(api_call=self.api_call)
        self.teachers = Teachers(api_call=self.api_call)
        self.schools = Schools(api_call=self.api_call)
        self.demographics = Demographics(api_call=self.api_call)
        self.academicSessions = AcademicSessions(api_call=self.api_call)
        self.courses = Courses(api_call=self.api_call)
        self.enrollments = Enrollments(api_call=self.api_call)
        self.gradingPeriods = GradingPeriods(api_call=self.api_call)
        self.orgs = Orgs(api_call=self.api_call)
        self.terms = Terms(api_call=self.api_call)
        self.users = Users(api_call=self.api_call)

    @property
    def access_token(self) -> str:
        """Return the current token while preserving the original public attribute."""
        return self.auth.access_token

    def api_call(self, endpoint, filters=""):
        params = {"limit": 5000}
        if filters:
            params["filter"] = filters
        url = f"{self.url.rstrip('/')}/{endpoint.lstrip('/')}"

        for attempt in range(2):
            headers = {"Authorization": f"Bearer {self.auth.access_token}"}
            try:
                response = self.session.get(
                    url,
                    headers=headers,
                    params=params,
                    timeout=self.timeout,
                )
            except requests.RequestException as exc:
                raise TransportError(
                    f"Unable to reach API endpoint {endpoint}"
                ) from exc

            if response.status_code != 401 or attempt == 1:
                break
            self.auth.refresh(force=True)

        if not 200 <= response.status_code < 300:
            raise APIError(
                f"API endpoint {endpoint} returned status code {response.status_code}",
                status_code=response.status_code,
                endpoint=endpoint,
            )

        try:
            return response.json()
        except (requests.exceptions.JSONDecodeError, ValueError) as exc:
            raise ResponseDecodeError(
                f"API endpoint {endpoint} returned invalid JSON"
            ) from exc
