> [!NOTE]
> This project is a backend project, meaning that what matters the most is data storage, API, cache
> and testing. The directories inside [/enhancemnts](/enhancements) are for future integration and are not
> considered at the core of the project yet. After all, I AM A BACKEND STUDENT.

# IQA - Interactive Quiz Application 
## Description
IQA is my webstack portfolio project, the last project on my ALX SWE program.

It's an application for creating and taking quizzes. It's also inteneded to make likes,
add feedback and track your progress.

It can be used throgh an API, and I will work to make it sooner via the browser also :)

## Stack
### Front end
* HTML
* CSS
* JS
* 
IQA browser interface is written in HTML, CSS and JS to add an elegant appearance to the application.
### Backend
* Python3
* Flask
* SQLAlchemy
* Redis-py
* Bcrypt

The backend is mainly written in Python3 programming language. With Flask as web framework and SQLAlchemy as an ORM. I also used Redis-py to link the application code with the cache and Bcrypt to encrypt user passwords before storing in the database to enhance security.

### Storage
* MySQL

The most popular relational DBMS is used to facilitate data storage and retrieval.
### Cache
* Redis Stack Server

Which is a lightning-fast in memory data store to reduce response time and to manage quizzes sessions.
### Servers
* Nginx

A very well-know web server for powering web apps.
* Gunicorn
A WSGI compatible application server. It's used for powering the API.

## Setup
This project includes many integrating parts, so you need to set it up carefully if you want to run it.

These setups are targeted towards Linux, mainly Ubuntu 20.04

### First, you need to clone the project and to navigate to its directory

```
$ git clone https://github.com/Ahmad-0000/IQA.git
$ cd IQA
```

### You need these installed:
* Pyhton3 interpreter - version 3.8.10
* MySQL server - version 8.0.39-0ubuntu0.20.04.1 (Ubuntu)
* Redis Stack server - version 7.4.2
* Gunicorn server - version 22.0.0
* Flask - version 3.0.3
* SQLAclhemy - version 2.0.36
* Bcrypt - version 4.2.1 
* Redis-py - version 99.99.99

### You need these ENV varaibles defined
* IQA_DB_HOST: MySQL server host
* IQA_DB_PORT: MySQL server port
* IQA_DB_USER: MySQL server username
* IQA_DB_PAWD: MySQL server password
* IQA_DB_NAME: MySQL db name
* IQA_REDIS_HOST: Redis Stack server host
* IQA_REDIS_PORT: Redis Stack server port
* IQA_REDIS_DB: Redis Stack server db number
* IQA_QUIZ_SESSION_COOKIE: quiz session cookie name

### You need these running:
* MySQL server
* Redis Stack server

### after that, create the db
```
$ echo "CREATE DATABASE IF NOT EXISTS $IQA_DB_NAME;" | mysql -p
```

### Then run the following python script to create the tables

```
$ python3 create_tables.py
```
> [!NOTE]
> Running this script is required if you want to use multiple gunicorn processes
> to avoid race conditions between them to create the tables.

You can also use **Chrome** version 126.0.6478.126 (Official Build) (64-bit) to see some of the pages I want to integrate with
the api in the folder [/enhancements/web_static](/enhancement/web_static).

### Lastly, run gunicorn server and enjoy :)

```
$ gunicorn --bind=0.0.0.0:5000 --workers=3 api.v1.app:app
```

## Usage

Now, after you run your server successfully, you can interact with it via the tool of your choide;
cURL, nodeJS, python3, a browser, or whatever a choose you want.

You will find the full docs of each endpoint in its handler function in the files: [/api/v1/views/user.py](/api/v1/views/user.py),
[/api/v1/views/quiz.py](/api/v1/views/quiz.py), [/api/v1/views/feedback.py](api/v1/views/feedback.py), [/api/v1/views/like.py](api/v1/views/like.py) and [/api/v1/views/session_auth.py](/api/v1/views/session_auth.py). But as a teaser you can do this for example:

```
$ #### GET /api/v1/users => will return an empty list initially, because the db is fresh.
$ curl localhost:5001/api/v1/users -i
HTTP/1.1 200 OK
Server: gunicorn
Date: Mon, 27 Jan 2025 18:39:31 GMT
Connection: close
Content-Type: application/json
Content-Length: 3
Access-Control-Allow-Origin: http://localhost:8080
Access-Control-Allow-Credentials: true

[]
$ #### POST /api/v1/users => and here we create an account, note that I get a cookie for authentication and the user's password is not returned.
$ curl -i -X POST -d '{"first_name": "Ahmad", "middle_name": "Husain", "last_name": "Basheer", "dob": "2005-03-05", "email": "ahmad.new.m.v@gmail.com", "password": "imaginary"}' -H 'Content-Type: application/json' localhost:5001/api/v1/users
HTTP/1.1 201 CREATED
Server: gunicorn
Date: Mon, 27 Jan 2025 18:47:55 GMT
Connection: close
Content-Type: application/json
Content-Length: 304
Set-Cookie: login_session=6e0d3fcb-e953-4eca-81e0-4683c4690205; Expires=Thu, 06 Feb 2025 18:47:55 GMT; Path=/
Access-Control-Allow-Origin: http://localhost:8080
Access-Control-Allow-Credentials: true

{"added_at":"2025-01-27T18:47:55.518145","dob":"2005-03-05","email":"ahmad.new.m.v@gmail.com","first_name":"Ahmad","id":"75f12f54-1bd3-44a6-b308-10acbaf3af35","last_name":"Basheer","liked_quizzes_num":0,"middle_name":"Husain","quizzes_made":0,"quizzes_taken":0,"updated_at":"2025-01-27T18:47:55.518145"}
$ ### Now, if I do this: curl -s localhost:50001/api/v1/users | jq
$ curl -s localhost:5001/api/v1/users | jq
[
  {
    "added_at": "2025-01-27T18:47:56",
    "bio": null,
    "dob": "2005-03-05",
    "email": "ahmad.new.m.v@gmail.com",
    "first_name": "Ahmad",
    "id": "75f12f54-1bd3-44a6-b308-10acbaf3af35",
    "image_path": null,
    "last_name": "Basheer",
    "liked_quizzes_num": 0,
    "middle_name": "Husain",
    "quizzes_made": 0,
    "quizzes_taken": 0,
    "updated_at": "2025-01-27T18:47:56"
  }
]
$ # There is a lot more :), and there will be even more \o/\o/\o/
```

## Architecutre

* IQA is developed using Python3.8.10 programming language.

* With MySQL Server 8.0.39-0ubuntu0.20.04.1 (Ubuntu) as a DBMS.

* Redis Stack Server 7.4.2 as a Cache server. Used to chache the newest, oldest and most popular quizzes.
 It is also used for quiz sessions management.

* Gunicorn 22.0.0 as an app server

* No third party-services where used, but I’m looking forward to integrated with Elastcisearch and a Redis cluster.

  ![architecure](/architecture.png)

## What's next ?
* Implementing FTS using elasticsearch server
* Writing a Django version, a nodeJs version, and using mongoDB instead of MySQL for learning purpose.

## Contribution
This project is intended to extract most of my knowledge and to improve it, so it's not open for contribution.
But I'm looking forward to contribute in other web projects in the future.

## Authors
***Ahmad Basheer** <ahmad.new.m.v@gmail.com>


