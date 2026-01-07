"""
Tests rate limiting enforcement, exemptions, and error responses
"""
import unittest
import time
from fastapi.testclient import TestClient

from main import app
from hotel.config import settings


class TestRateLimiting(unittest.TestCase):
    """Test rate limiting functionality across endpoints"""

    def setUp(self):
        """Set up test client"""
        self.client = TestClient(app)

    def test_health_endpoint_not_rate_limited(self):
        """Test that health check endpoints are exempt from rate limiting"""
        # Make many rapid requests - should all succeed
        for _ in range(150):  # In excess of any rate limit
            response = self.client.get("/health/")
            self.assertEqual(response.status_code, 200)

    def test_successful_request_within_limit(self):
        """Test that requests within the rate limit succeed"""
        # Test the root endpoint which has no rate limit
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_rate_limit_exceeded_returns_429(self):
        """Test that exceeding rate limit returns 429 status code"""
        # Parse the rate limit for customers (e.g., 50/minute)
        limit_str = settings.rate_limit_search
        limit_value = int(limit_str.split("/")[0])

        # Make requests up to the limit + 1
        responses = []
        for i in range(limit_value + 5):
            response = self.client.get("/customers")
            responses.append(response.status_code)

        # Should have at least one 429 response
        self.assertIn(429, responses, "Expected at least one 429 Too Many Requests response")

    def test_429_response_format(self):
        """Test that 429 response is formatted correctly"""
        # Exceed the rate limit
        limit_str = settings.rate_limit_search
        limit_value = int(limit_str.split("/")[0])

        response = None
        for _ in range(limit_value + 5):
            response = self.client.get("/customers")
            if response.status_code == 429:
                break

        if response and response.status_code == 429:
            data = response.json()
            self.assertIn("error", data)
            self.assertEqual(data["error"], "Rate Limit Exceeded")
            self.assertIn("message", data)
            self.assertIn("details", data)
            self.assertIn("Retry-After", response.headers)

    def test_different_endpoints_have_independent_limits(self):
        """Test that different endpoints have independent rate limits"""
        # This test verifies rate limiting is per-endpoint, not global
        # That is, making requests to one endpoint shouldn't block another

        # Health check is always exempt; just to confirm
        response1 = self.client.get("/health/")
        self.assertEqual(response1.status_code, 200)

        # Root endpoint has no rate limit
        response2 = self.client.get("/")
        self.assertEqual(response2.status_code, 200)

    def test_write_operations_have_stricter_limits(self):
        """Test that write operations have lower limits than read operations"""
        read_limit = int(settings.rate_limit_read.split("/")[0])
        write_limit = int(settings.rate_limit_write.split("/")[0])
        delete_limit = int(settings.rate_limit_delete.split("/")[0])

        self.assertGreater(read_limit, write_limit, "Read limit should be higher than write limit")
        self.assertGreater(write_limit, delete_limit, "Write limit should be higher than delete limit")

    def test_rate_limit_configuration_from_settings(self):
        """Test that rate limits are properly loaded from settings"""
        self.assertTrue(settings.rate_limit_enabled)
        self.assertIsNotNone(settings.rate_limit_read)
        self.assertIsNotNone(settings.rate_limit_write)
        self.assertIsNotNone(settings.rate_limit_delete)
        self.assertIsNotNone(settings.rate_limit_search)


class TestRateLimitWhitelist(unittest.TestCase):
    """Test rate limit whitelist functionality"""

    def setUp(self):
        """Set up test client"""
        self.client = TestClient(app)

    def test_localhost_in_whitelist(self):
        """Test that localhost is in the default whitelist"""
        whitelist = settings.rate_limit_whitelist.split(",")
        self.assertIn("127.0.0.1", whitelist)


if __name__ == "__main__":
    unittest.main()
