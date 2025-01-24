"""Test storage engine
"""
import unittest
<<<<<<< HEAD
import MySQLdb
from os import getenv
from uuid import uuid4
from datetime import date
from models.engine.storage import Storage
from models.users import User
=======
from unittest.mock import patch
import MySQLdb
from os import getenv
from datetime import date
from models.engine.storage import Storage
from models.users import User
from models.quizzes import Quiz
from sqlalchemy.orm.query import Query
from tests.test_models.fixtures import FILTERED_RESPONSE
from parameterized import parameterized
>>>>>>> storage


user = getenv('IQA_DB_USER')
pawd = getenv('IQA_DB_PAWD')
host = getenv('IQA_DB_HOST')
port = int(getenv('IQA_DB_PORT'))
db = getenv('IQA_DB_NAME')
storage = Storage()
<<<<<<< HEAD
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
        mocked_session.query.return_value.filter.return_value.limit.return_value.all.return_value = res
        data = storage.get_paged(Quiz, 'repeats', type, after)
        self.assertEqual(data, res)

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
=======


class TestStorageEngine(unittest.TestCase):
    """Main test class """
    
    @patch('tests.test_models.test_engine.Storage._Storage__session')
    def test_get(self, mocked_session):
        """Test "get" method
        """
        storage.reload()
        data = storage.get(User, 'Some id')
        mocked_session.assert_used_once = mocked_session.assert_called_once

    @patch('tests.test_models.test_engine.Storage._Storage__session')
    @patch('tests.test_models.test_engine.Query')
    def test_get_all(self, mocked_q, mocked_session):
        """Test "get_all" method
        """
        mocked_session.query.return_value = Query
        #mocked_q.order_by.return_value = Query
        storage.get_all(User)
        is_none = storage.get_all(int)
        mocked_session.query.assert_used_once_with = mocked_session.query.called_once_with
        mocked_session.query.return_value.order_by.assert_used_once = mocked_session.query.return_value.order_by.assert_called_once
        mocked_session.query.return_value.order_by.return_value.all.assert_used_once = mocked_session.query.return_value\
                                                                                       .order_by.return_value\
                                                                                       .all.assert_called_once 
        mocked_session.query.assert_used_once_with(User)
        mocked_session.query.return_value.order_by.assert_used_once()
        mocked_session.query.return_value.order_by.return_value.all.assert_used_once()
        self.assertIsNone(is_none)
 
    @patch('tests.test_models.test_engine.Storage._Storage__session')
    def test_method_delete(self, mocked_session):
        """Test "delete" method
        """
        user = "Some user"
        storage.delete(user)
        mocked_session.delete.assert_used_once_with = mocked_session.delete.assert_called_once_with
        mocked_session.delete.assert_used_once_with(user)
    
    @patch('tests.test_models.test_engine.Storage._Storage__session')
    def test_add(self, mocked_session):
        """Test "add" method
        """
        user = "Some user"
        mocked_session.add.assert_used_once_with = mocked_session.add.assert_called_once_with
        storage.add(user)
        mocked_session.add.assert_used_once_with(user)
    
    @patch('tests.test_models.test_engine.Storage._Storage__session')
    def test_save(self, mocked_session):
        """Test storage.save method
        """
        storage.save()
        mocked_session.commit.assert_used_once = mocked_session.commit.called_once
        mocked_session.commit.assert_used_once()
    
    @patch('tests.test_models.test_engine.Storage._Storage__session')
    def test_close(self, mocked_session):
        """Test storage.close method
        """
        storage.close()
        mocked_session.close.assert_used_once = mocked_session.close.called_once
        mocked_session.close.assert_used_once()

    @parameterized.expand([
            (
                'Ahmad',
                FILTERED_RESPONSE[0][0],
            ),
            (
                'Mohammad',
                FILTERED_RESPONSE[0][1],
            ),
            (
                'Ali',
                FILTERED_RESPONSE[0][2],
            )
    ])
    @patch('tests.test_models.test_engine.Storage._Storage__session')
    def test_get_filtered(self, first_name, res, mocked_session):
        """Test "storage.get_filtered" method
        """
        mocked_session.query.return_value.filter_by.return_value.all.return_value = res
        data = storage.get_filtered(User, {'first_name': first_name})
        self.assertEqual(data, res)

    @parameterized.expand([
        (
            'asc',
            10,
            FILTERED_RESPONSE[1][0]
        ),
        (
            'desc',
            30,
            FILTERED_RESPONSE[1][1]
        )
    ])
    @patch('tests.test_models.test_engine.Storage._Storage__session')
    def test_get_paged_with_popularity(self, type, after, res, mocked_session):
        """Test "storage.get_paged"
        """
        mocked_session.query.return_value.filter.return_value.limit.return_value.all.return_value = res
        data = storage.get_paged(Quiz, 'repeats', type, after)
        self.assertEqual(data, res)

    @parameterized.expand([
        (
            FILTERED_RESPONSE[2][0][0],
            FILTERED_RESPONSE[2][0][1],
            FILTERED_RESPONSE[2][0][2],
            FILTERED_RESPONSE[2][0][3],
            FILTERED_RESPONSE[2][0][4]

        ),
        (
            FILTERED_RESPONSE[2][1][0],
            FILTERED_RESPONSE[2][1][1],
            FILTERED_RESPONSE[2][1][2],
            FILTERED_RESPONSE[2][1][3],
            FILTERED_RESPONSE[2][1][4]
        )
    ])
    @patch('tests.test_models.test_engine.Storage._Storage__session')
    def test_get_categorized_with_popularity(self, categories, attr, _type, after, res, mocked_session):
        """Test "storage.get_paged"
        """
        mocked_session.query.return_value.order_by.return_value.filter.return_value.limit.return_value.all.return_value = res
        data = storage.get_categorized_quizzes(categories, attr, _type, after)
        self.assertEqual(data, res * len(categories))

>>>>>>> storage
