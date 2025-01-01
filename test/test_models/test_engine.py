"""Test storage engine
"""
import unittest
import MySQLdb
from os import getenv
from datetime import date
from models.engine.storage import Storage
from models.users import User
from models.quizzes import Quiz


user = getenv('IQA_DB_USER')
pawd = getenv('IQA_DB_PAWD')
host = getenv('IQA_DB_HOST')
port = int(getenv('IQA_DB_PORT'))
db = getenv('IQA_DB_NAME')
storage = Storage()
storage.reload()
db_connection = MySQLdb.connect(
                    user=user,
                    passwd=pawd,
                    host=host,
                    port=port,
                    db=db
                )

class TestStorageEngine(unittest.TestCase):
    """Main test class
    """
    def setUp(self):
        """Establish connection before each test case
        """
        self.db_connection = MySQLdb.connect(
                    user=user,
                    passwd=pawd,
                    host=host,
                    port=port,
                    db=db
                )
        self.cursor = db_connection.cursor()
        
        def tearDown(self):
            """Close the cursor and connection after each test
            """
            self.cursor.close()
            self.db_connection.close()

    def test_tables_number(self):
        """Test the number of tables in "iqa" database
        """
        self.cursor.execute('SHOW TABLES;')
        tables_num = self.cursor.rowcount
        self.assertEqual(tables_num, 5)
    
    def test_add_and_save(self):
        """Test 'add' and 'save' methods
        """
        self.cursor.execute('SELECT COUNT(*) FROM users;')
        rows_num = self.cursor.fetchone()[0]
        u = User(
                    first_name="Ahmad",
                    middle_name="Husain",
                    last_name="Basheer",
                    dob=date(2005, 3, 5),
                    email="ahmad.new.m.v@gmail.com",
                    password="fakepassword",
                    bio="Some bio"
                )
        u.save()
        self.cursor.close()
        self.db_connection.close()
        self.db_connection = MySQLdb.connect(
                    user=user,
                    passwd=pawd,
                    host=host,
                    port=port,
                    db=db
                )
        self.cursor = self.db_connection.cursor()
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
    
    def test_method_delete(self):
        """Test "delete" method
        """
        self.db_connection = MySQLdb.connect(
                    user=user,
                    passwd=pawd,
                    host=host,
                    port=port,
                    db=db
                )
        self.cursor = self.db_connection.cursor()
        self.cursor.execute('SELECT COUNT(*) FROM users;')
        rows_num = self.cursor.fetchone()[0]
        self.cursor.execute('SELECT id FROM users LIMIT 1;')
        id = self.cursor.fetchone()[0]
        u = storage.get(User, id)
        u.delete()
        self.db_connection.commit()
        self.cursor = self.db_connection.cursor()
        self.cursor.execute('SELECT COUNT(*) FROM users;')
        new_rows_num = self.cursor.fetchone()[0]
        self.assertEqual(rows_num - 1, new_rows_num)
