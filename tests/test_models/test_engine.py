"""Test storage engine
"""
import unittest
import MySQLdb
from os import getenv
from uuid import uuid4
from datetime import date
from models.engine.storage import Storage
from models.users import User


user = getenv('IQA_DB_USER')
pawd = getenv('IQA_DB_PAWD')
host = getenv('IQA_DB_HOST')
port = int(getenv('IQA_DB_PORT'))
db = getenv('IQA_DB_NAME')
storage = Storage()
storage.reload()


class TestStorageEngine(unittest.TestCase):
    """Main test class
    """

    @classmethod
    def setUpClass(cls):
        """Establish db connection for this class
        """
        user1 = User(
                    first_name="Ahmad",
                    middle_name="Zohair",
                    last_name="Unknown",
                    dob=date(2005, 3, 5),
                    email=f"{str(uuid4())}@fake.fake",
                    password="fakepassword",
                    bio="Some bio"
                )
        user1.save()
        user2 = User(
                    first_name="Mohammad",
                    middle_name="Ali",
                    last_name="Unknown",
                    dob=date(2005, 3, 5),
                    email=f"{str(uuid4())}@fake.fake",
                    password="fakepassword",
                    bio="Some bio"
                )
        user2.save()
        user3 = User(
                    first_name="Mohammad",
                    middle_name="Ali",
                    last_name="Unknown",
                    dob=date(2005, 3, 5),
                    email=f"{str(uuid4())}@fake.fake",
                    password="fakepassword",
                    bio="Some bio"
                )
        user3.save()
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
        """Close the cursor and connection of this class
        """
        cls.cursor.close()
        cls.db_connection.close()

    def test_tables_number(self):
        """Test the number of tables in "iqa" database
        """
        self.cursor.execute('SHOW TABLES;')
        tables_num = self.cursor.rowcount
        self.assertEqual(tables_num, 8)
    
    def test_add_and_save(self):
        """Test 'add' and 'save' methods
        """
        self.cursor.execute('SELECT COUNT(*) FROM users;')
        rows_num = self.cursor.fetchone()[0]
        u = User(
                    first_name="Unknown",
                    middle_name="Husain",
                    last_name="Basheer",
                    dob=date(2005, 3, 5),
                    email=f"{str(uuid4())}@fake.fake",
                    password="fakepassword",
                    bio="Some bio"
                )
        u.save()
        self.db_connection.commit()
        self.cursor.execute('SELECT COUNT(*) FROM users;')
        new_rows_num = self.cursor.fetchone()[0]
        self.assertEqual(rows_num + 1, new_rows_num)

    def test_get_all(self):
        """Test "get_all" method
        """
        objects = storage.get_all(User)
        is_none = storage.get_all(int)
        are_similar = filter(lambda obj: isinstance(obj, User), objects)
        self.assertTrue(are_similar)
        self.assertIsNone(is_none)

    def test_get(self):
        """Test "get" method
        """
        self.cursor.execute('SELECT id FROM users LIMIT 1;')
        id = self.cursor.fetchone()[0]
        self.assertEqual(id, storage.get(User, id).id)

    def test_method_filtered_get(self):
        """Test get filtered method
        """
        user1 = User(
                    first_name="fake_1",
                    middle_name="fakefather_1",
                    last_name="fakegrandfather_1",
                    dob=date(2005, 3, 5),
                    email=f"{str(uuid4())}@fake.fake",
                    password="fakepassword",
                    bio="Some bio"
                )
        user1.save()
        user2 = User(
                    first_name="fake_2",
                    middle_name="fakefather_1",
                    last_name="fakegrandfather_1",
                    dob=date(2005, 3, 5),
                    email=f"{str(uuid4())}@fake.fake",
                    password="fakepassword",
                    bio="Some bio"
                )
        user2.save()
        user3 = User(
                    first_name="Mohammad",
                    middle_name="Ali",
                    last_name="fakegrandfather_1",
                    dob=date(2005, 3, 5),
                    email=f"{str(uuid4())}@fake.fake",
                    password="fakepassword",
                    bio="Some bio"
                )
        user3.save()
        self.db_connection.commit()
        users_with_name_fake_1 = storage.get_filtered(User, {"first_name": "fake_1"})
        users_with_father_fakefather_1 = storage.get_filtered(User, {"middle_name": "fakefather_1"})
        users_with_fakegrandfather_1 = storage.get_filtered(
                                User, 
                                {"last_name": "fakegrandfather_1"}
                            )
        self.assertGreaterEqual(len(users_with_name_fake_1), 1)
        self.assertGreaterEqual(len(users_with_father_fakefather_1), 2)
        self.assertGreaterEqual(len(users_with_fakegrandfather_1), 3)

    def test_method_delete(self):
        """Test "delete" method
        """
        self.cursor.execute('SELECT COUNT(*) FROM users;')
        rows_num = self.cursor.fetchone()[0]
        self.cursor.execute('SELECT id FROM users LIMIT 3;')
        result = self.cursor.fetchall()
        for row in result:
            user = storage.get(User, row[0])
            user.delete()
        self.db_connection.commit()
        self.cursor.execute('SELECT COUNT(*) FROM users;')
        new_rows_num = self.cursor.fetchone()[0]
        self.assertEqual(rows_num - 3, new_rows_num)
