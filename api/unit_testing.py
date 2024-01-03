from dataclasses import dataclass
import json
import unittest
from urllib import response
import uuid
from app import app
from flask import  jsonify
from app import db,User,Page, Access
from base64 import b64encode
from werkzeug.security import generate_password_hash



class BasicTests(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        # DB Einrichten
        self.app = app.test_client()


    def tearDown(self) -> None:
        db.create_all()
        return super().tearDown()

    def test_hi(self):
        response=self.app.get('/hi', follow_redirects=True)
        self.assertEqual(response.status_code,200);
        self.assertEqual(response.data,b"Hello World from Backend")

    #test root route
    def test_root(self):
        response=self.app.get('/', follow_redirects=True)
        self.assertEqual(response.status_code,200);
        self.assertEqual(response.data,b"application is up and running!")

    #test loggertest
    def test_logging(self):
        response=self.app.get('/loggertest', follow_redirects=True)
        self.assertEqual(response.status_code,200);
        self.assertEqual(response.data,b"Logging Messages logged")
    
    #test clean install
    def test_clean_install(self):
        response=self.app.get('/cleaninstall', follow_redirects=True)
        self.assertEqual(response.status_code,200);
        self.assertEqual(response.data,b"Database was cleaned, recreated and filled with dummyData.")
        #check if dummy users are in db
        dummy_users = ["teacher1", "teacher2", "teacher3", "admin1", "admin2", "admin3", "student1", "student2", "student3"]

        # Check if dummy users are in the database
        for username in dummy_users:
            user = User.query.filter_by(username=username).first()
            self.assertIsNotNone(user, f"User {username} not found in database.")
            self.assertEqual(user.username, username)

        # user1=User.query.filter_by(username="teacher1").first()
        # user2=User.query.filter_by(username="teacher2").first()
        # user3=User.query.filter_by(username="teacher3").first()
        # user4=User.query.filter_by(username="admin1").first()
        # user5=User.query.filter_by(username="admin2").first()
        # user6=User.query.filter_by(username="admin3").first()
        # user7=User.query.filter_by(username="student1").first()
        # user8=User.query.filter_by(username="student2").first()
        # user9=User.query.filter_by(username="student3").first()
        # self.assertEqual(user1.username,"teacher1")
        # self.assertEqual(user2.username,"teacher2")
        # self.assertEqual(user3.username,"teacher3")
        # self.assertEqual(user4.username,"admin1")
        # self.assertEqual(user5.username,"admin2")
        # self.assertEqual(user6.username,"admin3")
        # self.assertEqual(user7.username,"student1")
        # self.assertEqual(user8.username,"student2")
        # self.assertEqual(user9.username,"student3")
        #check if dummy pages are in db


class UserEndpointTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        # DB Einrichten
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
        #add admin user
        admin =  User("adminName","adminUsername","admin@mail.com",generate_password_hash("adminPW"))
        admin.isAdmin = True
        db.session.add(admin)
        # INS-BEG-FPI-20231011
 #       test12 = User("test12","test12","test12@mail.com",generate_password_hash("supersafe"))
  #      db.session.add(test12)
        # INS-END-FPI-20231011
        db.session.commit()



    def tearDown(self) -> None:
        return super().tearDown()

    def test_createUser(self):

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype
        }
        data = {
                "name":"Florian",
                "mail":"florian@mail.com",
                "password":"supersafe",
                "username":"floreian"
        }
        url = '/user'

        response = self.app.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code,201)

    def test_createUser_DuplicateMail(self):
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype
        }
        data1 = {
                "name":"Florian",
                "mail":"florian@mail.com",
                "password":"supersafe",
                "username":"floreian"
        }
        data2 = {
                "name":"herold",
                "mail":"florian@mail.com",
                "password":"sdfer",
                "username":"hari"
        }
        url = '/user'

        response1 = self.app.post(url, json=data1, headers=headers)
        response2 = self.app.post(url, json=data2, headers=headers)

        self.assertEqual(response1.status_code,201)
        self.assertEqual(response2.status_code,406)
        self.assertEqual(response2.json["message"],"Email already in use!")

    def test_createUser_DuplicateUsername(self):
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype
        }
        data1 = {
                "name":"Florian",
                "mail":"florian@mail.com",
                "password":"supersafe",
                "username":"floreian"
        }
        data2 = {
                "name":"herold",
                "mail":"herold@mail.com",
                "password":"sdfer",
                "username":"floreian"
        }
        url = '/user'

        response1 = self.app.post(url, json=data1, headers=headers)
        response2 = self.app.post(url, json=data2, headers=headers)

        self.assertEqual(response1.status_code,201)
        self.assertEqual(response2.status_code,406)
        self.assertEqual(response2.json["message"],"Username already in use!")

    #test create user with invalid mail
    def test_createUser_InvalidMail(self):
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype
        }
        data = {
                "name":"Florian",
                "mail":"florian",
                "password":"supersafe",
                "username":"floreian"
        }
        url = '/user'

        response = self.app.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"Not a valid email adress!")

    def test_getUser(self):
        self.test_createUser()
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        #get existing user id
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/users'
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json),2)
        user_id = response.json[1]["userID"]


        url = '/user/'+user_id
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["name"],"Florian")

    def test_getUser_NotExisting(self):
        self.test_createUser()
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        #get existing user id
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/user/'+str(uuid.uuid4())
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,404)

    def test_getUser_NotAuthorized(self):
        self.test_createUser()
        data = {
                "name":"newName",
                "mail":"new@mail.at",
                "password":"newPassword",
                "username":"newUsername"
        }
        data2 = {
                "name":"newName2",
                "mail":"new2@mail.at",
                "password":"newPassword2",
                "username":"newUsername2"
        }
        url = '/user'
        response = self.app.post(url, json=data)
        self.assertEqual(response.status_code,201)
        
        response = self.app.post(url, json=data2)
        self.assertEqual(response.status_code,201)

        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/users'
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json),4)
        user_id = response.json[2]["userID"]

        url = '/user/'+user_id
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,406)

    #test get user by username
    def test_getUserByUsername(self):
        self.test_createUser()
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        #get existing user id
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/user/username/floreian'
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["name"],"Florian")

    def test_getUserByUsername_NotExisting(self):
        self.test_createUser()
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        #get existing user id
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/user/username/'+str(uuid.uuid4())
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,404)

    def test_getUserByUsername_NotAuthorized(self):
        self.test_createUser()
        data = {
                "name":"newName",
                "mail":"new@mail.com",
                "password":"newPassword",
                "username":"newUsername"
        }
        url = '/user'
        response = self.app.post(url, json=data)
        self.assertEqual(response.status_code,201)

        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/user/username/newUsername'
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,406)

    def test_updateUser(self):
        self.test_createUser()
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        #get existing user id
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/users'
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json),2)
        user_id = response.json[1]["userID"]

        data = {
                'userID':user_id,
                "name":"newName",
                "mail":"new@mail.at",
                "password":"newPassword",
                "username":"newUsername"
        }
        url = '/user'
        response = self.app.put(url, json=data, headers=headers)
        
        self.assertEqual(response.status_code,200)

        #get user to check if update was successful
        url = '/user/'+user_id
        response = self.app.get(url, headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["name"],"newName")
        self.assertEqual(response.json["mail"],"new@mail.at")
        self.assertEqual(response.json["username"],"newUsername")

    def test_updateUser_NotExisting(self):
        self.test_createUser()
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        data = {
                'userID':str(uuid.uuid4()),
                "name":"newName",
                "mail":"new@mail.at",
                "password":"newPassword",
                "username":"newUsername"
        }
        url = '/user'
        response = self.app.put(url, json=data, headers=headers)
        
        self.assertEqual(response.status_code,404)

    def test_updateUser_NotAuthorized(self):
        self.test_createUser()
        #create random user
        data = {
                "name":"newName",
                "mail":"new@mail.at",
                "password":"newPassword",
                "username":"newUsername"
        }
        data2 = {
                "name":"newName2",
                "mail":"new2@mail.at",
                "password":"newPassword2",
                "username":"newUsername2"
        }
        url = '/user'
        response = self.app.post(url, json=data)
        self.assertEqual(response.status_code,201)
        
        response = self.app.post(url, json=data2)
        self.assertEqual(response.status_code,201)

 
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        #get existing user id
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/users'
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json),4)
        user_id = response.json[2]["userID"]

        data = {
                'userID':user_id,
                "name":"editname",
                "mail":"mailedit@mail.com",
                "password":"editpassword",
                "username":"editusername"
        }
        url = '/user'
        response = self.app.put(url, json=data, headers=headers)
        
        self.assertEqual(response.status_code,406)

    #test update user as admin
    def test_updateUser_Admin(self):
        self.test_createUser()
        #create random user
        #login as admin
        userAndPass = b64encode(b"adminUsername:adminPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        #get existing user id
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/users'
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json),2)
        user_id = response.json[1]["userID"]

        data = {
                'userID':user_id,
                "name":"editname",
                "mail":"edit@mail.com",
                "password":"editpassword",
                "username":"editusername"
        }
        url = '/user'
        response = self.app.put(url, json=data, headers=headers)
        
        self.assertEqual(response.status_code,200)

        #get user to check if update was successful
        url = '/user/'+user_id
        response = self.app.get(url, headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["name"],"editname")

    #upodate user as admin wih existing username
    def test_updateUser_Admin_ExistingUsername(self):
        #create random user
        self.test_createUser()
        #login as admin
        userAndPass = b64encode(b"adminUsername:adminPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        #get existing user id
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/users'
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json),2)
        user_id = response.json[1]["userID"]

        data = {
                'userID':user_id,
                "name":"editname",
                "mail":"florian@mail.com",
                "password":"editpassword",
                "username":"adminUsername"
        }
        url = '/user'
        response = self.app.put(url, json=data, headers=headers)
        
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json['message'],"Username already in use!")

    #upodate user as admin wih existing mail
    def test_updateUser_Admin_ExistingMail(self):
        #create random user
        self.test_createUser()
        #login as admin
        userAndPass = b64encode(b"adminUsername:adminPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        #get existing user id
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/users'
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json),2)
        user_id = response.json[1]["userID"]

        data = {
                'userID':user_id,
                "name":"editname",
                "mail":"admin@mail.com",
                "password":"editpassword",
                "username":"editusername"
        }
        url = '/user'
        response = self.app.put(url, json=data, headers=headers)
        
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json['message'],"Mail already in use!")


    def test_deleteUser(self):
        self.test_createUser()
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        #get existing user id
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/users'
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json),2)
        user_id = response.json[1]["userID"]

        data={
            "userID":user_id
        }

        url = '/user'
        response = self.app.delete(url, json=data, headers=headers)
        
        self.assertEqual(response.status_code,200)

        #get user to check if update was successful
        url = '/user/'+user_id
        response = self.app.get(url, headers=headers)
        self.assertEqual(response.status_code,404)

    def test_deleteUser_NotExisting(self):
        self.test_createUser()
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        data = {
                'userID':str(uuid.uuid4())
        }
        url = '/user'
        response = self.app.delete(url, json=data, headers=headers)
        
        self.assertEqual(response.status_code,404)

    def test_deleteUser_NotAuthorized(self):
        self.test_createUser()
        #create random user
        data = {
                "name":"newName",
                "mail":"new@mail.com", 
                "password":"newPassword",
                "username":"newUsername"
        }
        data2 = {
                "name":"newName2",
                "mail":"new2@mail.com",
                "password":"newPassword2",
                "username":"newUsername2"
        }
        url = '/user'
        response = self.app.post(url, json=data)
        self.assertEqual(response.status_code,201)
        
        response = self.app.post(url, json=data2)
        self.assertEqual(response.status_code,201)

 
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        #get existing user id
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/users'
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json),4)
        user_id = response.json[2]["userID"]

        data = {
                'userID':user_id
        }
        url = '/user'
        response = self.app.delete(url, json=data, headers=headers)
        
        self.assertEqual(response.status_code,406)

    def test_deleteUser_Admin(self):
        self.test_createUser()
        
        #login as admin
        userAndPass = b64encode(b"adminUsername:adminPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        #get existing user id
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/users'
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json),2)
        user_id = response.json[1]["userID"]

        data = {
                'userID':user_id
        }
        url = '/user'
        response = self.app.delete(url, json=data, headers=headers)
        
        self.assertEqual(response.status_code,200)

        #get user to check if update was successful
        url = '/user/'+user_id
        response = self.app.get(url, headers=headers)
        self.assertEqual(response.status_code,404)

    #Test get users
    def test_getUsers(self):
        self.test_createUser()
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        #log response
        app.logger.debug(response.json)
        authToken = response.json["authToken"]


        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/users'
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json),2)

    def test_getUsers_NotAuthorized(self):
        
        self.test_createUser()
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        #log response
        app.logger.debug(response.json)
        authToken = response.json["authToken"]


        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/users'
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json),2)    
    
    #test change user to admin
    def test_changeUserToAdmin(self):
        self.test_createUser()
        userAndPass = b64encode(b"adminUsername:adminPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        #get existing user id
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/users'
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json),2)
        user_id = response.json[1]["userID"]


        url = '/user/admin/'+user_id
        response = self.app.put(url, headers=headers)
        
        self.assertEqual(response.status_code,200)

        #get user to check if update was successful
        url = '/user/'+user_id
        response = self.app.get(url, headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["isAdmin"],True)



    def test_changeUserToAdmin_NotAuthorized(self):
        self.test_createUser()
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        #get existing user id
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/users'
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json),2)
        user_id = response.json[1]["userID"]


        url = '/user/admin/'+user_id
        response = self.app.put(url, headers=headers)
        
        self.assertEqual(response.status_code,406)
        
        #get user to check if update was successful
        url = '/user/'+user_id
        response = self.app.get(url, headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["isAdmin"],False)

    #change user to amdin user not found
    def test_changeUserToAdmin_UserNotFound(self):
        self.test_createUser()
        userAndPass = b64encode(b"adminUsername:adminPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        #get existing user id
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/user/admin/'+str(uuid.uuid4())
        response = self.app.put(url, headers=headers)
        
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"The user to be updated is not found")

       

    #test change user to teacher
    def test_changeUserToTeacher(self):
        self.test_createUser()
        userAndPass = b64encode(b"adminUsername:adminPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        #get existing user id
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/users'
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json),2)
        user_id = response.json[1]["userID"]


        url = '/user/teacher/'+user_id
        response = self.app.put(url, headers=headers)
        
        self.assertEqual(response.status_code,200)

        #get user to check if update was successful
        url = '/user/'+user_id
        response = self.app.get(url, headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["isTeacher"],True)

    #test change user to teacher not authorized
    def test_changeUserToTeacher_NotAuthorized(self):
        self.test_createUser()
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        #get existing user id
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/users'
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(len(response.json),2)
        user_id = response.json[1]["userID"]


        url = '/user/teacher/'+user_id
        response = self.app.put(url, headers=headers)
        
        self.assertEqual(response.status_code,406)
        
        #get user to check if update was successful
        url = '/user/'+user_id
        response = self.app.get(url, headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["isTeacher"],False)
    
    #change user to teacher user not found
    def test_changeUserToTeacher_UserNotFound(self):
        self.test_createUser()
        userAndPass = b64encode(b"adminUsername:adminPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/user/teacher/'+str(uuid.uuid4())
        response = self.app.put(url, headers=headers)
        
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"The user to be updated is not found")

class LoginLogoutTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        # DB Einrichten
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
        #Create User
        UserEndpointTest.test_createUser(self)


    def tearDown(self) -> None:
        return super().tearDown()

    def test_login_username(self):
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)

        self.assertEqual(response.status_code,200)
        self.assertEqual(b"authToken" in response.data,True)

    def test_login_email(self):
        userAndPass = b64encode(b"florian@mail.com:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)

        self.assertEqual(response.status_code,200)
        self.assertEqual(b"authToken" in response.data,True)

    def test_wrongPW(self):
        userAndPass = b64encode(b"floreian:supersafed").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)

        self.assertEqual(response.status_code,401)
        self.assertEqual(response.json["message"],"Email or password wrong!")

    def test_wrongUsername(self):
        userAndPass = b64encode(b"floreiandd:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)

        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"There is no user account with this Username/E-Mail and password combination")

    def test_wrongMail(self):
        userAndPass = b64encode(b"florian@mail.coms:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)

        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"There is no user account with this Username/E-Mail and password combination")

    #test logout
    def test_logout(self):
        userAndPass = b64encode(b"florian@mail.com:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)

        self.assertEqual(response.status_code,200)
        #get authToken
        authToken = response.json["authToken"]
        #logout
        url = '/logout'
        headers = {
            'authToken': authToken
        }
        response = self.app.get(url, headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["message"],"Logout successful!")

    #test invalid authToken
    def test_invalidAuthToken(self):
        
        #create Page
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': "invalidToken"
        }
        data = {
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test"
        }
        url = '/page'

        response = self.app.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code,403)
        self.assertEqual(response.json["message"],"Token is invalid!")
       

class PWresteTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        # DB Einrichten
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
        #Create User
        UserEndpointTest.test_createUser(self)


    def tearDown(self) -> None:
        return super().tearDown()

    def test_loginBeforeReset(self):
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)

        self.assertEqual(response.status_code,200)
        self.assertEqual(b"authToken" in response.data,True)

    def test_resetPW(self):
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype
        }
        data = {
                
                "login":"floreian"
        }
        url = '/resetpassword'

        response = self.app.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["message"],"Email sent")

    def test_loginAfterReset(self):
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)

        self.assertEqual(response.status_code,200)
        self.assertEqual(b"authToken" in response.data,True)

    def test_resetPWWrongLogin(self):
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype
        }
        data = {
                
                "login":"floreiandd"
        }
        url = '/resetpassword'

        response = self.app.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"There is no user account for the entered email address or username!")


#test Pages
class PagesTest(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        # DB Einrichten
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
        #Create User
        UserEndpointTest.test_createUser(self)
        #Create random user
        rand =  User("randName","randUsername","rand@mail.com",generate_password_hash("randPW"))
        db.session.add(rand)
        #add admin user
        admin =  User("adminName","adminUsername","admin@mail.com",generate_password_hash("adminPW"))
        admin.isAdmin = True
        db.session.add(admin)
#  INS-BEG-FPI-20231011
        #add page
        page = Page("name","test","das ist mein Link")
        access = Access(1,page.pageID,rand.userID)
        db.session.add(page)
        db.session.add(access)
#  INS-END-FPI-20231011
        db.session.commit()
        

    def tearDown(self) -> None:
        return super().tearDown()

    #test create Page
    def test_createPage(self):
        #get AuthToken
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)



        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': response.json["authToken"]
        }
        data = {
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test"
        }
        url = '/page'

        response = self.app.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json["message"],"Page created")

    def test_createPage_noAuth(self):
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype
        }
        data = {
                
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test"
        }
        url = '/page'

        response = self.app.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code,401)
        self.assertEqual(response.json["message"],"Token is missing!")

    def test_createPage_noName(self):
        #get AuthToken
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': response.json["authToken"]
        }
        data = {
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test"
        }
        url = '/page'

        response = self.app.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"Missing name")

    

    def test_createPage_noImgLink(self):
        #get AuthToken
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': response.json["authToken"]
        }
        data = {
                "name":"name",
                "content":"test",
                "description":"test"
        }
        url = '/page'

        response = self.app.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"Missing imgLink")

    def test_createPage_noDescription(self):
        #get AuthToken
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        data = {
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link"
        }
        url = '/page'

        response = self.app.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"Missing description")

    #create page with accesslist
    def test_createPage_withAccessList(self):
        #get AuthToken
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        #get userID from adminUsername
        user = User.query.filter_by(username="adminUsername").first()

        data = {
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test",
                "accessList":[{"userID": user.userID, "accessLvl": "1"}]
        }
        url = '/page'

        response = self.app.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json["message"],"Page created")

    #test create page with accesslist but no accesslvl
    def test_createPage_withAccessList_noAccessLvl(self):
        #get AuthToken
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        #get userID from adminUsername
        user = User.query.filter_by(username="adminUsername").first()

        data = {
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test",
                "accessList":[{"userID": user.userID}]
        }
        url = '/page'

        response = self.app.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"Missing accessLvl")

    #test create page with accesslist but no userID
    def test_createPage_withAccessList_noUserID(self):
        #get AuthToken
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        data = {
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test",
                "accessList":[{"accessLvl": "1"}]
        }
        url = '/page'

        response = self.app.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"Missing userID")

    # test create page with access list but not existing userID
    def test_createPage_withAccessList_notExistingUserID(self):
        #get AuthToken
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        data = {
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test",
                "accessList":
                [
                    {
                        "userID": str(uuid.uuid4()), 
                        "accessLvl": "1"
                    }
                ]
        }
        url = '/page'

        response = self.app.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"User not found!")

    #test get all Pages
    def test_getAllPages(self):
        #get AuthToken
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        #create Page
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': response.json["authToken"]
        }
        data = {
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test"
        }
        url = '/page'

        response = self.app.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json["message"],"Page created")
        response = self.app.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json["message"],"Page created")
        response = self.app.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json["message"],"Page created")
        
        
        url = '/pages'
        response = self.app.get(url, headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json[0]['name'],'name')

    def test_getPage(self):
        #get AuthToken
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createPage()
        self.test_createPage()
        self.test_createPage()

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)


        url = '/page/'+response.json[0]["pageID"]
        response = self.app.get(url, headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["name"],'name')

        response = self.app.get(url, headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["name"],"name")
        self.assertEqual(response.json["imgLink"],"das ist mein Link")
        self.assertEqual(response.json["description"],"test")

    
    def test_getPage_noPageID(self):
        #get AuthToken
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createPage()
        self.test_createPage()
        self.test_createPage()

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }


        url = '/page/'+str(uuid.uuid4())
        response = self.app.get(url, headers=headers)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"Page not found!")

    #test update Page as Owner
    def test_updatePage_asOwner(self):
        #get AuthToken
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createPage()
        self.test_createPage()
        self.test_createPage()

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]

        #get user id of existing user
        url = '/users'
        response = self.app.get(url, headers=headers)
        userID = response.json[1]["userID"]

        url = '/page'
        data = {
                "pageID": pageID,
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test",
                "accessList":
                [
                    {"userID":userID,"accessLvl":1}
                ]
        }
        
        response = self.app.put(url, json=data, headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["message"],"Page updated!")

    #test update Page as Admin
    def test_updatePage_asAdmin(self):
        #get AuthToken
        userAndPass = b64encode(b"adminUsername:adminPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createPage()
        self.test_createPage()
        self.test_createPage()

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]

        #get user id of existing user
        url = '/users'
        response = self.app.get(url, headers=headers)
        userID = response.json[1]["userID"]

        url = '/page'
        data = {
                "pageID": pageID,
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test",
                "accessList":
                [
                    {"userID":userID,"accessLvl":1}
                ]
        }
        
        response = self.app.put(url, json=data, headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["message"],"Page updated!")

    #test update Page as write authorized user
    def _test_updatePage_asWriteAuthorizedUser(self):
        #Create Page as User with write access for another user
        #get AuthToken
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        #get user by username randName
        url = '/user/username/randName'
        response = self.app.get(url, headers=headers)
        userID = response.json["userID"]
        #create Page
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        data = {
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test",
                "accessList": [
                    {"userID":userID,"accessLvl":1}
                ]
        }
        url = '/page'

        response = self.app.post(url, json=data, headers=headers)
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json["message"],"Page created")


        #Login as user with write access
        userAndPass = b64encode(b"randName:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]



        url = '/page'
        data = {
                "pageID": pageID,
                "name":"changedname",
        }
        
        response = self.app.put(url, json=data, headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["message"],"Page updated!")

        #test if page was updated
        url = '/page/'+str(pageID)
        response = self.app.get(url, headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["name"],"changedname")
    
    #test update Page with invalid pageid
    def test_updatePage_invalidPageID(self):
        #get AuthToken
        userAndPass = b64encode(b"adminUsername:adminPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createPage()
        self.test_createPage()
        self.test_createPage()

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        

        #get user id of existing user
        url = '/users'
        response = self.app.get(url, headers=headers)
        userID = response.json[1]["userID"]

        url = '/page'
        data = {
                "pageID": str(uuid.uuid4()),
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test",
                "accessList":
                [
                    {"userID":userID,"accessLvl":1}
                ]
        }
        
        response = self.app.put(url, json=data, headers=headers)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"Page not found!")

    #test update Page with unauthorized user
    def test_updatePage_unauthorizedUser(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createPage()
        self.test_createPage()
        self.test_createPage()

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]

        #get user id of existing user
        url = '/users'
        response = self.app.get(url, headers=headers)
        userID = response.json[1]["userID"] 

        url = '/page'
        data = {
                "pageID": pageID,
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test",
                "accessList":
                [
                    {"userID":userID,"accessLvl":1}
                ]
        }
        
        response = self.app.put(url, json=data, headers=headers)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"You are not allowed to update the page")


    #update Page with accesslist with invalid user
    def test_updatePage_invalidUser(self):
        #get AuthToken
        userAndPass = b64encode(b"adminUsername:adminPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createPage()
        self.test_createPage()
        self.test_createPage()

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]

        #get user id of existing user
       

        url = '/page'
        data = {
                "pageID": pageID,
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test",
                "accessList":
                [
                    {"userID":str(uuid.uuid4()),"accessLvl":1}
                ]
        }
        
        response = self.app.put(url, json=data, headers=headers)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"User for Access not found!")

    #test update Page with invalid accesslvl
    def test_updatePage_invalidAccessLvl(self):
        #get AuthToken
        userAndPass = b64encode(b"adminUsername:adminPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createPage()
        self.test_createPage()
        self.test_createPage()

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]

        #get user id of existing user
        url = '/users'
        response = self.app.get(url, headers=headers)
        userID = response.json[1]["userID"]

        url = '/page'
        data = {
                "pageID": pageID,
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test",
                "accessList":
                [
                    {"userID":userID,"accessLvl":5}
                ]
        }
        
        response = self.app.put(url, json=data, headers=headers)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"Invalid accessLvl")

    #test update Page with accesslist with missing user
    def test_updatePage_missingUser(self):
        #get AuthToken
        userAndPass = b64encode(b"adminUsername:adminPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createPage()
        self.test_createPage()
        self.test_createPage()

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]

        #get user id of existing user
        url = '/users'
        response = self.app.get(url, headers=headers)
        userID = response.json[1]["userID"]

        url = '/page'
        data = {
                "pageID": pageID,
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test",
                "accessList":
                [
                    {"accessLvl":1}
                ]
        }
        
        response = self.app.put(url, json=data, headers=headers)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"Missing userID")

    #test update Page with accesslist with missing accesslvl
    def test_updatePage_missingAccessLvl(self):
        #get AuthToken
        userAndPass = b64encode(b"adminUsername:adminPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createPage()
        self.test_createPage()
        self.test_createPage()

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]

        #get user id of existing user
        url = '/users'
        response = self.app.get(url, headers=headers)
        userID = response.json[1]["userID"]

        url = '/page'
        data = {
                "pageID": pageID,
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test",
                "accessList":
                [
                    {"userID":userID}
                ]
        }
        
        response = self.app.put(url, json=data, headers=headers)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"Missing accessLvl")


    #test update Page with accesslist where access already exists
    def test_updatePage_accessAlreadyExists(self):
        #get AuthToken
        userAndPass = b64encode(b"adminUsername:adminPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createPage()
        self.test_createPage()
        self.test_createPage()

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]

        #get user id of existing user
        url = '/users'
        response = self.app.get(url, headers=headers)
        userID = response.json[1]["userID"]

        url = '/page'
        data = {
                "pageID": pageID,
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test",
                "accessList":
                [
                    {"userID":userID,"accessLvl":1}
                ]
        }
        
        response = self.app.put(url, json=data, headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["message"],"Page updated!")

    
        data = {
                "pageID": pageID,
                "name":"name",
                "content":"test",
                "imgLink":"das ist mein Link",
                "description":"test",
                "accessList":
                [
                    {"userID":userID,"accessLvl":2}
                ]
        }
        response = self.app.put(url, json=data, headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["message"],"Page updated!")

    #Delete Page as Owner
    def test_deletePage_asOwner(self):
        #get AuthToken
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createPage()
        self.test_createPage()
        self.test_createPage()

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]

        url = '/page'
        data = {
                "pageID": pageID,
        }
        
        response = self.app.delete(url, json=data, headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["message"],"Page deleted!")


    #Delete Page as Admin
    def test_deletePage_asAdmin(self):
        #get AuthToken
        userAndPass = b64encode(b"adminUsername:adminPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createPage()
        self.test_createPage()
        self.test_createPage()

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]

        url = '/page'
        data = {
                "pageID": pageID,
        }
        
        response = self.app.delete(url, json=data, headers=headers)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["message"],"Page deleted!")

    #Delete Page as write authorized user
    def test_deletePage_asWriteAuthorizedUser(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        
 
        #log response to console


        #create Page
        self.test_createPage()
        self.test_createPage()
        self.test_createPage()

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console


        pageID = response.json[0]["pageID"]

        url = '/page'
        data = {
                "pageID": pageID,
        }
        
        response = self.app.delete(url, json=data, headers=headers)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"You are not allowed to delete the page")

    #Delete Page with invalid pageID
    def test_deletePage_invalidPageID(self):
        #get AuthToken
        userAndPass = b64encode(b"adminUsername:adminPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createPage()
        self.test_createPage()
        self.test_createPage()

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
       
        url = '/page'
        data = {
                "pageID": str(uuid.uuid4()),
        }
        
        response = self.app.delete(url, json=data, headers=headers)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"Page not found!")

