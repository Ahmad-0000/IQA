#!/usr/bin/env python3
from models.users import User
from datetime import date


user = User(
        first_name='Ahmad',
        middle_name='Husain',
        last_name='Ali',
        dob=date.fromisoformat('2005-03-05'),
        email='ahmad.new.m.v@gmail.com',
        password='fakepassword'
)

user_account_creation_success_response = user.to_dict()

TEST_FIXTURE = {
    "POST": [
        (
            None,
            'Husain',
            'Ali',
            '2005-03-05',
            'ahmad.new.m.v@gmail.com',
            'fakepassword',
            {'error': 'Missing data'},
            400
        ),
        (
            'Ahmad',
            'Husain',
            'Ali',
            '2005/3/5',
            'ahmad.new.m.v@gmail.com',
            'fakepassword',
            {'error': 'Use YYYY-MM-DD format for date of birth'}, 
            400
        ),
        (
            'Ahmad',
            'Husain',
            'Ali',
            '2017-03-05',
            'ahmad.new.m.v@gmail.com',
            'fakepassword',
            {'error': 'You need to be at least 10 years old'},
            400
        ),
        (
            'A very long first name',
            'Husain',
            'Ali',
            '2005-03-05',
            'ahmad.new.m.v@gmail.com',
            'fakepassword',
            {'error': 'Abide to data constraints'},
            400
        ),
        (
            'Ahmad',
            'Husain',
            'Ali',
            '2005-03-05',
            'ahmad.new.m.v@gmail.com',
            'fakepassword',
            user_account_creation_success_response,
            201
        )
    ]
}
