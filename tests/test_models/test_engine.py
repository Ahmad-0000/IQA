"""Test storage engine
"""
import unittest
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


user = getenv('IQA_DB_USER')
pawd = getenv('IQA_DB_PAWD')
host = getenv('IQA_DB_HOST')
port = int(getenv('IQA_DB_PORT'))
db = getenv('IQA_DB_NAME')
storage = Storage()


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