#test Content
class TestContent(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        # DB Einrichten
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
        #Create User
        UserEndpointTest.test_createUser(self)
        #Create random user
        rand =  User("randName","randUsername","rand@mail.com",generate_password_hash("randPW"))
        db.session.add(rand)
        #add admin user
        admin =  User("adminName","adminUsername","admin@mail.com",generate_password_hash("adminPW"))
        admin.isAdmin = True
        db.session.add(admin)
        #add page
        page = Page("name","test","das ist mein Link")
        access = Access(2,page.pageID,rand.userID)
        db.session.add(page)
        db.session.add(access)
        # INS-BEG-FPI-20231011
        #get userid for username floreian
        user = User.query.filter_by(username="floreian").first()
        access1 = Access(1,page.pageID,user.userID)
        db.session.add(access1)
        page1 = Page("name2","test2","das ist mein Link2")
        db.session.add(page1)
        noauth =  User("noauthName","noauthUsername","noauth@mail.com",generate_password_hash("noauth"))
        db.session.add(noauth)
        #INS-END-FPI-20231011
        db.session.commit()

    
        
    def tearDown(self) -> None:
        return super().tearDown()

    #Create Content
    def test_createContent(self):
        #get AuthToken

        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        authToken = response.json["authToken"]
        #get Page id of existing page
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]
        #create Content
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        data = {
                "pageID":pageID,
                "content":"Das ist mein Content",
                "type":"type",
                "name":"Dasst ein Name",
        }
        url = '/content'

        response = self.app.post(url, json=data, headers=headers)
        #print(response.json)

        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json["message"],"Content created")

    #test create content without pageID
    def test_createContent_withoutPageID(self):
        #get AuthToken

        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        authToken = response.json["authToken"]
        #get Page id of existing page
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        data = {
                "content":"Das ist mein Content",
                "type":"type",
                "name":"Dasst ein Name",
        }
        url = '/content'

        response = self.app.post(url, json=data, headers=headers)
        #print(response.json)

        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"No pageID given!")

    #test create content without content
    def test_createContent_withoutContent(self):
        #get AuthToken

        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        authToken = response.json["authToken"]
        #get Page id of existing page
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]
        #create Content
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        data = {
                "pageID":pageID,
                "type":"type",
                "name":"Dasst ein Name",
        }
        url = '/content'

        response = self.app.post(url, json=data, headers=headers)
        #print(response.json)

        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"No content given!")

    #test create content without type
    def test_createContent_withoutType(self):
        #get AuthToken

        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        authToken = response.json["authToken"]
        #get Page id of existing page
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]
        #create Content
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        data = {
                "pageID":pageID,
                "content":"Das ist mein Content",
                "name":"Dasst ein Name",
        }
        url = '/content'

        response = self.app.post(url, json=data, headers=headers)
        #print(response.json)

        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"No type given!")

    #test create content without name
    def test_createContent_withoutName(self):
        #get AuthToken

        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        authToken = response.json["authToken"]
        #get Page id of existing page
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]
        #create Content
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        data = {
                "pageID":pageID,
                "content":"Das ist mein Content",
                "type":"type",
        }
        url = '/content'

        response = self.app.post(url, json=data, headers=headers)
        #print(response.json)

        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"No name given!")

    #test create content not allowed
    def test_createContent_notAllowed(self):
        #get AuthToken

        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        authToken = response.json["authToken"]
        #get Page id of existing page
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]
        #create Content
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        data = {
                "pageID":pageID,
                "content":"Das ist mein Content",
                "type":"type",
                "name":"Dasst ein Name",
        }
        url = '/content'

    

        response = self.app.post(url, json=data, headers=headers)


        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"You are not allowed to create the content")


    #Get page with content
    def test_getPage_withContent(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createContent()
        self.test_createContent()
        self.test_createContent()
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        

        pageID = response.json[0]["pageID"]

        url = '/page/'+str(pageID)+'/contents'
        #print(url)
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["contents"][0]["content"],"Das ist mein Content")
        self.assertEqual(len(response.json["contents"]),3)

    #get page with content with wrong pageID
    def test_getPage_withContent_wrongPageID(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createContent()
        self.test_createContent()
        self.test_createContent()
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page

        url = '/page/'+str(uuid.uuid4())+'/contents'
        
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"Page not found!")

    #get page with content unauthorized user
    def test_getPage_withContent_unauthorizedUser(self):
        #get AuthToken
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createContent()
        self.test_createContent()
        self.test_createContent()
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        
        pageID = response.json[0]["pageID"]
        # INS-BEG-FPI-20231011
        #login as unautorized user
        userAndPass = b64encode(b"noauthUsername:noauth").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        # INS-END-FPI-20231011

        url = '/page/'+str(pageID)+'/contents'
        #print(url)
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"You are not allowed to get the page")

    #get page with content no id
    def test_getPage_withContent_noID(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createContent()
        self.test_createContent()
        self.test_createContent()
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page

        url = '/page/contents'
        
        response = self.app.get(url, headers=headers)
        
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"Page not found!")
           
  
    #duplicate page with content
    def test_duplicatePage_withContent(self):    
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createContent()
        self.test_createContent()
        self.test_createContent()
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]

        data = {
            "pageID":pageID
        }

        url = '/page/duplicate'
        response = self.app.post(url,json=data, headers=headers)
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json["message"],"Page duplicated!")

        #check if page is duplicated
        url = '/pages'
        response = self.app.get(url, headers=headers)
        self.assertEqual(len(response.json),2)
        self.assertEqual(response.json[0]["pageID"],pageID)
        self.assertEqual(response.json[1]["name"],response.json[0]["name"])
        self.assertEqual(response.json[1]["imgLink"],response.json[0]["imgLink"])

    #test duplicate page without content
    def test_duplicatePage_withoutContent(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        #log response to console
        pageID = response.json[0]["pageID"]

        data = {
            "pageID":pageID
        }

        url = '/page/duplicate'
        response = self.app.post(url,json=data, headers=headers)
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json["message"],"Page duplicated!")

        #check if page is duplicated
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        self.assertEqual(len(response.json),2)
        self.assertEqual(response.json[0]["pageID"],pageID)
        self.assertEqual(response.json[1]["name"],response.json[0]["name"])
        self.assertEqual(response.json[1]["imgLink"],response.json[0]["imgLink"])

    #test duplicate page with wrong pageID
    def test_duplicatePage_wrongPageID(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        data = {
            "pageID":uuid.uuid4()
        }

        url = '/page/duplicate'
        response = self.app.post(url,json=data, headers=headers)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"Page not found!")

    #test duplicate page without authorization
    def test_duplicatePage_noAuth(self):
        #get AuthToken
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        #log response to console
        pageID = response.json[0]["pageID"]

        data = {
            "pageID":pageID
        }

        url = '/page/duplicate'
        response = self.app.post(url,json=data, headers=headers)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"You are not allowed to duplicate the page")

    #delte content
    def test_deleteContent(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createContent()
        self.test_createContent()
        self.test_createContent()
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]

        #get contentID
        url = '/page/'+str(pageID)+'/contents'
        response = self.app.get(url, headers=headers)
        contentID = response.json['contents'][0]["contentID"]
        self.assertEqual(len(response.json['contents']),3)

        data = {
            "contentID":contentID
        }

        url = '/content'
        response = self.app.delete(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["message"],"Content deleted")

        #check if content is deleted
        url = '/page/'+str(pageID)+'/contents'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        self.assertEqual(len(response.json['contents']),2)

    #test delete content with wrong contentID
    def test_deleteContent_wrongContentID(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createContent()
        self.test_createContent()
        self.test_createContent()
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        contentID = uuid.uuid4()

        data = {
            "contentID":contentID
        }

        url = '/content'
        response = self.app.delete(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"Content not found!")

    #test delete content without contentID
    def test_deleteContent_noContentID(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createContent()
        self.test_createContent()
        self.test_createContent()
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        data = {}

        url = '/content'
        response = self.app.delete(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"No contentID given!")


    #test delete content without allowed
    def test_deleteContent_noAllowed(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createContent()
        self.test_createContent()
        self.test_createContent()
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]

        #get contentID
        url = '/page/'+str(pageID)+'/contents'
        response = self.app.get(url, headers=headers)
        contentID = response.json['contents'][0]["contentID"]
        self.assertEqual(len(response.json['contents']),3)

        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        data = {
            "contentID":contentID
        }

        url = '/content'
        response = self.app.delete(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"You are not allowed to delete the content")

    #test update content
    def test_updateContent(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createContent()
        self.test_createContent()
        self.test_createContent()
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]

        #get contentID
        url = '/page/'+str(pageID)+'/contents'
        response = self.app.get(url, headers=headers)
        contentID = response.json['contents'][0]["contentID"]
        self.assertEqual(len(response.json['contents']),3)

        data = {
            "contentID":contentID,
            "content":"new content123",
            "type":"text123",
            "name":"new name123"
        }

        url = '/content'
        response = self.app.put(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["message"],"Content updated")

        #check if content is updated
        url = '/page/'+str(pageID)+'/contents'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        self.assertEqual(len(response.json['contents']),3)
        self.assertEqual(response.json['contents'][0]["content"],"new content123")
        self.assertEqual(response.json['contents'][0]["type"],"text123")
        self.assertEqual(response.json['contents'][0]["name"],"new name123")

    #test update content with wrong contentID
    def test_updateContent_wrongContentID(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createContent()
        self.test_createContent()
        self.test_createContent()
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        contentID = uuid.uuid4()

        data = {
            "contentID":contentID,
            "content":"new content123",
            "type":"text123",
            "name":"new name123"
        }

        url = '/content'
        response = self.app.put(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"Content not found!")

    #test update content without contentId
    def test_updateContent_noContentID(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createContent()
        self.test_createContent()
        self.test_createContent()
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        data = {
            "content":"new content123",
            "type":"text123",
            "name":"new name123"
        }

        url = '/content'
        response = self.app.put(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"No contentID given!")

    #test update content without access
    def test_updateContent_noAccess(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createContent()
        self.test_createContent()
        self.test_createContent()
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]

        #get contentID
        url = '/page/'+str(pageID)+'/contents'
        response = self.app.get(url, headers=headers)
        contentID = response.json['contents'][0]["contentID"]
        self.assertEqual(len(response.json['contents']),3)

        data = {
            "contentID":contentID,
            "content":"new content123",
            "type":"text123",
            "name":"new name123"
        }
        

        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/content'
        response = self.app.put(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"You are not allowed to update the content")

    #test duplicate content
    def test_duplicateContent(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createContent()
        self.test_createContent()
        self.test_createContent()
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]

        #get contentID
        url = '/page/'+str(pageID)+'/contents'
        response = self.app.get(url, headers=headers)
        contentID = response.json['contents'][0]["contentID"]
        self.assertEqual(len(response.json['contents']),3)

        data = {
            "contentID":contentID
        }

        url = '/content/duplicate'
        response = self.app.post(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["message"],"Content duplicated")

        #check if content is duplicated
        url = '/page/'+str(pageID)+'/contents'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        self.assertEqual(len(response.json['contents']),4)

    #test duplicate content with wrong contentID
    def test_duplicateContent_wrongContentID(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createContent()
        self.test_createContent()
        self.test_createContent()
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        contentID = uuid.uuid4()

        data = {
            "contentID":contentID
        }

        url = '/content/duplicate'
        response = self.app.post(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"Content not found!")

    #test duplicate content without contentID
    def test_duplicateContent_noContentID(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createContent()
        self.test_createContent()
        self.test_createContent()
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        data = {
        }

        url = '/content/duplicate'
        response = self.app.post(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"No contentID given!")

    # test duplicate content not allowed
    def test_duplicateContent_notAllowed(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        #create Page
        self.test_createContent()
        self.test_createContent()
        self.test_createContent()
        mimetype = 'application/json'
        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }
        #get Page id of existing page
        url = '/pages'
        response = self.app.get(url, headers=headers)
        #log response to console
        pageID = response.json[0]["pageID"]

        #get contentID
        url = '/page/'+str(pageID)+'/contents'
        response = self.app.get(url, headers=headers)
        contentID = response.json['contents'][0]["contentID"]
        self.assertEqual(len(response.json['contents']),3)

        data = {
            "contentID":contentID
        }

        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]

        headers = {
            'Content-Type': mimetype,
            'Accept': mimetype,
            'authToken': authToken
        }

        url = '/content/duplicate'
        response = self.app.post(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"You are not allowed to duplicate the content")

#Test Access
class TestAccess(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['DEBUG'] = False
        # DB Einrichten
        self.app = app.test_client()
        db.drop_all()
        db.create_all()
        #Create User
        UserEndpointTest.test_createUser(self)
        #Create random user
        rand =  User("randName","randUsername","rand@mail.com",generate_password_hash("randPW"))
        flo =  User("florian","flo","flo@mail.com",generate_password_hash("floPW"))
        db.session.add(rand)
        db.session.add(flo)
        #add admin user
        admin =  User("adminName","adminUsername","admin@mail.com",generate_password_hash("adminPW"))
        admin.isAdmin = True
        db.session.add(admin)
        #add page
        page = Page("name","test","das ist mein Link")
        access = Access(3,page.pageID,rand.userID)
        db.session.add(page)
        db.session.add(access)
        # INS-BEG-FPI-20231011
        #get userid for username floreian
        user = User.query.filter_by(username="floreian").first()
        access1 = Access(1,page.pageID,user.userID)
        db.session.add(access1)
        #INS-END-FPI-20231011
        db.session.commit()

    
        
    def tearDown(self) -> None:
        return super().tearDown()

    #test create access
    def test_createAccess(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        
        #get userID from username
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        
        url = '/users'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json[2]["username"],"flo")
        userID = response.json[2]["userID"]

        #get pageID
        url = '/pages'
        response = self.app.get(url, headers=headers)
        pageID = response.json[0]["pageID"]
        self.assertEqual(response.status_code,200)

        #create access
        data = {
            "userID":userID,
            "pageID":pageID,
            "accessLvl":2
        }
        url = '/access'
        response = self.app.post(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json["message"],"Access created")

        
    #test create access with wrong userID
    def test_createAccess_wrongUserID(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        
        #get userID from username
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        
        userID = uuid.uuid4()

        #get pageID
        url = '/pages'
        response = self.app.get(url, headers=headers)
        pageID = response.json[0]["pageID"]
        self.assertEqual(response.status_code,200)

        #create access
        data = {
            "userID":userID,
            "pageID":pageID,
            "accessLvl":2
        }
        url = '/access'
        response = self.app.post(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"User not found!")

        
    #test create access with wrong pageID
    def test_createAccess_wrongPageID(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        
        #get userID from username
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        
        url = '/users'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json[2]["username"],"flo")
        userID = response.json[2]["userID"]

        #get pageID
        pageID = uuid.uuid4()

        #create access
        data = {
            "userID":userID,
            "pageID":pageID,
            "accessLvl":2
        }
        url = '/access'
        response = self.app.post(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"Page not found!")

    #test create access with wrong accessLvl
    def test_createAccess_wrongAccessLvl(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        
        #get userID from username
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        
        url = '/users'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json[2]["username"],"flo")
        userID = response.json[2]["userID"]

        #get pageID
        url = '/pages'
        response = self.app.get(url, headers=headers)
        pageID = response.json[0]["pageID"]
        self.assertEqual(response.status_code,200)

        #create access
        data = {
            "userID":userID,
            "pageID":pageID,
            "accessLvl":5
        }
        url = '/access'
        response = self.app.post(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"Access level must be between 0 and 3")

    #test create access with no pageID
    def test_createAccess_noPageID(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        
        #get userID from username
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        
        url = '/users'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json[2]["username"],"flo")
        userID = response.json[2]["userID"]

        #create access
        data = {
            "userID":userID,
            "accessLvl":2
        }
        url = '/access'
        response = self.app.post(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"No pageID given!")

    #test create access with no userID
    def test_createAccess_noUserID(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        
        #get userID from username
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        
        #get pageID
        url = '/pages'
        response = self.app.get(url, headers=headers)
        pageID = response.json[0]["pageID"]
        self.assertEqual(response.status_code,200)

        #create access
        data = {
            "pageID":pageID,
            "accessLvl":2
        }
        url = '/access'
        response = self.app.post(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"No userID given!")

    #test create access with no accessLvl
    def test_createAccess_noAccessLvl(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        
        #get userID from username
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        
        url = '/users'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json[2]["username"],"flo")
        userID = response.json[2]["userID"]

        #get pageID
        url = '/pages'
        response = self.app.get(url, headers=headers)
        pageID = response.json[0]["pageID"]
        self.assertEqual(response.status_code,200)

        #create access
        data = {
            "userID":userID,
            "pageID":pageID,
        }
        url = '/access'
        response = self.app.post(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"No accessLvl given!")

    #test create access with no authorization to create access
    def test_createAccess_noAuth(self):
        #get AuthToken
        userAndPass = b64encode(b"floreian:supersafe").decode("ascii") #floreian:supersafe changed to randUsername:randPW
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        
        #get userID from username
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        
        url = '/users'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json[2]["username"],"flo")
        userID = response.json[2]["userID"]

        #get pageID
        url = '/pages'
        response = self.app.get(url, headers=headers)
        pageID = response.json[0]["pageID"]
        self.assertEqual(response.status_code,200)

        #create access
        data = {
            "userID":userID,
            "pageID":pageID,
            "accessLvl":2
        }
        url = '/access'
        response = self.app.post(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"You are not allowed to create the access")
    
    #test to create access that already exists
    def test_createAccess_alreadyExists(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        
        #get userID from username
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        
        url = '/users'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json[2]["username"],"flo")
        userID = response.json[2]["userID"]

        #get pageID
        url = '/pages'
        response = self.app.get(url, headers=headers)
        pageID = response.json[0]["pageID"]
        self.assertEqual(response.status_code,200)

        #create access
        data = {
            "userID":userID,
            "pageID":pageID,
            "accessLvl":2
        }
        url = '/access'
        response = self.app.post(url,json=data, headers=headers)
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json["message"],"Access created")

        data = {
            "userID":userID,
            "pageID":pageID,
            "accessLvl":1
        }
        response = self.app.post(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json["message"],"Access created")



    #test delete access
    def test_deleteAccess(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        
        #get userID from username
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        
        url = '/users'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json[2]["username"],"flo")
        userID = response.json[2]["userID"]

        #get pageID
        url = '/pages'
        response = self.app.get(url, headers=headers)
        pageID = response.json[0]["pageID"]
        self.assertEqual(response.status_code,200)

        #create access
        data = {
            "userID":userID,
            "pageID":pageID,
            "accessLvl":2
        }
        url = '/access'
        response = self.app.post(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json["message"],"Access created")

        #delete access
        url = '/access'
        response = self.app.delete(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["message"],"Access deleted")

    #test delete access with wrong userID
    def test_deleteAccess_wrongUserID(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        
        #get userID from username
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        
        userID = uuid.uuid4()

        #get pageID
        url = '/pages'
        response = self.app.get(url, headers=headers)
        pageID = response.json[0]["pageID"]
        self.assertEqual(response.status_code,200)

        #create access
        data = {
            "userID":userID,
            "pageID":pageID,
            "accessLvl":2
        }
        url = '/access'
        response = self.app.post(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"User not found!")

        #delete access
        url = '/access'
        response = self.app.delete(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"User not found!")

    #test delete access with wrong pageID
    def test_deleteAccess_wrongPageID(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        
        #get userID from username
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        
        url = '/users'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json[2]["username"],"flo")
        userID = response.json[2]["userID"]

        #get pageID
        pageID = uuid.uuid4()

        #create access
        data = {
            "userID":userID,
            "pageID":pageID,
            "accessLvl":2
        }
        url = '/access'
        response = self.app.post(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"Page not found!")

        #delete access
        url = '/access'
        response = self.app.delete(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"Page not found!")

    #test delete access without pageID
    def test_deleteAccess_noPageID(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        
        #get userID from username
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        
        url = '/users'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json[2]["username"],"flo")
        userID = response.json[2]["userID"]

        #get pageID
        url = '/pages'
        response = self.app.get(url, headers=headers)
        pageID = response.json[0]["pageID"]
        self.assertEqual(response.status_code,200)

        #create access
        data = {
            "userID":userID,
            "pageID":pageID,
            "accessLvl":2
        }
        url = '/access'
        response = self.app.post(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json["message"],"Access created")

        data = {
            "userID":userID
        }
        #delete access
        url = '/access'
        response = self.app.delete(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"No pageID given!")

    #test delete access without userID
    def test_deleteAccess_noUserID(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        
        #get userID from username
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        
        url = '/users'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json[2]["username"],"flo")
        userID = response.json[2]["userID"]

        #get pageID
        url = '/pages'
        response = self.app.get(url, headers=headers)
        pageID = response.json[0]["pageID"]
        self.assertEqual(response.status_code,200)

        #create access
        data = {
            "userID":userID,
            "pageID":pageID,
            "accessLvl":2
        }
        url = '/access'
        response = self.app.post(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json["message"],"Access created")

        data = {
            "pageID":pageID
            
        }
        #delete access
        url = '/access'
        response = self.app.delete(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"No userID given!")

        #delete access withcout access
    def test_deleteAccess_noAccess(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        
        #get userID from username
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        
        url = '/users'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json[2]["username"],"flo")
        userID = response.json[2]["userID"]

        #get pageID
        url = '/pages'
        response = self.app.get(url, headers=headers)
        pageID = response.json[0]["pageID"]
        self.assertEqual(response.status_code,200)

        #create access
        data = {
            "userID":userID,
            "pageID":pageID,
            "accessLvl":2
        }
        url = '/access'
        response = self.app.post(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,201)
        self.assertEqual(response.json["message"],"Access created")

        userAndPass = b64encode(b"floreian:supersafe").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        
        #get userID from username
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }

        #delete access
        url = '/access'
        response = self.app.delete(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,406)
        self.assertEqual(response.json["message"],"You are not allowed to delete the access")

    #test delete non existing access
    def test_deleteAccess_nonExisting(self):
        #get AuthToken
        userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
        headers = { 'Authorization' : 'Basic %s' %  userAndPass }
        url = '/login'
        response = self.app.get(url, headers=headers)
        authToken = response.json["authToken"]
        
        #get userID from username
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'authToken': authToken
        }
        
        url = '/users'
        response = self.app.get(url, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json[2]["username"],"flo")
        userID = response.json[2]["userID"]

        #get pageID
        url = '/pages'
        response = self.app.get(url, headers=headers)
        pageID = response.json[0]["pageID"]
        self.assertEqual(response.status_code,200)

        data = {
            "userID":userID,
            "pageID":pageID
        }
        #delete access
        url = '/access'
        response = self.app.delete(url,json=data, headers=headers)
        #print(response.json)
        self.assertEqual(response.status_code,404)
        self.assertEqual(response.json["message"],"Access not found!")

    #test update access for specific page
    #TODO: test update access for specific page
    # def test_updateAccess(self):
    #     #get AuthToken
    #     userAndPass = b64encode(b"randUsername:randPW").decode("ascii")
    #     headers = { 'Authorization' : 'Basic %s' %  userAndPass }
    #     url = '/login'
    #     response = self.app.get(url, headers=headers)
    #     authToken = response.json["authToken"]
        
    #     #get userID from username
    #     headers = {
    #         'Content-Type': 'application/json',
    #         'Accept': 'application/json',
    #         'authToken': authToken
    #     }
        
    #     url = '/users'
    #     response = self.app.get(url, headers=headers)
    #     #print(response.json)
    #     self.assertEqual(response.status_code,200)
    #     self.assertEqual(response.json[3]["username"],"teacher1")
    #     userID = response.json[3]["userID"]

    #     #get pageID
    #     url = '/pages'
    #     response = self.app.get(url, headers=headers)
    #     pageID = response.json[0]["pageID"]
    #     self.assertEqual(response.status_code,200)

    #     #create access
    #     data = {
    #         "userID":userID,
    #         "pageID":pageID,
    #         "accessLvl":2
    #     }
    #     url = '/access'
    #     response = self.app.post(url,json=data, headers=headers)
    #     #print(response.json)
    #     self.assertEqual(response.status_code,201)
    #     self.assertEqual(response.json["message"],"Access created")

    #     data = {
    #         "userID":userID,
    #         "pageID":pageID,
    #         "accessLvl":3
    #     }
    #     #update access
    #     url = '/access'
    #     response = self.app.put(url,json=data, headers=headers)
    #     #print(response.json)
    #     self.assertEqual(response.status_code,200)
    #     self.assertEqual(response.json["message"],"Access updated")

        #update access without userID

# Healthcheck test
class HealthcheckTest(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_healthcheck(self):
        response = self.app.get('/healthcheck')
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json["databaseStatus"],"available")


if __name__ == "__main__":
    unittest.main()