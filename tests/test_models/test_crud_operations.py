"""Test CRUD operations using a "User" class instance
"""
import bcrypt
import unittest
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
        cls.user = User(first_name="Ahmad",
                         middle_name="Husain",
                         last_name="Basheer",
                         dob=date(2005, 3, 5),
                         email="ahmad.new.m.v@gmail.com",
                         password="fakepassword",
                         image_path="somepath",
                         bio="A person seeking to be a software engineer"
        )
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
        cls.user.delete()
        cls.cursor.close()
        cls.db_connection.close()

    def test_attributes(self):
        """Test normal initialization
        """
        expected_path = f"/data/iqa/images/user/{self.__class__.user.id}"
        expected_bio = "A person seeking to be a software engineer"
        self.assertEqual(self.__class__.user.first_name, "Ahmad")
        self.assertEqual(self.__class__.user.middle_name, "Husain")
        self.assertEqual(self.__class__.user.last_name, "Basheer")
        self.assertEqual(self.__class__.user.dob, date(2005, 3, 5))
        self.assertEqual(self.__class__.user.email, "ahmad.new.m.v@gmail.com")
        self.assertTrue(bcrypt.checkpw(bytes('fakepassword', 'utf-8'),
                        bytes(self.__class__.user.password, 'utf-8')))
        self.assertEqual(self.__class__.user.image_path, expected_path)
        self.assertEqual(self.__class__.user.bio, expected_bio)
        self.assertEqual(self.user.liked_quizzes_num, 0)
        self.assertEqual(self.user.quizzes_made, 0)
        self.assertEqual(self.user.quizzes_taken, 0)

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
        """Test object data update int the db
        """
    def test_db_creation(self):
        """Test object creation in the db
        """
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
        self.cursor.execute(f'SELECT first_name FROM users WHERE id = "{user.id}"')
        initial_first_name = self.cursor.fetchone()[0]
        user.update(first_name='Mohammad')
        self.db_connection.commit()
        self.cursor.execute(f'SELECT first_name FROM users WHERE id = "{user.id}"')
        new_first_name = self.cursor.fetchone()[0]
        self.assertEqual(initial_first_name, "Ahmad")
        self.assertEqual(new_first_name, "Mohammad")
