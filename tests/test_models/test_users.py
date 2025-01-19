"""Test "User" class behavior
"""
import bcrypt
import unittest
from uuid import uuid4
from datetime import date, timedelta
from sqlalchemy.exc import DataError
from models import storage
from models.users import User
from models.exc import DOBError


class TestUser(unittest.TestCase):
    """Main test class
    """
    @classmethod
    def setUpClass(cls):
        """Execute for class initalization
        """
        cls.user_email = f"{str(uuid4())}@fake.fake"
        cls.user = User(first_name="Ahmad",
                         middle_name="Husain",
                         last_name="Basheer",
                         dob=date(2005, 3, 5),
                         email=cls.user_email,
                         password="fakepassword",
                         image_path="invalid",
                         bio="A person seeking to be a software engineer")

    @classmethod
    def tearDownClass(cls):
        """Execute for class clean up
        """
        del cls.user

    def test_attributes(self):
        """Test normal initialization
        """
        expected_path = f"/data/iqa/images/user/{self.user.id}"
        expected_bio = "A person seeking to be a software engineer"
        self.assertEqual(self.user.first_name, "Ahmad")
        self.assertEqual(self.user.middle_name, "Husain")
        self.assertEqual(self.user.last_name, "Basheer")
        self.assertEqual(self.user.dob, date(2005, 3, 5))
        self.assertEqual(self.user.email, self.user_email)
        self.assertTrue(bcrypt.checkpw(bytes('fakepassword', 'utf-8'),
                        bytes(self.user.password, 'utf-8')))
        self.assertEqual(self.user.image_path, expected_path)
        self.assertEqual(self.user.bio, expected_bio)

    def test_dob_raises(self):
        """Test users ages
        """
        with self.assertRaises(DOBError):
            new_user = User(
                        first_name="Unknown",
                        middle_name="Unknown",
                        last_name="Unknown",
                        dob=date.today(),
                        email=f"{str(uuid4())}@fake.fake",
                        password="fake"
                    )
            new_user.save()
