from flask import Flask, request, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import os
from uuid import UUID
from uuid import uuid4
import uuid


app = Flask(__name__)
app.secret_key = "123"
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'securitypage.sqlite')
db = SQLAlchemy(app)
ma = Marshmallow(app)
db.create_all()

engine = create_engine('sqlite:///securitypage.sqlite', echo = True)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    usn = db.Column(db.String(80), unique=True)
    identity = db.Column(db.String(120), unique=True)
    username = db.Column(db.String(10), unique=True)
    password = db.Column(db.String(25),unique=False)
    sessionid = db.Column(db.String(500), unique=False)
	

    def __init__(self, usn, identity, username, password, sessionid):
        self.usn = usn
        self.identity = identity
        self.username = username
        self.password = password
        self.sessionid = sessionid
		
class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('usn', 'identity','username','password')


user_schema = UserSchema()
users_schema = UserSchema(many=True)

# endpoint to create new user	
@app.route("/user/addUser", methods=["POST"])
def add_user():
    usn = request.json['usn']
    identity = request.json['identity']
    
    new_user = User(usn, identity)
    #result = user_schema.dump(new_user)

    db.session.add(new_user)
    db.session.commit()
    #data = user_schema.dump(new_user).data
    return user_schema.jsonify(new_user)
	
# endpoint to show all users
@app.route("/user/showAll", methods=["GET"])
def get_user():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return jsonify(result.data)
        
        
	
#endpoint for fixed login	
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        if request.form['username'] != 'admin' or request.form['password'] != 'admin123':
            error = 'Invalid Credentials. Please try again.'
        else:
            error = 'Successful.'
    return jsonify(error)

#endpoint for dynamic login
@app.route('/login/user', methods=['POST'])
def do_login():
    username = str(request.json['username'])
    password = str(request.json['password'])
    Session = sessionmaker(bind = engine)
    s = Session()
    query = User.query.filter_by(username=username,password=password).first()
    #result = query.first()
    if query:
        s.sid = uuid.uuid4()
        query.sessionid = str(s.sid)
        db.session.commit()
        error = "Successful"
        session['logged_in'] = True		
    else:
        error = "Unsuccessful"
    return jsonify(query.sessionid)

#endpoint to add one time usersettings
@app.route('/signup', methods=['POST'])
def do_signup():
    username = request.json['username']
    password = request.json['password']
    usn = request.json['usn']
    identity = request.json['identity']

    new_user = User(usn, identity, username, password)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user)

@app.route('/logout',methods=['POST'])
def logout():
    session['logged_in'] = False
    return jsonify('logged out')

if __name__ == '__main__':
    #app.run(debug=True)
    
    app.run(host='0.0.0.0')
