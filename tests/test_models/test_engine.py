"""Test storage engine
"""
import unittest
import MySQLdb
from os import getenv
from uuid import uuid4
from datetime import date
from models.engine.storage import Storage
from models.users import User


unittest.TestLoader.sortTestMethodsUsing = None
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
        self.__class__.cursor.execute('SHOW TABLES;')
        tables_num = self.__class__.cursor.rowcount
        self.assertEqual(tables_num, 8)
        self.__class__.db_connection.commit()
    
    def test_add_and_save(self):
        """Test 'add' and 'save' methods
        """
        self.__class__.cursor.execute('SELECT COUNT(*) FROM users;')
        rows_num = self.__class__.cursor.fetchone()[0]
        u = User(
                    first_name="Ahmad",
                    middle_name="Husain",
                    last_name="Basheer",
                    dob=date(2005, 3, 5),
                    email=f"{str(uuid4())}@fake.fake",
                    password="fakepassword",
                    bio="Some bio"
                )
        u.save()
        self.__class__.db_connection.commit()
        self.__class__.cursor.execute('SELECT COUNT(*) FROM users;')
        new_rows_num = self.__class__.cursor.fetchone()[0]
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
        self.__class__.cursor.execute('SELECT id FROM users LIMIT 1;')
        id = self.__class__.cursor.fetchone()[0]
        self.assertEqual(id, storage.get(User, id).id)

    def test_method_filtered_get(self):
        """Test get filtered method
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
        users_with_name_ahmad = storage.get_filtered(User, {"first_name": "Ahmad"})
        users_with_name_mohammad = storage.get_filtered(User, {"first_name": "Mohammad"})
        users_with_father_zohair = storage.get_filtered(User, {"middle_name": "Zohair"})
        users_with_unknown_grandparent = storage.get_filtered(User, {"last_name": "Unknown"})
        self.assertGreaterEqual(len(users_with_name_ahmad), 2)
        self.assertGreaterEqual(len(users_with_father_zohair), 1)
        self.assertGreaterEqual(len(users_with_unknown_grandparent), 3)

    def test_method_delete(self):
        """Test "delete" method
        """
        self.__class__.cursor.execute('SELECT COUNT(*) FROM users;')
        rows_num = self.__class__.cursor.fetchone()[0]
        self.__class__.cursor.execute('SELECT id FROM users ORDER BY added_at DESC LIMIT 4;')
        for row in self.__class__.cursor.fetchall():
             user = storage.get(User, row[0])
             user.delete()
        self.__class__.db_connection.commit()
        self.__class__.cursor.execute('SELECT COUNT(*) FROM users;')
        new_rows_num = self.__class__.cursor.fetchone()[0]
        self.assertEqual(rows_num - 4, new_rows_num)
