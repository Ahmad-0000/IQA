"""Test IQA API
"""
import unittest
from api.v1.app import app


class TestAPI(unittest.TestCase):
    """Main test class
    """
    @classmethod
    def setUpClass(cls):
        """Initialize the test class environment
        """
        app.config.update({"TESTING": True})
        cls.client = app.test_client()

    @classmethod
    def tearDownClass(cls):
        """Destroying class test environment
        """
        del cls.client

    def test_404(self):
        """Test error 404
        """
        error_404 = self.__class__.client.get("/none");
        self.assertEqual(error_404.status_code, 404)

