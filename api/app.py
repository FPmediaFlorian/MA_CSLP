from dataclasses import fields
from distutils.dep_util import newer_group
from enum import unique
from hashlib import new
import json

from flask import Flask,request, jsonify,make_response
from flask_cors import CORS,cross_origin
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from logging.config import fileConfig
from functools import wraps
from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash, check_password_hash
import os,uuid, re, jwt, requests, string, random



from os import path
log_file_path = path.join(path.dirname(path.abspath(__file__)), 'logging.cfg')

basedir = os.path.abspath(os.path.dirname(__file__))

## Init app



##Logging
fileConfig(log_file_path)
#logging.basicConfig(level=logging.DEBUG)
#logging.basicConfig(filename='backend.log', filemode='w', level=logging.DEBUG)

##Config
app = Flask(__name__)
app.config['JWT_SECRET_KEY'] = "mysupersecretkey"
# CORS(app,resources={r"/api": {"origins": "*"}})
CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir,'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)



###
# DATABASE 
###

class Page(db.Model):
    __tablename__="page"
    pageID = db.Column(db.String(38), primary_key=True) #UUID
    name = db.Column(db.String(100))
    imgLink = db.Column(db.String(100))
    description = db.Column(db.String(400))
    contents = db.relationship("Content",back_populates="page")
    access = db.relationship("Access")

    def __init__(self,name,imgLink,description):
        self.pageID = str(uuid.uuid4())
        self.name = name
        self.imgLink = imgLink
        self.description = description

class Content(db.Model):
    __tablename__="content"
    contentID = db.Column(db.String(38), primary_key=True) #UUID
    name = db.Column(db.String(100))
    type = db.Column(db.String(100))
    content = db.Column(db.String(10000))
    pageID = db.Column(db.String(38), db.ForeignKey("page.pageID"))
    page = db.relationship('Page',back_populates="contents")

    def __init__(self,name,type,content,pageID):
        self.contentID = str(uuid.uuid4())
        self.name = name
        self.type = type
        self.content = content
        self.pageID = pageID

class User(db.Model):
    userID = db.Column(db.String(38), primary_key=True) #UUID
    name = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)
    mail=db.Column(db.String(100),unique=True)
    pwHash = db.Column(db.String(100))
    isAdmin = db.Column(db.Boolean,default=False)
    isTeacher = db.Column(db.Boolean,default=False)
    access = db.relationship("Access")

    def __init__(self,name,username,mail,pwHash):
        self.userID= str(uuid.uuid4())
        self.name=name
        self.username = username
        self.mail=mail
        self.pwHash=pwHash
        self.isAdmin = False
        self.isTeacher = False

class Access(db.Model):
    __tablename__="access"
    accessID = db.Column(db.String(38), primary_key=True) 
    accessLvl= db.Column(db.Integer)
    #1 = read, 2accessLvl = write, 3 = owner

    pageID = db.Column(db.String(38), db.ForeignKey("page.pageID"))
    pages = db.relationship("Page", back_populates="access")
    userID = db.Column(db.String(38), db.ForeignKey("user.userID"))
    users = db.relationship("User", back_populates="access")

    def __init__(self,accessLvl,pageID,userID):
        self.accessID = str(uuid.uuid4())
        self.accessLvl = accessLvl
        self.pageID = pageID
        self.userID = userID
    

###
#Marschmallow Schemas
###

class ContentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Content
        load_instance = True

class PageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Page
        load_instance = True
    contents = ma.Nested("ContentSchema",many=True)
    
class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True

class AccessSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Access
        load_instance = True
        include_fk = True
    

user_schema = UserSchema()
users_schema = UserSchema(many=True)
page_schema = PageSchema()
pages_schema = PageSchema(many=True)
content_schema = ContentSchema()
contents_schema = ContentSchema(many=True)
access_schema = AccessSchema()
accesses_schema = AccessSchema(many=True)

###
# Tokencheck
###

def tokenCheck(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            token = request.headers['authToken']
        except Exception as e:
            return jsonify({'message':'Token is missing!'}),401
        try:
            data = jwt.decode(token, app.config['JWT_SECRET_KEY'],algorithms=['HS256'])
            app.logger.debug(data)
            currentUser = User.query.filter_by(userID=data['userid']).first()
        except Exception as e:
            return jsonify({'message':'Token is invalid!'}),403
        return f(currentUser, *args, **kwargs)
    return decorated

###
# Utilities
###

def get_random_string(length):
    # choose from all lowercase letter
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))
    return result_str



###
# Endponts
###

# Basic route to check if Service is running
@app.route('/')
@cross_origin(origin='*',headers=['content-type'])
def hello():
    return "application is up and running!",200

# Route to say hi to the frontend
@app.route('/hi', methods=['GET'])
@cross_origin(origin='*',headers=['content-type'])
def hi():
    return "Hello World from Backend",200

    
#Logger testing Endpoint
@app.route('/loggertest/', methods=['GET'])
@cross_origin(origin='*',headers=['content-type'])
def loggingTest():
    app.logger.debug('debug message')
    app.logger.info('info message')
    app.logger.warning('warn message')
    app.logger.error('error message')
    app.logger.critical('critical message')
    return "Logging Messages logged",200

