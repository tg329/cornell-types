"""
Requests:
GET: Feed of ALL posts --> related to users and all of the 16 personalities.
GET: Share Link from your profile.
GET: Search feed for a specific user (ask Mateo) to return their profile consisiting of bio, username and personality.
GET: Statistics for cornell community - generate pie charts/graphs to shows statistics (percentage) based on school.
GET: Get the questions for the quiz.
GET: Get personality type of user after they're done with the quiz and also when user clicks on their profile icon.
POST: Register New User
POST: Login New User
POST: Logout User
POST: Update Session for User
POST: Survey to get personality type
DELETE can delete personality type from user info 
POST: Create post with text for the associated user
"""
#TODO: Research External APi
#TODO: Research Image Lecture
#TODO: Test users routes with postman

import json
from db import db
from flask import Flask, request
from db import User, Personality_Type, Post
import os
import datetime
import users_dao
app = Flask(__name__)
db_filename = "users.db"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()

# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code

def failure_response(message, code=404):
    return json.dumps({"error": message}), code

#helper function
def extract_token(request):
    """
    Helper function that extracts the token from the header
    """
    auth_header = request.headers.get("Authorization")
    if auth_header is None:
        return False, failure_response("Missing authorization header.")
    bearer_token = auth_header.replace("Bearer ", "").strip()
    if bearer_token is None or not bearer_token:
        return False, failure_response("Invalid authorization header.")
    return True, bearer_token

#ROUTES

@app.route("/")
def greeting():
    """
    Starting Point (Home Page)
    
    """
    return success_response("Hello! Welcome to the Cornell Personality Type App!")

#User Register/Login/Logout/UpdateSession
@app.route("/api/users/register/", methods=["POST"])
def register_account():
    """
    Endipoing for creating a new user
        Requires email
        Requires password 
    Redirect to POST: Survey to get personality type
    """
    body = json.loads(request.data)
    email = body.get("email")
    password = body.get("password")

    if email is None or password is None:
        return failure_response("Email or password not provided")
    created, user = users_dao.create_user(email, password)

    if not created:
        return failure_response("User already exists")
    
    #NOTE: from authentication demo; doesn't work until db is set up 
    return success_response({
        "session_token": user.session_token,
        "session_expiration": str(user.session_expiration),
        "update_token": user.update_token
    })

@app.route("/api/users/login/", methods=["POST"])
def login():
    """
    Endpoint for logging in
        Requires email
        Requires password
    """
    body = json.loads(request.data)
    email = body.get("email")
    password = body.get("password")

    if email is None or password is None:
        return failure_response("Email or password not provided")
    success, user = users_dao.verify_credentials(email, password)

    if not success:
        return failure_response("Incorrect email or password")
    
    #NOTE: from authentication demo; doesn't work until db is set up
    return success_response({
        "session_token": user.session_token,
        "session_expiration": str(user.session_expiration),
        "update_token": user.update_token
    })


@app.route("/api/users/logout/", methods=["POST"])
def logout():
    """
    Endpoint for logging out
    """
    success, session_token = extract_token(request)
    if not success:
        return session_token
    user = users_dao.get_user_by_session_token(session_token)
    if user is None:
        return failure_response("Invalid session token")
    if not user.verify_session_token(session_token):
        return failure_response("Invalid session token")
    user.session.expiration = datetime.datetime.now()
    db.session.commit()
    return success_response("Successfully logged out")

@app.route("/api/users/session/", methods=["POST"])
def update_session():
    """
    Endpoint for updating session
    """
    success, update_token = extract_token(request)

    if not success:
        return update_token
    user = users_dao.get_user_by_update_token(update_token)
    if user is None:
        return failure_response("Invalid update token")
    
    #NOTE: from authentication demo; doesn't work until db is set up
    return success_response({
        "session_token": user.session_token,
        "session_expiration": str(user.session_expiration),
        "update_token": user.update_token
    })

#TODO: might need secret message for this

#TODO: REWORK THIS TOMORROW
@app.route("/api/users/")
def get_users():
    """
    GET Feed of users with personality types
    """
    pass

@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    """
    GET: Search feed for a specific user
    """
    pass

@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user_personality(user_id):
    """
    DELETE can delete personality type from user info 
    Redirect to POST: Survey to get personality type
    """
    pass

@app.route("/api/users/<int:user_id>/", methods=["POST"])
def post_user(user_id):
    """
    POST: Post personality type to feed
    """
    pass

@app.route("/api/users/<int:user_id>/share")
def get_user_share_link(user_id):
    """
    GET: Share Link from your profile 
    """
    pass

@app.route("/api/users/statistics", methods=["GET"])
def get_statistics(user_id):
    """
    GET: Statistics for cornell community
    """
    pass

#TODO: need GET app for external APi? then post? 
@app.route("/api/users/<int:user_id>/survey", methods=["POST"])
def post_survey(user_id):
    """
    POST: Survey to get personality type
    """
    pass

@app.route("/api/users/<int:user_id>/survey", methods=["UPDATE"])
def update_survey(user_id):
    """
    UPDATE Can retake survey to get new personality type
    Redirect to POST: Survey to get personality type
    """
    pass
