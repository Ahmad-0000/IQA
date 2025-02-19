"""
Test BaseModel class and instances behavior
"""
import unittest
from unittest.mock import patch
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

    # New feature
    def assertHasAttr(self, obj, attr):
        """Test attribute presence
        """
        result = hasattr(obj, attr)
        self.assertTrue(result)

    # New feature
    def assertAlmostEqualDatetimes(self, datetime1, datetime2):
        """Compare datetime objects for approximate equality
        """
        datetime1 = int(datetime1.timestamp())
        datetime2 = int(datetime2.timestamp())
        self.assertLess(abs(datetime1 - datetime2), 3)

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
                'added_at': self.bm.added_at.isoformat(),
                'updated_at': self.bm.updated_at.isoformat()
        }
        self.assertEqual(self.bm.to_dict(), expected_dict)

    @patch('models.base_model.BaseModel.to_dict', return_value='TO_DICT')
    def test_str_representation(self, patched_to_dict):
        """Test __str__ method return value
        """
        expected_str = f'[BaseModel] ({self.bm.id}) TO_DICT'
        real_str = self.bm.__str__()
        self.assertEqual(real_str, expected_str)

    @patch('models.storage.save')
    def test_update_method(self, patched_save):
        """Test the behavior of self.bm.update(**kwargs)
        """
        fake_added_at = datetime.utcnow()
        new_data = {
                    'id': '123456',
                    'added_at': fake_added_at,
                    'bouns_attribute': 'winner'
        }
        self.bm.update(**new_data)
        updated_at = datetime.utcnow()
        self.assertEqual(self.bm.id, '123456')
        self.assertEqual(self.bm.added_at, fake_added_at)
        self.assertHasAttr(self.bm, 'bouns_attribute')
        self.assertEqual(self.bm.bouns_attribute, 'winner')
        self.assertAlmostEqualDatetimes(self.bm.updated_at, updated_at)