@app.route('/cleaninstall', methods=['GET'])
@cross_origin(origin='*',headers=['content-type'])
def cleanInstall():
    db.drop_all()
    db.create_all()
    #insert user data from json
    with open('db_setup_dummydata/createUsers.json') as f:
        data = json.load(f)
        #print data to console


        for user in data['users']:
            #hash password
            #log password to console
            pwHash = generate_password_hash(user['password'], method = 'sha256')
            newUser = User(user['name'],user['username'],user['mail'],pwHash)
            newUser.isAdmin = user['isAdmin']
            newUser.isTeacher = user['isTeacher']
            db.session.add(newUser)
            db.session.commit()

    #insert pages with content from json
    with open('db_setup_dummydata/createPagesWithContent.json') as f:
        data = json.load(f)
        for page in data['pages']:
            newPage = Page(page['name'],page['imgLink'],page['description'])
            db.session.add(newPage)
            db.session.commit()
            for content in page['content']:
                newContent = Content(content['name'],content['type'],content['content'],newPage.pageID)
                db.session.add(newContent)
                db.session.commit()
            #insert access from json
            #create owner access
            #get userid by username
            user = User.query.filter_by(username=page['owner']).first()
            newAccess = Access(3,newPage.pageID,user.userID)
            db.session.add(newAccess)
            #create write access
            for username in page['writer']:
                user = User.query.filter_by(username=username).first()
                newAccess = Access(2,newPage.pageID,user.userID)
                db.session.add(newAccess)
            #create read access
            for username in page['reader']:
                user = User.query.filter_by(username=username).first()
                newAccess = Access(1,newPage.pageID,user.userID)
                db.session.add(newAccess)
            db.session.commit()


    return "Database was cleaned, recreated and filled with dummyData.",200

#Method to login suer end return accessToken
@app.route('/login')
@cross_origin(origin='*',headers=['content-type'])
def login():
    app.logger.debug("Request on /login")
    auth = request.authorization
    user = User.query.filter_by(mail=auth.username).first()
    if not user:
        user = User.query.filter_by(username=auth.username).first()
        if not user:
            return jsonify({'message':'There is no user account with this Username/E-Mail and password combination'}),404
    if auth and check_password_hash(user.pwHash, auth.password):
        token  = jwt.encode({'userid':str(user.userID), 'exp':datetime.utcnow() + timedelta(minutes=120)}, app.config['JWT_SECRET_KEY'])
        return jsonify({'authToken':token}) #token.decode('UTF-8')
    return jsonify({'message':'Email or password wrong!'}),401

#logout
@app.route('/logout')
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def logout(currentUser):
    app.logger.debug("Request on /logout")
    #delete token
    


    return jsonify({'message':'Logout successful!'}),200

#check token validity
@app.route('/checkToken')
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def checkToken(currentUser):
    app.logger.debug("Request on /checkToken")
    return jsonify({'message':'Token is valid!'}),200

#Method to reset password
@app.route('/resetpassword', methods=['POST'])
@cross_origin(origin='*',headers=['content-type'])
def resetpw():
    login = request.json["login"]
    user = User.query.filter_by(mail=login).first()
    if not user:
        user = User.query.filter_by(username=login).first()
        if not user:
            return jsonify({'message':'There is no user account for the entered email address or username!'}),404
    
    new_pw = get_random_string(random.randint(16,24))

    resp = requests.post(
		"https://api.mailgun.net/v3/sandbox2cb955efe954472ea8c6673c7bbb9e01.mailgun.org/messages",
		auth=("api", "95b2a71429a5cea58cca65024a9750ae-07e2c238-f120ca2a"),
		data={"from": "Mailgun Sandbox <postmaster@sandbox2cb955efe954472ea8c6673c7bbb9e01.mailgun.org>",
			"to": "Florian <learncs.ma@gmail.com>",
			"subject": "Hello Master",
			"template": "reset_password",
			"h:X-Mailgun-Variables": '{"name": "'+str(user.name)+'","password": "'+str(new_pw)+'"}'})

    #save pw to db
    pwHash = generate_password_hash(new_pw, method = 'sha256')
    user.pwHash=pwHash

    db.session.commit()

    if resp.status_code == 200:
        return jsonify({'message':'Email sent'}),200
    else :
        app.logger.error("Error while sending Mail: " + str(resp.content))
        return jsonify({'message': 'Error while sending mail'}),resp.status_code



#create User
@app.route('/user', methods=['POST'])
@cross_origin(origin='*',headers=['content-type'])
def createUser():
    #expectet json: {"name":"Florian","username":"florian","mail":"test@test.com","pwHash":"123456"}
    app.logger.info("Request on /user with POST")
    #print(request.json["name"])
    password = generate_password_hash(request.json["password"], method = 'sha256')
    try:
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if not (re.fullmatch(regex, request.json["mail"])):
            return jsonify({'message':'Not a valid email adress!'}),406
        #Check if Mail exists
        user = User.query.filter_by(mail=request.json["mail"]).first()#get('mail'=request.json["mail"])
        #print(user)
        if user:
            return jsonify({'message':'Email already in use!'}),406
        
        user1 = User.query.filter_by(username=request.json["username"]).first()#get('mail'=request.json["mail"])
        #print(user1)
        if user1:
            return jsonify({'message':'Username already in use!'}),406
        
        newUser = User(request.json["name"],request.json["username"],request.json["mail"],password)
        
        db.session.add(newUser)
        db.session.commit()

    except Exception as e:
        app.logger.error(e)
        return jsonify({'message':'Failed to save User!'}),406 #, 'error':e
    return jsonify({'message':'Success!'}),201

