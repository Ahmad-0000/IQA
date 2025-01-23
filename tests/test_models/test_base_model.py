"""
Test BaseModel class and instances behavior
"""
import unittest
from datetime import datetime
from uuid import uuid4
from models.base_model import BaseModel


class TestBaseModel(unittest.TestCase):
    """Main Testing Class
    """
    def setUp(self):
        """Initialize a new object with each test case
        """
        self.bm = BaseModel()

    def tearDown(self):
        """Destroy previously initialized BaseModel
        """
        del self.bm

    def test_default_initialization(self):
        """Test "id", "added_at" and "updated_at" attributes presence
        """
        self.assertTrue(self.bm.id)
        self.assertTrue(self.bm.added_at)
        self.assertTrue(self.bm.updated_at)
        self.assertEqual(self.bm.added_at, self.bm.updated_at)

    def test_custom_initalization(self):
        """Test initalization from a custom dict
        """
        id, added_at = str(uuid4()), datetime.utcnow()
        updated_at = added_at
        del self.bm
        self.bm = BaseModel(**{
            'id': id,
            'added_at': added_at,
            'updated_at': updated_at
            })
        self.assertEqual(self.bm.id, id)
        self.assertEqual(self.bm.added_at, added_at)
        self.assertEqual(self.bm.updated_at, updated_at)

    def test_to_dict_method(self):
        """Test to_dict custom method
        """
        expected_dict = {
                'id': self.bm.id,
                'added_at': self.bm.added_at,
                'updated_at': self.bm.updated_at
            }
        self.assertEqual(self.bm.to_dict(), expected_dict)
