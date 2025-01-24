from models.users import User
from models.quizzes import Quiz


user_1 = User(first_name="Ahmad")
user_2 = User(first_name="Ahmad")
user_3 = User(first_name="Mohammdad")
user_4 = User(first_name="Ali")
user_5 = User(first_name="Ali")

quiz_1 = Quiz(repeats=10, category='Medicine')
quiz_2 = Quiz(repeats=20, category='CS')
quiz_3 = Quiz(repeats=30, category='Medicine')
quiz_4 = Quiz(repeats=40, category='Food')
quiz_5 = Quiz(repeats=50, category='Physics')
quiz_6 = Quiz(repeats=60, category='CS')

FILTERED_RESPONSE = [
    (
        [user_1, user_2],
        [user_3],
        [user_4, user_5]
    ),
    (
        [quiz_2, quiz_3, quiz_4, quiz_5, quiz_6],
        [quiz_5, quiz_4, quiz_3, quiz_2, quiz_1]
    ),
    (
        (['Medicine'], 'repeats', 'asc', 'initial', [quiz_1, quiz_3]),
        (['CS', 'Food', 'Physics'], 'repeats', 'desc', 'initial', [quiz_2, quiz_4, quiz_5, quiz_6]),
    )
]