#delete User
@app.route('/user', methods=['DELETE'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def deleteUser(currentUser):
    app.logger.info("Request on /user with DELETE")

    #get userID from request
    userID_to_delete = request.json["userID"]
    user_to_delete = User.query.filter_by(userID=userID_to_delete).first()
    if not user_to_delete:
        return jsonify({'message':'User not found!'}),404
    if not (currentUser.isAdmin or user_to_delete == currentUser):
        return jsonify({'message':'You are not allowed to delete the user'}),406
    db.session.delete(user_to_delete)
    db.session.commit()
    return jsonify({'message':'User deleted!'}),200

#update User
@app.route('/user', methods=['PUT'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def updateUser(currentUser):
    #expected format: {"userID":1,"name":"Florian","username":"florian","mail":"mail","password":"pw"}
    app.logger.info("Request on /user with PUT")

    #check if userid exists in request
    if not "userID" in request.json:
        return jsonify({'message':'No userID in request!'}),406

    #get userID from request
    userID_to_update = request.json["userID"]
    user_to_update = User.query.filter_by(userID=userID_to_update).first()
    if not user_to_update:
        return jsonify({'message':'The user to be updated is not found'}),404
    if not (currentUser.isAdmin or user_to_update == currentUser):
        return jsonify({'message':'You are not allowed to update the user'}),406
    
   
    if "name" in request.json:
        user_to_update.name = request.json["name"]
    if "username" in request.json:
        #check if username stays the same
        if not (user_to_update.username == request.json["username"]):
            user1 = User.query.filter_by(username=request.json["username"]).first()
            if user1:
                return jsonify({'message':'Username already in use!'}),406
            user_to_update.username = request.json["username"]
        #check if username is already in use
        
    if "mail" in request.json:
        #check if mail stays the same
        if not (user_to_update.mail == request.json["mail"]):
            #check if mail is already in use
            user2 = User.query.filter_by(mail=request.json["mail"]).first()
            if user2:
                return jsonify({'message':'Mail already in use!'}),406
            user_to_update.mail = request.json["mail"]
    if "password" in request.json:
        password = generate_password_hash(request.json["password"], method = 'sha256')
        user_to_update.pwHash = password
    db.session.commit()
    return jsonify({'message':'User updated!'}),200

#set user is admin
@app.route('/user/admin/<id>', methods=['PUT'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def setUserAdmin(currentUser,id):
    app.logger.info("Request on /user/admin/<id> with PUT")
    if not currentUser.isAdmin:
        return jsonify({'message':'You are not allowed to change the admin status of a user'}),406
    user_to_update = User.query.filter_by(userID=id).first()
    if not user_to_update:
        return jsonify({'message':'The user to be updated is not found'}),404
    user_to_update.isAdmin = not user_to_update.isAdmin
    db.session.commit()
    return jsonify({'message':'User updated!'}),200

#set user is teacher
@app.route('/user/teacher/<id>', methods=['PUT'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def setUserTeacher(currentUser,id):
    app.logger.info("Request on /user/teacher/<id> with PUT")
    if not currentUser.isAdmin:
        return jsonify({'message':'You are not allowed to change the teacher status of a user'}),406
    user_to_update = User.query.filter_by(userID=id).first()
    if not user_to_update:
        return jsonify({'message':'The user to be updated is not found'}),404
    user_to_update.isTeacher = not user_to_update.isTeacher
    db.session.commit()
    return jsonify({'message':'User updated!'}),200

#get User
@app.route('/user/<id>', methods=['GET'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def getUser(currentUser,id):
    app.logger.info("Request on /user with GET")

    user = User.query.filter_by(userID=id).first()

    if not user:
        return jsonify({'message':'User not found!'}),404
    if not (currentUser.isAdmin or (user.userID == currentUser.userID)):
        return jsonify({'message':'You are not allowed to get the user'}),406
    return user_schema.jsonify(user)

#get current User
@app.route('/user', methods=['GET'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def getCurrentUser(currentUser):
    app.logger.info("Request on /user with GET")
    return user_schema.jsonify(currentUser)

#get user by username
@app.route('/user/username/<username>', methods=['GET'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def getUserByUsername(currentUser,username):
    app.logger.info("Request on /user/username/<username> with GET")
    
    #print(username)

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({'message':'User not found!'}),404
    if not (currentUser.isAdmin or (user.userID == currentUser.userID)):
        return jsonify({'message':'You are not allowed to get the user'}),406
    return user_schema.jsonify(user)

#retrieve all users
@app.route('/users', methods=['GET'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def getUsers(currentUser):
    app.logger.info("Request on /users with GET")
    all_users= User.query.all()
    return users_schema.jsonify(all_users),200 


#create a new Page
@app.route('/page', methods=['POST'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def createPage(currentUser):
    #expected json : {'name':'name','imgLink':'imgLink','description':'description'}
    app.logger.info("Request on /page with POST")
    try:
        #check if key exists in request json
        if "name" not in request.json:
            return jsonify({'message':'Missing name'}),406
        if "imgLink" not in request.json:
            return jsonify({'message':'Missing imgLink'}),406
        if "description" not in request.json:
            return jsonify({'message':'Missing description'}),406

        newPage = Page(request.json["name"],request.json["imgLink"],request.json["description"])
        if "accessList" in request.json:
            accessList = request.json["accessList"]
            for access in accessList:
                if "accessLvl" not in access:
                    return jsonify({'message':'Missing accessLvl'}),406
                if "userID" not in access:
                    return jsonify({'message':'Missing userID'}),406
                user = User.query.filter_by(userID=access["userID"]).first()
                if not user:
                    return jsonify({'message':'User not found!'}),404
                
                newAccess = Access(access["accessLvl"],newPage.pageID,access["userID"])
                db.session.add(newAccess)

        #add contents if exists
        if "contents" in request.json:
            contents = request.json["contents"]
            for content in contents:
                if "name" not in content:
                    return jsonify({'message':'Missing name'}),406
                if "content" not in content:
                    return jsonify({'message':'Missing content'}),406
                if "type" not in content:
                    return jsonify({'message':'Missing type'}),406
                #check if type is valid
                type = int(content["type"])
                if type < 0 or type > 4:
                    return jsonify({'message':'Invalid type'}),406
                newContent = Content(content["name"],type,content["content"],newPage.pageID)
                db.session.add(newContent)
                
        
        newAccess = Access(3,newPage.pageID,currentUser.userID)
        db.session.add(newPage)
        db.session.add(newAccess)
        db.session.commit()
        return jsonify({'message':'Page created'}),201
    except Exception as e:
        app.logger.error(e)
        return jsonify({'message':'Failed to save Page!'}),406


#delete Page
@app.route('/page', methods=['DELETE'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def deletePage(currentUser):
    app.logger.info("Request on /page with DELETE")
    token = request.headers.get('Authorization')
    #get userID from request
    pageID_to_delete = request.json["pageID"]
    page = Page.query.filter_by(pageID=pageID_to_delete).first()
    if not page:
        return jsonify({'message':'Page not found!'}),404
    #check if user is allowed to delete page
    #get information from Access table filter by pageID and userID
    access = Access.query.filter_by(pageID=pageID_to_delete,userID=currentUser.userID).first()
    if not ((access and access.accessLvl >2) or currentUser.isAdmin):
        return jsonify({'message':'You are not allowed to delete the page'}),406
    #delete all access entries for this page
    Access.query.filter_by(pageID=pageID_to_delete).delete()

    db.session.delete(page)
    db.session.commit()
    return jsonify({'message':'Page deleted!'}),200

#delte Page with id
@app.route('/page/<id>', methods=['DELETE'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def deletePageByID(currentUser,id):
    app.logger.info("Request on /page with DELETE")
    
    pageID_to_delete = id
    page = Page.query.filter_by(pageID=pageID_to_delete).first()
    if not page:
        return jsonify({'message':'Page not found!'}),404
    #check if user is allowed to delete page
    #get information from Access table filter by pageID and userID
    access = Access.query.filter_by(pageID=pageID_to_delete,userID=currentUser.userID).first()
    if not ((access and access.accessLvl >2) or currentUser.isAdmin):
        return jsonify({'message':'You are not allowed to delete the page'}),406
    #delete all access entries for this page
    Access.query.filter_by(pageID=pageID_to_delete).delete()
    db.session.delete(page)
    db.session.commit()
    return jsonify({'message':'Page deleted!'}),200

#update Page
@app.route('/page', methods=['PUT'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def updatePage(currentUser):
    #expected json: {"pageID":1,"name":"new title","accessList":"[{\"userID\":uuid,\"accessLvl\":1},{\"userID\":uuid,\"accessLvl\":2}]"}
    app.logger.info("Request on /page with PUT")

    pageID_to_update = request.json["pageID"]
    page = Page.query.filter_by(pageID=pageID_to_update).first()
    if not page:
        return jsonify({'message':'Page not found!'}),404
    #check if user is allowed to update page
    #get information from Access table filter by pageID and userID
    access = Access.query.filter_by(pageID=pageID_to_update,userID=currentUser.userID).first()
    if not ((access and access.accessLvl >1) or currentUser.isAdmin):
        return jsonify({'message':'You are not allowed to update the page'}),406
    #
    if "name" in request.json:
        page.name = request.json["name"]
    if "imgLink" in request.json:
        page.imgLink = request.json["imgLink"]
    if "description" in request.json:
        page.description = request.json["description"]
    if "accessList" in request.json:
        accessList = request.json["accessList"]
        
        for access in accessList:
            if "accessLvl" not in access:
                return jsonify({'message':'Missing accessLvl'}),406
            #test if accessLvl is valid
            if access["accessLvl"] not in [1,2,3]:  
                return jsonify({'message':'Invalid accessLvl'}),406
            if "userID" not in access:
                return jsonify({'message':'Missing userID'}),406
            user = User.query.filter_by(userID=access["userID"]).first()
            if not user:
                return jsonify({'message':'User for Access not found!'}),404
            accessinDB = Access.query.filter_by(pageID=pageID_to_update,userID=access["userID"]).first()
            if not accessinDB:
                newAccess = Access(access["accessLvl"],pageID_to_update,access["userID"])
                db.session.add(newAccess)
            else:
                accessinDB.accessLvl = access["accessLvl"]

    if "contents" in request.json:
        contents = request.json["contents"]
        #check if contents are deleted
        alreadyExistingContents =[]
        for content in contents:
            if "contentID" in content:
                alreadyExistingContents.append(content)

        for content in page.contents:
            #create subset of request contents with same contentID
            
            if content.contentID not in [content["contentID"] for content in alreadyExistingContents]:
                #log content deletion
                app.logger.info("Content deleted: "+str(content.contentID))
                db.session.delete(content)

        for content in contents:
            if "contentID" not in content:
                app.logger.info("Trying to create content: "+str(content))
                #create new content
                if "name" not in content:
                    return jsonify({'message':'Can not create new content: Missing name'}),406
                if "type" not in content:
                    return jsonify({'message':'Can not create new content: Missing type'}),406
                if "content" not in content:
                    return jsonify({'message':'Can not create new content: Missing content'}),406
                newContent = Content(content["name"],content["type"],content["content"],pageID_to_update)
                # log content creation
                app.logger.info("Content created: "+str(newContent.contentID))
                db.session.add(newContent)
            else:
                contentinDB = Content.query.filter_by(contentID=content["contentID"]).first()
                if not contentinDB:
                    return jsonify({'message':'Content not found!'}),404
                #log content update
                app.logger.info("Content updated: "+str(contentinDB.contentID))
                if "name" in content:
                    contentinDB.name = content["name"]
                if "content" in content:
                    contentinDB.content = content["content"]
                if "type" in content:
                    #check if type is valid
                    type = int(content["type"])
                    if type < 0 or type > 4:
                        return jsonify({'message':'Invalid type'}),406
                    contentinDB.type = type
            
        
    
    db.session.commit()
    return jsonify({'message':'Page updated!'}),200

#get Page
@app.route('/page/<id>', methods=['GET'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def getPage(currentUser,id):
    # app.logger.info("Request on /page with GET")

    # print("ID die im Backend ankommt: "+id)

    # if not id:
    #     return jsonify({'message':'No pageID given!'}),406

    # page = Page.query.filter_by(pageID=id).first()
    # if not page:
    #     return jsonify({'message':'Page not found!'}),404
    # #check if user is allowed to get page
    # #get information from Access table filter by pageID and userID
    # access = Access.query.filter_by(pageID=id,userID=currentUser.userID).first()
    # if not (access and access.accessLvl >=0) or currentUser.isAdmin:
    #     return jsonify({'message':'You are not allowed to get the page'}),406
    # return (page_schema.jsonify(page)),200
    return getPageContents(id)

#get page with contents
@app.route('/page/<id>/contents', methods=['GET'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck 
def getPageContents(currentUser,id):
    app.logger.info("Request on /page/<id>/contents with GET")

    #check if id is a valid uuid
    
    # if not id:
    #     return jsonify({'message':'No pageID given!'}),406
    page = Page.query.filter_by(pageID=id).first()
    if not page:
        return jsonify({'message':'Page not found!'}),404
    
    
    #check if user is allowed to get page
    #get information from Access table filter by pageID and userID
    access = Access.query.filter_by(pageID=id,userID=currentUser.userID).first()
    if not ((access and access.accessLvl >=0) or currentUser.isAdmin):
        return jsonify({'message':'You are not allowed to get the page'}),406
    #get all contents from page
    
    
    return (page_schema.jsonify(page)),200

#get all Pages
@app.route('/pages', methods=['GET'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def getAllPages(currentUser):
    app.logger.info("Request on /pages with GET")

    #check if current user is admin
    if  currentUser.isAdmin:
        pages = Page.query.all()
        return (pages_schema.jsonify(pages)),200


    #get all pages from db where user has access
    accesses = Access.query.filter_by(userID=currentUser.userID).all()
    pages = []
    for access in accesses:
        page = Page.query.filter_by(pageID=access.pageID).first()
        pages.append(page)
    return (pages_schema.jsonify(pages)),200
    

    #pages = Page.query.all()
    
    #return pages_schema.jsonify(pages),200

#create multiple pages
@app.route('/pages', methods=['POST'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def createPages(currentUser):
    #expected json: {"pages":[{"name":"test","imgLink":"test","description":"test","accessList":"[{\"userID\":uuid,\"accessLvl\":1},{\"userID\":uuid,\"accessLvl\":2}]"}]}
    app.logger.info("Request on /pages with POST")

    if "pages" not in request.json:
        return jsonify({'message':'Missing pages'}),406
    pages = request.json["pages"]
    for page in pages:
       
        if "name" not in page:
            return jsonify({'message':'Missing name'}),406
        if "imgLink" not in page:
            return jsonify({'message':'Missing imgLink'}),406
        if "description" not in page:
            return jsonify({'message':'Missing description'}),406
        newPage = Page(page["name"],page["imgLink"],page["description"])
        db.session.add(newPage)
        #add acces for current user
        newAccess = Access(3,newPage.pageID,currentUser.userID)
        db.session.add(newAccess)
        if "accessList" in page:
            accessList = page["accessList"]
            for access in accessList:
                if "accessLvl" not in access:
                    return jsonify({'message':'Missing accessLvl'}),406
                #test if accessLvl is valid
                if access["accessLvl"] not in [1,2,3]:  
                    return jsonify({'message':'Invalid accessLvl'}),406
                if "userID" not in access:
                    return jsonify({'message':'Missing userID'}),406
                user = User.query.filter_by(userID=access["userID"]).first()
                if not user:
                    return jsonify({'message':'User for Access not found!'}),404
                
                newAccess = Access(access["accessLvl"],newPage.pageID,access["userID"])
        db.session.commit()

        
    return jsonify({'message':'Pages created!'}),200

#duplicate Page
@app.route('/page/duplicate', methods=['POST'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def duplicatePage(currentUser):
    app.logger.info("Request on /page/duplicate with POST")
    try:
        #check if key exists in request json
        pageID_to_duplicate = request.json["pageID"]
        #print(pageID_to_duplicate)
        page = Page.query.filter_by(pageID=pageID_to_duplicate).first()
        if not page:
            return jsonify({'message':'Page not found!'}),404
        #check if user is allowed to duplicate page
        #get information from Access table filter by pageID and userID
        access = Access.query.filter_by(pageID=pageID_to_duplicate,userID=currentUser.userID).first()
        if not ((access and access.accessLvl >1) or currentUser.isAdmin):
            return jsonify({'message':'You are not allowed to duplicate the page'}),406
        newPage = Page(page.name,page.imgLink,page.description)
        newAccess = Access(3,newPage.pageID,currentUser.userID)
        db.session.add(newPage)
        db.session.add(newAccess)
        #duplicate all contents of page
        contents = Content.query.filter_by(pageID=pageID_to_duplicate).all()
        for content in contents:
            newContent = Content(content.name,content.type,content.content,newPage.pageID)
            db.session.add(newContent)
        db.session.commit()
        return jsonify({'message':'Page duplicated!'}),201
    except Exception as e:
        app.logger.error(e)
        return jsonify({'message':'Failed to duplicate Page!'}),406

#create Access
@app.route('/access', methods=['POST'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def createAccess(currentUser):
    app.logger.info("Request on /access with POST")
    try:
        #check if key exists in request json
        if not "pageID" in request.json:
            return jsonify({'message':'No pageID given!'}),406
        if not "userID" in request.json:
            return jsonify({'message':'No userID given!'}),406
        if not "accessLvl" in request.json:
            return jsonify({'message':'No accessLvl given!'}),406

        user = User.query.filter_by(userID=request.json["userID"]).first()
        if not user:
            return jsonify({'message':'User not found!'}),404
        #check if page exists
        page = Page.query.filter_by(pageID=request.json["pageID"]).first()
        if not page:
            return jsonify({'message':'Page not found!'}),404
        #check if access is valid
        if not (request.json["accessLvl"] >= 0 and request.json["accessLvl"] <= 3):
            return jsonify({'message':'Access level must be between 0 and 3'}),406
        
        #check if user is allowed to create access
        #get information from Access table filter by pageID and userID
        access = Access.query.filter_by(pageID=request.json["pageID"],userID=currentUser.userID).first()

        if not ((access and access.accessLvl >2) or currentUser.isAdmin): #only the owner of the page or the admin can create access
            return jsonify({'message':'You are not allowed to create the access'}),406
        #check if access already exists
        
        accessNew = Access.query.filter_by(pageID=request.json["pageID"],userID=request.json["userID"]).first()
        if accessNew:
            #update accessLvl
            accessNew.accessLvl = request.json["accessLvl"]

        else:
            #check if user exists
            
            #create new access
            newAccess = Access(request.json["accessLvl"],request.json["pageID"],request.json["userID"])
            db.session.add(newAccess)
        db.session.commit()
        return jsonify({'message':'Access created'}),201
    except Exception as e:
        app.logger.error(e)
        return jsonify({'message':'Failed to save Access!'}),406

#get AccessLvl
@app.route('/access/<id>', methods=['GET'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def getAccessLvl(currentUser,id):
    app.logger.info("Request on /access with GET")
    try:
        #check if page exists
        page = Page.query.filter_by(pageID=id).first()
        if not page:
            return jsonify({'message':'Page not found!'}),404
        #check if user exists
        user = User.query.filter_by(userID=currentUser.userID).first()
        if not user:
            return jsonify({'message':'User not found!'}),404
        #check if access exists
        access = Access.query.filter_by(pageID=id,userID=currentUser.userID).first()

        if not ((access and access.accessLvl >0) or currentUser.isAdmin): 
            return jsonify({'message':'You are not allowed to get the access'}),406
        return jsonify({'accessLvl':access.accessLvl}),200
    except Exception as e:
        app.logger.error(e)
        return jsonify({'message':'Failed to get Access!'}),406

#update Access for page
@app.route('/access/<id>', methods=['PUT'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def updateAccessLvl(currentUser,id):
    app.logger.info("Request on /access with PUT")
    # try:
        #check if page exists
    page = Page.query.filter_by(pageID=id).first()
    if not page:
        return jsonify({'message':'Page not found!'}),404

    #check id user is allowed to update access
    #get information from Access table filter by pageID and userID
    accessEditor = Access.query.filter_by(pageID=id,userID=currentUser.userID).first()
    if not ((accessEditor and accessEditor.accessLvl >2) or currentUser.isAdmin): #only the owner of the page or the admin can update access
        return jsonify({'message':'You are not allowed to update the access'}),406

    #loop through request json array
    


    for access in request.json:
        #log access
        app.logger.info(access)
        #log accessLvl
        app.logger.info(access["accessLvl"])


        #check if accessLvl exists in access

        if not "accessLvl" in access:
            return jsonify({'message':'No accessLvl given!'}),406
        #check if access is valid
        if not (access["accessLvl"] >= 0 and access["accessLvl"] < 3):
            return jsonify({'message':'Access level must be between 0 and 2'}),406
        
        
        #check if user exists
        user = User.query.filter_by(userID=currentUser.userID).first()
        if not user:
            return jsonify({'message':'User not found!'}),404
        #check if access exists
        existingaccess = Access.query.filter_by(pageID=id,userID=access["userID"]).first()
        if not existingaccess:
            #create new access
            newAccess = Access(access["accessLvl"],id,access["userID"])
            db.session.add(newAccess)
        else:
            #update accessLvl
            existingaccess.accessLvl = access["accessLvl"]
        
        db.session.commit()
    return jsonify({'message':'Access updated'}),200
    # except Exception as e:
    #     app.logger.error(e)
    #     return jsonify({'message':'Failed to update Access!'}),406


#get AccessLvls for current user
@app.route('/access', methods=['GET'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def getAccessLvls(currentUser):
    app.logger.info("Request on /access with GET")
    try:
        #get all accessLvls for current user
        accessLvls = Access.query.filter_by(userID=currentUser.userID).all()
        if not accessLvls:
            return jsonify({'message':'No accessLvls found!'}),404
        # accessLvls = accesses_schema.dump(accessLvls)
        # pages_schema.jsonify(pages)
        return (accesses_schema.jsonify(accessLvls)),200
    except Exception as e:
        app.logger.error(e)
        return jsonify({'message':'Failed to get Access!'}),406

#get all users with accessLvl for Page
@app.route('/access/allusers/<id>', methods=['GET'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def getAllUsersWithAccessLvl(currentUser,id):
    app.logger.info("Request on /access/allusers with GET")
    try:
        #check if page exists
        page = Page.query.filter_by(pageID=id).first()
        if not page:
            return jsonify({'message':'Page not found!'}),404
        #check if user exists
        user = User.query.filter_by(userID=currentUser.userID).first()
        if not user:
            return jsonify({'message':'User not found!'}),404
        #check if access exists
        access = Access.query.filter_by(pageID=id,userID=currentUser.userID).first()

        if not ((access and access.accessLvl >2) or currentUser.isAdmin): 
            return jsonify({'message':'You are not allowed to get the access'}),406
        

        #get all users
        users = User.query.all()

        #filter current User from users
        users = [user for user in users if user.userID != currentUser.userID]

        #get all accessLvls for page
        accessLvls = Access.query.filter_by(pageID=id).all()
        
        minUser=[]

        for user in users:
            added = False;
            #if user is in accessLvls add id, role, name and accessLvl to minUser
            for accessLvl in accessLvls:
                if user.userID == accessLvl.userID:
                    #check if user is admin
                    if user.isAdmin:
                        minUser.append({"userID":user.userID,"role":"Admin","name":user.name,"accessLvl":accessLvl.accessLvl})
                        added=True
                        break
                    #check if user is teacher
                    if user.isTeacher:
                        minUser.append({"userID":user.userID,"role":"Lehrer","name":user.name,"accessLvl":accessLvl.accessLvl})
                        added=True
                        break
                    minUser.append({"userID":user.userID,"role":"User","name":user.name,"accessLvl":accessLvl.accessLvl})
                    added=True
                    break
            #if user is not in accessLvls add id, role, name and accessLvl 0 to minUser
            if not added: 
                if user.isAdmin: minUser.append({"userID":user.userID,"role":"Admin","name":user.name,"accessLvl":0})
                elif user.isTeacher: minUser.append({"userID":user.userID,"role":"Lehrer","name":user.name,"accessLvl":0})
                else: minUser.append({"userID":user.userID,"role":"User","name":user.name,"accessLvl":0})
        
        #match accessLvls with users

        
        return (jsonify(minUser)),200
    except Exception as e:
        app.logger.error(e)
        return jsonify({'message':'Failed to get all Users with access!'}),406

#delete Access
@app.route('/access', methods=['DELETE'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def deleteAccess(currentUser):
    app.logger.info("Request on /access with DELETE")
    try:
        #check if key exists in request json
        if not "pageID" in request.json:
            return jsonify({'message':'No pageID given!'}),406
        if not "userID" in request.json:
            return jsonify({'message':'No userID given!'}),406
        #check if user exists
        user = User.query.filter_by(userID=request.json["userID"]).first()
        if not user:
            return jsonify({'message':'User not found!'}),404
        #check if page exists
        page = Page.query.filter_by(pageID=request.json["pageID"]).first()
        if not page:
            return jsonify({'message':'Page not found!'}),404

        #check if user is allowed to delete access
        #get information from Access table filter by pageID and userID
        access = Access.query.filter_by(pageID=request.json["pageID"],userID=currentUser.userID).first()
        if not (access and access.accessLvl >2) or currentUser.isAdmin: #only the owner of the page or the admin can delete access
            return jsonify({'message':'You are not allowed to delete the access'}),406
        #check if access exists
        access = Access.query.filter_by(pageID=request.json["pageID"],userID=request.json["userID"]).first()
        if not access:
            return jsonify({'message':'Access not found!'}),404
        #delete access
        db.session.delete(access)
        db.session.commit()
        return jsonify({'message':'Access deleted'}),200
    except Exception as e:
        app.logger.error(e)
        return jsonify({'message':'Failed to delete Access!'}),406


#create Content
@app.route('/content', methods=['POST'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def createContent(currentUser):
    #example request json {"name":"test","type":"text","content":"test","pageID":1}
    app.logger.info("Request on /content with POST")
    try:
        #check if key exists in request json
        if not "pageID" in request.json:
            return jsonify({'message':'No pageID given!'}),406
        if not "content" in request.json:
            return jsonify({'message':'No content given!'}),406
        if not "type" in request.json:
            return jsonify({'message':'No type given!'}),406
        if not "name" in request.json:
            return jsonify({'message':'No name given!'}),406


        #check if user is allowed to create content
        #get information from Access table filter by pageID and userID
        access = Access.query.filter_by(pageID=request.json["pageID"],userID=currentUser.userID).first()
        if not ((access and (int(access.accessLvl) > 1)) or currentUser.isAdmin): #only the owner of the page or the admin can create content
            return jsonify({'message':'You are not allowed to create the content'}),406
        
        
        #create new content
        newContent = Content(request.json["name"],request.json["type"],request.json["content"],request.json["pageID"])
        db.session.add(newContent)
        db.session.commit()
        return jsonify({'message':'Content created'}),201
    except Exception as e:
        app.logger.error(e)
        return jsonify({'message':'Failed to save Content!'}),406


#update Content
@app.route('/content', methods=['PUT'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def updateContent(currentUser):
    app.logger.info("Request on /content with PUT")
    try:
        #check if contentid exists in json
        if not "contentID" in request.json:
            return jsonify({'message':'No contentID given!'}),406

        #check if content exists
        content = Content.query.filter_by(contentID=request.json["contentID"]).first()
        if not content:
            return jsonify({'message':'Content not found!'}),404
        
        #check if user is allowed to update content
        #get information from Access table filter by pageID and userID
        access = Access.query.filter_by(pageID=content.pageID,userID=currentUser.userID).first()
        if not ((access and access.accessLvl >1) or currentUser.isAdmin): #only the owner of the page or the admin can update content
            return jsonify({'message':'You are not allowed to update the content'}),406
        
        #update content
        #check if key exists in request json
        if "name" in request.json:
            content.name = request.json["name"]
        if "type" in request.json:   
            content.type = request.json["type"]
        if "content" in request.json:
            content.content = request.json["content"]

        db.session.commit()
        return jsonify({'message':'Content updated'}),200
    except Exception as e:
        app.logger.error(e)
        return jsonify({'message':'Failed to save Content!'}),406

#Delete Content
@app.route('/content', methods=['DELETE'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def deleteContent(currentUser):
    app.logger.info("Request on /content with DELETE")
    try:
        #check if contentid exists in json
        if not "contentID" in request.json:
            return jsonify({'message':'No contentID given!'}),406
        #check if content exists
        content = Content.query.filter_by(contentID=request.json["contentID"]).first()
        if not content:
            return jsonify({'message':'Content not found!'}),404

        #check if user is allowed to delete content
        #get information from Access table filter by pageID and userID
        access = Access.query.filter_by(pageID=content.pageID,userID=currentUser.userID).first()
        #print(access)
        #print(access.accessLvl)
        if not ((access and access.accessLvl >1) or currentUser.isAdmin): #only the owner of the page or the admin can delete content
            return jsonify({'message':'You are not allowed to delete the content'}),406
        

        #delete content
        #print(content)
        db.session.delete(content)
        db.session.commit()
        return jsonify({'message':'Content deleted'}),200
    except Exception as e:
        app.logger.error(e)
        return jsonify({'message':'Failed to delete Content!'}),406


#duplicate content
@app.route('/content/duplicate', methods=['POST'])
@cross_origin(origin='*',headers=['content-type'])
@tokenCheck
def duplicateContent(currentUser):
    app.logger.info("Request on /content/duplicate with POST")
    try:
        #check if contentid exists in json
        if not "contentID" in request.json:
            return jsonify({'message':'No contentID given!'}),406

    
        #check if content exists
        content = Content.query.filter_by(contentID=request.json["contentID"]).first()
        if not content:
            return jsonify({'message':'Content not found!'}),404
        #check if user is allowed to duplicate content
        #get information from Access table filter by pageID and userID
        access = Access.query.filter_by(pageID=content.pageID,userID=currentUser.userID).first()
        if not (access and access.accessLvl >1) or currentUser.isAdmin: #only the owner of the page or the admin can duplicate content
            return jsonify({'message':'You are not allowed to duplicate the content'}),406
        
        
        #duplicate content
        newContent = Content(content.name,content.type,content.content,content.pageID)
        db.session.add(newContent)
        db.session.commit()
        return jsonify({'message':'Content duplicated'}),200
    except Exception as e:
        app.logger.error(e)
        return jsonify({'message':'Failed to duplicate Content!'}),406

#healthcheck
@app.route('/healthcheck', methods=['GET'])
@cross_origin(origin='*',headers=['content-type'])
def healthcheck():
    app.logger.info("Request on /healthcheck with GET")
    #check if database is reachable
    try:
        db.session.query(User).first()
        return jsonify({'databaseStatus':'available'}),200
    except Exception as e:
        app.logger.error(e)
        return jsonify({'databaseStatus':'unavailable'}),500
   

@app.before_first_request
def initDB():
    db.create_all()
    #only in debug state:
    if app.debug:
        cleanInstall()



if __name__ == '__main__':
    app.logger.info("Server starting...")

    app.run(host="0.0.0.0",port=5050,debug=True) #docker
    #app.run(port=5060,debug=True) #local