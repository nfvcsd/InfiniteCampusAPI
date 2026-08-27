import unittest

import requests

from infinitecampusapi import (
    APIError,
    AuthenticationError,
    InfiniteCampus,
    TransportError,
)


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self.payload = payload
        self.status_code = status_code

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, *, token_responses=None, api_responses=None):
        self.token_responses = token_responses or [
            FakeResponse({"access_token": "token", "expires_in": 3600})
        ]
        self.api_responses = api_responses or [FakeResponse({"users": []})]
        self.post_call = None
        self.get_call = None
        self.post_calls = []
        self.get_calls = []

    def post(self, url, **kwargs):
        self.post_call = (url, kwargs)
        self.post_calls.append(self.post_call)
        return self.token_responses.pop(0)

    def get(self, url, **kwargs):
        self.get_call = (url, kwargs)
        self.get_calls.append(self.get_call)
        return self.api_responses.pop(0)


class TransportTests(unittest.TestCase):
    def make_client(self, session):
        return InfiniteCampus(
            token_url="https://example.test/token",
            key="key",
            secret="secret",
            base_url="https://example.test/api/",
            session=session,
            timeout=12,
        )

    def test_session_timeout_and_query_parameters_are_used(self):
        session = FakeSession()
        client = self.make_client(session)

        result = client.api_call("students", filters="familyName='Doe & Sons'")

        self.assertEqual(result, {"users": []})
        self.assertEqual(session.post_call[1]["timeout"], 12)
        self.assertEqual(session.get_call[0], "https://example.test/api/students")
        self.assertEqual(session.get_call[1]["timeout"], 12)
        self.assertEqual(
            session.get_call[1]["params"],
            {"limit": 5000, "filter": "familyName='Doe & Sons'"},
        )
        self.assertEqual(
            session.get_call[1]["headers"], {"Authorization": "Bearer token"}
        )

    def test_api_failure_raises_api_error_with_context(self):
        session = FakeSession(api_responses=[FakeResponse({}, status_code=503)])
        client = self.make_client(session)

        with self.assertRaises(APIError) as raised:
            client.api_call("students")

        self.assertEqual(raised.exception.status_code, 503)
        self.assertEqual(raised.exception.endpoint, "students")

    def test_authentication_failure_raises_authentication_error(self):
        session = FakeSession(token_responses=[FakeResponse({}, status_code=401)])

        with self.assertRaises(AuthenticationError) as raised:
            self.make_client(session)

        self.assertEqual(raised.exception.status_code, 401)

    def test_request_failure_preserves_original_cause(self):
        class FailingSession(FakeSession):
            def get(self, url, **kwargs):
                raise requests.Timeout("timed out")

        client = self.make_client(FailingSession())

        with self.assertRaises(TransportError) as raised:
            client.api_call("students")

        self.assertIsInstance(raised.exception.__cause__, requests.Timeout)

    def test_expired_token_is_refreshed_before_api_call(self):
        session = FakeSession(
            token_responses=[
                FakeResponse({"access_token": "old", "expires_in": 3600}),
                FakeResponse({"access_token": "new", "expires_in": 3600}),
            ]
        )
        client = self.make_client(session)
        client.auth._expires_at = 0

        client.api_call("students")

        self.assertEqual(len(session.post_calls), 2)
        self.assertEqual(
            session.get_call[1]["headers"], {"Authorization": "Bearer new"}
        )

    def test_unauthorized_response_refreshes_and_retries_once(self):
        session = FakeSession(
            token_responses=[
                FakeResponse({"access_token": "old", "expires_in": 3600}),
                FakeResponse({"access_token": "new", "expires_in": 3600}),
            ],
            api_responses=[
                FakeResponse({}, status_code=401),
                FakeResponse({"users": []}),
            ],
        )
        client = self.make_client(session)

        result = client.api_call("students")

        self.assertEqual(result, {"users": []})
        self.assertEqual(len(session.post_calls), 2)
        self.assertEqual(len(session.get_calls), 2)
        self.assertEqual(
            session.get_calls[0][1]["headers"], {"Authorization": "Bearer old"}
        )
        self.assertEqual(
            session.get_calls[1][1]["headers"], {"Authorization": "Bearer new"}
        )

    def test_second_unauthorized_response_is_not_retried(self):
        session = FakeSession(
            token_responses=[
                FakeResponse({"access_token": "old", "expires_in": 3600}),
                FakeResponse({"access_token": "new", "expires_in": 3600}),
            ],
            api_responses=[
                FakeResponse({}, status_code=401),
                FakeResponse({}, status_code=401),
            ],
        )
        client = self.make_client(session)

        with self.assertRaises(APIError) as raised:
            client.api_call("students")

        self.assertEqual(raised.exception.status_code, 401)
        self.assertEqual(len(session.post_calls), 2)
        self.assertEqual(len(session.get_calls), 2)


if __name__ == "__main__":
    unittest.main()
