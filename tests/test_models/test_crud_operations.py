"""Test CRUD operations on classes inhereting from "Base"
    using a "User" class instance.

    NOTE: "Reading" operation will not be tested here, it will
    be tested as an engine funcionality
"""
import bcrypt
import unittest
from unittest.mock import patch
from datetime import date
from models.users import User
import MySQLdb
from os import getenv


user = getenv('IQA_DB_USER')
pawd = getenv('IQA_DB_PAWD')
host = getenv('IQA_DB_HOST')
port = int(getenv('IQA_DB_PORT'))
db = getenv('IQA_DB_NAME')


class TestUser(unittest.TestCase):
    """Main test class
    """
    @classmethod
    def setUpClass(cls):
        """Execute for class initalization
        """
        cls.db_connection = MySQLdb.connect(
                    user=user,
                    passwd=pawd,
                    host=host,
                    port=port,
                    db=db
        )
        cls.cursor = cls.db_connection.cursor()

    @classmethod
    def tearDownClass(cls):
        """Execute for class clean up
        """
        cls.cursor.close()
        cls.db_connection.close()

    def test_attributes(self):
        """Test normal initialization
        """
        with patch('models.Storage'):
            user = User(
                         first_name="Ahmad",
                         middle_name="Husain",
                         last_name="Basheer",
                         dob=date(2005, 3, 5),
                         email="ahmad.new.m.v@gmail.com",
                         password="fakepassword",
                         image_path="somepath",
                         bio="A person seeking to be a software engineer"
            )
            user.save()
            expected_path = f"/data/iqa/images/user/{user.id}"
            expected_bio = "A person seeking to be a software engineer"
            self.assertEqual(user.first_name, "Ahmad")
            self.assertEqual(user.middle_name, "Husain")
            self.assertEqual(user.last_name, "Basheer")
            self.assertEqual(user.dob, date(2005, 3, 5))
            self.assertEqual(user.email, "ahmad.new.m.v@gmail.com")
            self.assertTrue(bcrypt.checkpw(bytes('fakepassword', 'utf-8'),
                            bytes(user.password, 'utf-8')))
            self.assertEqual(user.image_path, expected_path)
            self.assertEqual(user.bio, expected_bio)
            self.assertEqual(user.liked_quizzes_num, 0)
            self.assertEqual(user.quizzes_made, 0)
            self.assertEqual(user.quizzes_taken, 0)

    def test_db_creation(self):
        """Test object creation in the db
        """
        self.cursor.execute('SELECT COUNT(*) FROM users;')
        initial_rows_number = self.cursor.fetchone()[0]
        self.db_connection.commit()
        user = User(
                         first_name="Ahmad",
                         middle_name="Husain",
                         last_name="Basheer",
                         dob=date(2005, 3, 5),
                         email="ahmadhusain5002@gmail.com",
                         password="fakepassword",
                         image_path="somepath",
                         bio="A person seeking to be a software engineer"
        )
        user.save()
        self.cursor.execute('SELECT COUNT(*) FROM users;')
        new_rows_number = self.cursor.fetchone()[0]
        self.db_connection.commit()
        self.assertEqual(initial_rows_number + 1, new_rows_number)

    def test_db_update(self):
        """Test object data update in the db
        """
        user = User(
                         first_name="Ahmad",
                         middle_name="Husain",
                         last_name="Basheer",
                         dob=date(2005, 3, 5),
                         email="ahmadfruit311@gmail.com",
                         password="fakepassword",
                         image_path="somepath",
                         bio="A person seeking to be a software engineer"
        )
        user.save()
        self.db_connection.commit()
        self.cursor.execute(f'SELECT first_name FROM users WHERE id = "{user.id}"')
        initial_first_name = self.cursor.fetchone()[0]
        user.update(first_name='Mohammad')
        self.db_connection.commit()
        self.cursor.execute(f'SELECT first_name FROM users WHERE id = "{user.id}"')
        new_first_name = self.cursor.fetchone()[0]
        cls.user.save()
        cls.db_connection = MySQLdb.connect(
                    user=user,
                    passwd=pawd,
                    host=host,
                    port=port,
                    db=db
        )
        cls.cursor = cls.db_connection.cursor()

    @classmethod
    def tearDownClass(cls):
        """Execute for class clean up
        """
        cls.cursor.close()
        cls.db_connection.close()

    def test_db_creation(self):
        """Test object creation in the db
        """
        self.cursor.execute('SELECT COUNT(*) FROM users;')
        initial_rows_number = self.cursor.fetchone()[0]
        self.db_connection.commit()
        user = User(
                         first_name="Ahmad",
                         middle_name="Husain",
                         last_name="Basheer",
                         dob=date(2005, 3, 5),
                         email="ahmadhusain5002@gmail.com",
                         password="fakepassword",
                         image_path="somepath",
                         bio="A person seeking to be a software engineer"
        )
        user.save()
        self.cursor.execute('SELECT COUNT(*) FROM users;')
        new_rows_number = self.cursor.fetchone()[0]
        self.db_connection.commit()
        self.assertEqual(initial_rows_number + 1, new_rows_number)

    def test_db_update(self):
        """Test object data update in the db
        """
        user = User(
                         first_name="Ahmad",
                         middle_name="Husain",
                         last_name="Basheer",
                         dob=date(2005, 3, 5),
                         email="ahmadfruit311@gmail.com",
                         password="fakepassword",
                         image_path="somepath",
                         bio="A person seeking to be a software engineer"
        )
        user.save()
        self.db_connection.commit()
        self.cursor.execute(f'SELECT first_name FROM users WHERE id = "{user.id}"')
        initial_first_name = self.cursor.fetchone()[0]
        user.update(first_name='Mohammad')
        self.db_connection.commit()
        self.cursor.execute(f'SELECT first_name FROM users WHERE id = "{user.id}"')
        new_first_name = self.cursor.fetchone()[0]
        self.assertEqual(initial_first_name, "Ahmad")
        self.assertEqual(new_first_name, "Mohammad")


    def test_db_deletion(self):
        """Test deletion from the database
        """
        user = User(
                         first_name="Ahmad",
                         middle_name="Husain",
                         last_name="Basheer",
                         dob=date(2005, 3, 5),
                         email="ahmadfruit211@gmail.com",
                         password="fakepassword",
                         image_path="somepath",
                         bio="A person seeking to be a software engineer"
        )
        user.save()
        self.db_connection.commit()
        self.cursor.execute(f'SELECT COUNT(*) FROM users WHERE id = "{user.id}"')
        initial_user_presence = bool(self.cursor.fetchone()[0])
        user.delete() 
        self.db_connection.commit()
        self.cursor.execute(f'SELECT COUNT(*) FROM users WHERE id = "{user.id}"')
        new_user_presence = bool(self.cursor.fetchone()[0])
        self.assertTrue(initial_user_presence)
        self.assertFalse(new_user_presence)
