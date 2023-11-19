#NOTE: added GET: Search feed for a specific user by username to return their profile consisiting of bio, username and personality.
#NOTE: added GET: Search feed for a specific user by post_id to return their profile consisiting of bio, username and personality.
#NOTE: added POST: create new survey for the user
#NOTE: added POST: submit survey responses and return personality type for the user (E/I, N/S, T/F, J/P)
#NOTE: removed GET Personality Type. Just use GET User or Hard Coded Personality Type (for the mini circles at top of feed)
"""
Requests:
Posts:
    GET: Feed of ALL posts --> related to users and all of the 16 personalities.
    POST: Create post with text for the associated user
    GET: Return personality type by personality_id 

Users:
    GET: Share Link from your profile.
    GET: Get Personality Type 
    DELETE: Delete user's personality type (Afterwards, frontend should redirect to POST: Survey to get personality type)

    Authentication: 
        POST: Register New User
        POST: Login New User
        POST: Logout User
        POST: Update Session for User
    Feed:
        GET: Search feed for a specific user by username to return their profile consisiting of bio, username and personality.
        GET: Search feed for a specific user by post_id to return their profile consisiting of bio, username and personality.
        GET: Statistics for cornell community - generate pie charts/graphs to shows statistics (percentage) based on school.
Survey:
    POST: Create new survey (hardcoded questions) for the user
    POST: Submit response to a specific question 
          survey's reponse will be equal to the list of responses from the user in terms of [E, I, N, S, T, F, J, P]
          increment response dictionary's value by 1
    GET: Analyze results from survey, update the user with the personality type, and return personality type
"""

#TODO: Research External APi
    #Can't find external API, but did find questionnaires
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
    bearer_token = auth_header.replace("Bearer", "").strip()
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
    username = body.get("username")
    password = body.get("password")
    school = body.get("school")

    if email is None or password is None:
        return failure_response("Email, password, username, or school not provided")
    created, user = users_dao.create_user(email, username, password, school) #TODO: same format as user_dao.py

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
    username = body.get("username")
    password = body.get("password")

    if (email is None and username is None) or password is None:
        return failure_response("Email or username not provided, or password not provided")
    success, user = users_dao.verify_credentials(email, username, password) #TODO: update users_dao.py 

    if not success:
        return failure_response("Incorrect email/username or password")

    #NOTE: from authentication demo; doesn't work until db is set up
    return success_response({
        "session_token": user.session_token,
        "session_expiration": str(user.session_expiration),
        "update_token": user.update_token
    })


@app.route("/api/users/logout/", methods=["POST"])
def logout():
    """
    Endpoint for logging out a user
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
    user = users_dao.renew_session(update_token)
    #change this - should be renew_session method in users_dao.py
    if user is None:
        return failure_response("Invalid update token")

    #NOTE: from authentication demo; doesn't work until db is set up
    return success_response({
        "session_token": user.session_token,
        "session_expiration": str(user.session_expiration),
        "update_token": user.update_token
    })
  
@app.route("/api/users/")
def get_posts():
    """
    GET: Feed of ALL posts --> related to users and all of the 16 personalities.
    """
    return success_response([p.serialize() for p in Post.query.all()])

# also need get all personalities for mini-circles on top of feed
#TODO: add GET personality by personality_id request 
@app.route("/api/users/<int:personality_id>/", methods=["GET"])
def get_personality_type(personality_id):
  """
  GET: personality
  """
  pass

@app.route("/api/users/posts/<int:post_id>/")
def get_user(post_id):
    """
    GET: Search feed for a specific user by post_id
    """
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
      return failure_response("Post not found!")
    user_id = post.userid
    user = User.query.filter_by(id=user_id).first()
    if user is None:
      return failure_response("User not found!")
    return success_response(user.simple_serialize())

@app.route("/api/users/username/<String:username>", methods=["GET"])
def get_user_by_username(username):
    """
    GET: Search feed for a specific user by username
    #NOTE: case sensitive
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        return failure_response("User not found!")
    return success_response(user.simple_serialize())

#TODO: check "personality_type" in db.py 
@app.route("/api/users/<int:user_id>/", methods=["DELETE"])
def delete_user_personality(user_id):
    """
    DELETE can delete personality type from user info 
    After this request, frontend should redirect to POST: Survey to get personality type
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")
    user.personality_id = None
    db.session.commit()
    return success_response(user.simple_serialize())

#TODO: check "Post" in db.py
@app.route("/api/users/<int:user_id>/", methods=["POST"])
def create_post(user_id):
    """
    POST: Create post with text for the associated user
    """
    body = json.loads(request.data)
    text = body.get("text")
    #TODO: add image stuff later
    if text is None:
        return failure_response("Text not provided")

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")

    post = Post(text=text, userid=user_id) #TODO: add image stuff later
    db.session.add(post)
    db.session.commit()
    return success_response(post.serialize())

#TODO: check "User.share_link" in db.py
@app.route("/api/users/<int:user_id>/share")
def get_user_share_link(user_id):
    """
    GET: Share Link from your profile 
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")
    return success_response(User.share_link(user)) #TODO: figure out share_link function

@app.route("/api/users/statistics", methods=["GET"])
def get_statistics(user_id):
    """
    GET: Statistics for cornell community
    """
    # by school, what % are a certain personality type
    pass
    # query filter of users in school
    # [users]/[a personality_model # of users]

#Survey Routes

@app.route("/api/surveys/<int:user_id>/<int:question_id>", methods=["GET"])
def create_survey():
    """
    POST: Create Survey
         Also return all survey questions
    """
    # get user_id 
    # create survey (user_id, question_id)
    # return the survey with that specific question

    pass

@app.route("/api/surveys/<int:user_id>/<int:question_id>", methods=["POST"])
def submit_responses():
    """
    POST: Submit response to a specific question 
          survey's reponse will be equal to the list of responses from the user in terms of [E, I, N, S, T, F, J, P]
          increment response dictionary's value by 1
    """
    pass

@app.route("/api/surveys/<int: user_id>/results", methods = ["GET"])
def get_results():
  """
  GET: Analyze results from survey, update the user with the personality type, and return personality type
  """
  pass

