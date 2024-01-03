

user_group = db.Table('user_group',
                            db.Column('userID', db.String, db.ForeignKey('user.userID')),
                            db.Column('groupID', db.String, db.ForeignKey('group.groupID')))
            
# user_access = db.Table('user_access', 
#                             db.Column('userID', db.String, db.ForeignKey('user.userID')),
#                             db.Column('pageID', db.String, db.ForeignKey('page.pageID')),
#                             db.Column('accesslevel',db.Integer))

# group_access = db.Table('group_access', 
#                             db.Column('groupID', db.String, db.ForeignKey('group.groupID')),
#                             db.Column('pageID', db.String, db.ForeignKey('page.pageID')),
#                             db.Column('accesslevel',db.Integer))

class Accessor(db.Model):
    __tablename__="accessor"
    accessorID = db.Column(db.String(38), primary_key=True) #UUID
    
    #access = db.relationship("Access")

    __mapper_args__ = {
        "polymorphic_identity": "accessor",
        #"concrete": True,
    }
    def __init__(self):
        self.accessorID=str(uuid.uuid4())


class User(Accessor):
    userID = db.Column(db.ForeignKey("accessor.accessorID"), primary_key=True)#db.Column(db.String(38), primary_key=True) #UUID  #
    name = db.Column(db.String(100))
    username = db.Column(db.String(100), unique=True)
    mail=db.Column(db.String(100),unique=True)
    pwHash = db.Column(db.String(100))



    def hash_password(self):
        self.pwHash = generate_password_hash(self.pwHash).decode('utf8')

    def check_password(self, pwHash):
        return check_password_hash(self.pwHash, pwHash)

    def __init__(self,name,username,mail,pwHash):
        Accessor.__init__(self)
        #self.userID=userID
        self.name=name
        self.username = username
        self.mail=mail
        self.pwHash=pwHash

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        load_instance = True


class AccessorSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Accessor
        load_instance = True
    

user_schema = UserSchema()
users_schema = UserSchema(many=True)

class Group(Accessor):
    __tablename__ = "group"
    groupID = db.Column(db.ForeignKey("accessor.accessorID"), primary_key=True)#db.Column(db.String(38), primary_key=True) #UUID
    name = db.Column(db.String(100))
    users =db.relationship('User', secondary="user_group", backref='groups', lazy="joined")
    
    __mapper_args__ = {
        "polymorphic_identity": "group",
        #"concrete": True,
    }

    def __init__(self,name):
        Accessor.__init__(self)
        #self.groupID=groupID
        self.name=name



class GroupSchema(ma.SQLAlchemyAutoSchema):
    users = ma.Nested(UserSchema, many=True)
    class Meta:
        model = Group
        load_instance = True


group_schema = GroupSchema()
groups_schema = GroupSchema(many=True)
class Content(db.Model):
    __tablename__="content"
    contentID = db.Column(db.String(38), primary_key=True) #UUID
    name = db.Column(db.String(100))
    type = db.Column(db.String(100))
    description = db.Column(db.String(10000))
    page_id = db.Column(db.String(38), db.ForeignKey("page.pageID"))
    page = db.relationship('Page',back_populates="contents")

class Page(db.Model):
    __tablename__="page"
    pageID = db.Column(db.String(38), primary_key=True) #UUID
    name = db.Column(db.String(100))
    imgLink = db.Column(db.String(100))
    description = db.Column(db.String(400))
    contents = db.relationship("Content",back_populates="page")

    #access = db.relationship("Access")

    #users_access =db.relationship('User', secondary="user_access", backref='access', lazy="joined")
    #group_access =db.relationship('Group', secondary="group_access", backref='access', lazy="joined")

class PageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Page
        load_instance = True


class ContentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Content
        load_instance = True


class Access(db.Model):
    __tablename__="access"
    accessID = db.Column(db.String(38), primary_key=True) 
    accessLvl= db.Column(db.Integer)


    pageID = db.Column(db.String(38), db.ForeignKey("page.pageID"))
    pages = db.relationship("Page", back_populates="access")
    accessorID = db.Column(db.String(38), db.ForeignKey("accessor.accessorID"))
    accessors = db.relationship("Accessor", back_populates="access")
    

    

### Groups old code dump

@app.route('/groups/', methods=['GET'])
@cross_origin(origin='*',headers=['content-type'])
def getGroups():
    all_groups= Group.query.all()

    result = groups_schema.dump(all_groups)

    return jsonify(result)