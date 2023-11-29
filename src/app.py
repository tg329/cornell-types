#TODO: (AFTER TESTING) add descriptions for each personliaty type instead of image
#TODO: fix libraries for images 
#TODO: restore proper liberaries for flask login and flask mail (why didn't it save lol)
"""
TESTING

if there is body request, then make sure throws the correct error message if information is missing

USER Authentication:
1. add email_verification code 
2. user (register, login, logout, update_session) 
- check if user logouts, information still remains in database

Survey:
1. FUNC create_survey_questions
2. GET: Specific Question with Questions Options
3. POST: Submit specific user's response to a specific question
4. GET: After all answers submitted, get user's new personality type and update the user in the database.
 - test out different combinations of options 

Feed with Posts:
1. GET: Feed of ALL posts --> related to users and all of the 16 personalities.
2. POST: Create post with text for the associated user
3. GET: Return personality type by personality_id
4. GET: Search feed for a specific user by username to return their profile consisiting of bio, username and personality.
5. GET: Search feed for a specific user by post_id to return their profile consisiting of bio, username and personality.
6. GET: Statistics for cornell community - generate pie charts/graphs to shows statistics (percentage) based on school.
"""


"""
Requests:
Posts:
    GET: Feed of ALL posts --> related to users and all of the 16 personalities.
    POST: Create post with text for the associated user
    GET: Return personality type by personality_id 

Users:
    GET: Get Personality Type 
    DELETE: Delete user's personality type (Afterwards, frontend should redirect to POST: Survey to get personality type)
    POST: Edit bio for specific user 

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
    FUNC create_survey_questions: creates all questions w/ options models at beginning of app
    GET: Specific Question with Questions Options 
    POST: Submit specific user's response to a specific question
    PATCH: After all answers submitted, get user's new personality type and update the user in the database. 
"""

#TODO: Research External APi
    #Can't find external API, but did find questionnaires
#TODO: Research Image Lecture
#TODO: Test users routes with postman

import json
from db import db
from flask import Flask, request, redirect, url_for, flash, g
import flask_login
from flask_mail import Mail, Message
import os
import datetime
import users_dao
import random
import string
from functools import wraps
from flask import Flask, request
from db import User, Personality, Post, Question, QuestionOption, UserAnswer, Asset
import os
import datetime
import users_dao
from questions import question_data
#import helper_funcs as helper
app = Flask(__name__)
db_filename = "users.db"

secret_key = os.environ.get('SECRET_KEY')
app.secret_key = secret_key #TODO: place in .env file another time
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
# Configure Flask-Mail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'hannahyunzizhou@gmail.com'
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = 'hannahyunzizhou@gmail.com'

INITIALIZATION_FILE = 'initialization_status.txt'

mail = Mail(app)

login_manager = flask_login.LoginManager(app)
login_manager.login_view = "login"

#global variable 
cornell_schools = [
    "College of Agriculture and Life Sciences",
    "College of Architecture, Art, and Planning",
    "College of Arts and Sciences",
    "Cornell SC Johnson College of Business",
    "College of Engineering",
    "College of Human Ecology",
    "School of Hotel Administration",
    "Cornell Law School"
]

db.init_app(app)
def create_app():
    # Check if the initialization status file exists
    if not os.path.exists(INITIALIZATION_FILE):
        with app.app_context():
            # Initialize the database and run your functions
            db.create_all()
            helper.create_survey_questions()
            helper.create_personalities()
            # Create the initialization status file
            with open(INITIALIZATION_FILE, 'w') as file:
                file.write("initialized")
    return app

# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code

def failure_response(message, code=404):
    return json.dumps({"error": message}), code

def send_verification_email(email, verification_code):
    """
    Helper function that sends a verification code to the user's email
    """
    msg = Message("Cornell Personality Type Verification Code", recipients=[email], sender = 'hannahyunzizhou@gmail.com')
    msg.body = f"Your verification code is: {verification_code}"
    mail.send(msg)

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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def greeting():
    """
    Starting Point (Home Page)

    """
    return success_response("Hello! Welcome to the Cornell Personality Type App!")

#--- DEBUGGERS---
@app.route("/api/users/delete/<int:user_id>/", methods=["DELETE"])
def delete_user(user_id):
    """
    DELETE: Delete User
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")
    db.session.delete(user)
    db.session.commit()
    return success_response(user.simple_serialize())

@app.route("/api/users/survey/", methods=["GET"])
def get_survey_questions():
    """
    GET: Survey Questions
    """
    return success_response([q.serialize() for q in Question.query.all()])

@app.route("/api/users/personalities/", methods=["GET"])
def get_personalities():
    """
    GET: All Personalities
    """
    return success_response([p.serialize() for p in Personality.query.all()])

@app.route("/api/users/personalities/delete/", methods=["DELETE"])
def delete_personality():
    """
    DELETE: from the database, delete all the personalities models
    """
    for personality in Personality.query.all():
        db.session.delete(personality)
    db.session.commit()
    return success_response("Successfully deleted all personalities")

#---AUTHENTICATION---
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
    if "@cornell.edu" not in email:
        return failure_response("Email not a valid Cornell email")
    if school not in cornell_schools:
        return failure_response("School not a valid Cornell school")
    # Generate a random verification code
    verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    created, user = users_dao.create_user(email, username, password, school, verification_code = verification_code) #TODO: same format as user_dao.py

    if not created:
        return failure_response("User already exists")
    
        #send the  verification email
    send_verification_email(email, verification_code)
    flash('Check your email for the verification code', 'success')

    #NOTE: from authentication demo; doesn't work until db is set up 
    return success_response({
        "message": "Check your email for the verification code",
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
    
    if user.is_verified != True:
        return failure_response("User not verified. Please verify your account.", 403)
    
    flask_login.login_user(user)
    flash('You have been logged in!', 'success')
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
    user.session_expiration = datetime.datetime.now()
    db.session.commit()
    return success_response("Successfully logged out")

@app.route('/api/users/verify/<string:verification_code>/')
def verify(verification_code):
    user = User.query.filter_by(verification_code=verification_code).first()

    if user:
        user.is_verified = True
        db.session.commit()
    else:
        return failure_response("Invalid verification code")

    return success_response("Email verification successful. You can now log in.")

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

@app.route("/api/posts/")
def get_posts():
    """
    GET: Feed of ALL posts --> related to users and all of the 16 personalities.
    """
    return success_response([p.serialize() for p in Post.query.all()])

# also need get all personalities for mini-circles on top of feed
@app.route("/api/personalities/<int:personality_id>/", methods=["GET"])
def get_personality_type(personality_id):
  """
  GET: personality
  """
  personality = Personality.query.filter_by(id = personality_id).first()
  if personality is None:
    return failure_response("Personality not found")
  return success_response(personality.serialize()) 

@app.route("/api/posts/<int:post_id>/")
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
    if user.is_verified != True:
        return failure_response("User not verified. Please verify your account.", 403)
    return success_response(user.simple_serialize())

@app.route("/api/users/<string:username>/", methods=["GET"])
def get_user_by_username(username):
    """
    GET: Search feed for a specific user by username
    #NOTE: case sensitive
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        return failure_response("User not found!")
    if user.is_verified != True:
        return failure_response("The user found is not verified.")
    return success_response(user.simple_serialize())

@app.route("/api/users/<int:user_id>/bio/", methods = ["POST"])
def edit_user_bio(user_id):
  """
  Edit bio for specific user
  """
  body = request.get_json()
  text = body.get("text")
  if text is None: text = "No bio provided"
  
  user = User.query.filter_by(id=user_id).first()
  if user is None:
    return failure_response("No user found")

  user.bio = text
  db.session.commit()
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
    personality = Personality.query.filter_by(id=user.personality_id).first()
    personality.num_of_each -=1 #NEW, decrement num_of_each in personality instance
    user.personality_id = None
    db.session.commit()
    return success_response(user.simple_serialize())

#TODO: check "Post" in db.py
@app.route("/api/users/<int:user_id>/posts/", methods=["POST"])
def create_post(user_id):
    """
    POST: Create post with text for the associated user
    """
    body = json.loads(request.data)
    text = body.get("text")
    #image_data = body.get("image_data")
    #if image_data is None:
       #return failure_response("No url for image provided")
    if text is None:
        return failure_response("Text not provided")

    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found!")

    #asset = Asset(image_data = image_data)
    #db.session.add(asset)
    #db.session.commit()
    post = Post(text=text, userid=user_id) #TODO: add image stuff later
    db.session.add(post)
    db.session.commit()
    return success_response(post.serialize())

#-- Debug---
@app.route("/api/posts/<int:post_id>/", methods=["DELETE"])
def get_post(post_id):
    """
    GET: Search feed delete post by post_id
    """
    post = Post.query.filter_by(id=post_id).first()
    if post is None:
        return failure_response("Post not found!")
    db.session.delete(post)
    db.session.commit()
    return success_response("deleted")

#MAJORITY personality type for a school 
@app.route("/api/users/statistics/", methods=["GET"])
def get_statistics():
    """
    GET: Statistics for cornell community
    """
    # by personality type, what % are from this school?
    # ENTP - % school of engineering, school of
    #key: ENTP
    # value: school of engineer: % 
    dict = {}

    #TODO: append dictionary

    """personality_id = Personality.query.filter_by(personality_type = "ESFP" ).first().id
    num_users = len(User.query.filter_by(personality_id=personality_id).all())
    lst = []
    lst.append({"College of Engineering": num_users})
    dict["ESFP"] = lst
    """
    
    
    for personality in Personality.query.all():
      max = 0.0
      max_school = ""
      lst = [] #lst of dictionaries. dictionary key is school, value is % 
      for school in cornell_schools:
        num_users = len(User.query.filter_by(personality_id=personality.id, school = school).all())
        if personality.number_of_each == 0: percentage = 0.0
        else: percentage = num_users / personality.number_of_each
        if percentage > max: 
          max = percentage
          max_school = school
      if max != 0.0: lst.append({f"{max_school}": max})
      else: lst.append({f"No users found for {personality.personality_type}": 0.0})
      dict[personality.personality_type] = lst
    return success_response(dict)   

            

    
     

#Survey Routes

# TODO: consider user id in url
@app.route("/api/surveys/<int:question_id>/", methods=["GET"])
def get_question_options(question_id):
    """
    GET: return specific Question with Question Options 
    """
    question = Question.query.filter_by(id = question_id).first()
    options = QuestionOption.query.filter_by(question_id= question.id).all()
    if question is None:
      return failure_response("No question found")
    if options is None:
      return failure_response("No options found")
    return success_response(question.serialize())

#code that will help you create routes
# Assume you have loaded questions and options from your JSON file
# question_data in questions.py file
# User answers questions
#route needs user_id and question_id
@app.route("/api/surveys/<int:user_id>/<int:question_id>/", methods = ["POST"])
def submit_answer(user_id, question_id):
  """
    POST: Submit specific user's response to a specific question
  """
  question = Question.query.filter_by(id = question_id).first()
  options = QuestionOption.query.filter_by(question_id = question.id).all()
  user = User.query.filter_by(id = user_id).first()

  if question is None:
    return failure_response("No question found")
  if options is None:
    return failure_response("No options found")
  if user is None:
    return failure_response("No user found")
  if not user.is_verified:
    return failure_response("User not verified. Please verify your account.", 403)
  
  #selected_option = get_user_selection(question.id)
  body = json.loads(request.data)
  score = body.get("score")
  # find the option that correleates with the correct option.id and score
  selected_option = next((option for option in options if option.score==score), None)
  # (DONT NEED FOR NOW)Find the selected option in the options list
  # selected_option = next((option for option in options if option.option_text == selected_option_text), None)
  if selected_option is None:
    return failure_response("No option based on user's response is found")
    
  previous_answer = UserAnswer.query.filter_by(user_id=user_id, question_id=question.id).first()
  if previous_answer is not None:
    db.session.delete(previous_answer)
  user_answer = UserAnswer(user_id=user_id, question_id=question.id, option_id=selected_option.id)
  #question.answers.append(user_answer)
  db.session.add(user_answer)
  db.session.commit()
  return success_response(user_answer.serialize())

"""#an example of how the get_user_selection method can be defined 
def get_user_selection(question_id):
  # question = Question.query.get(question_id)
  # if not question:
  #     print(f"Question with ID {question_id} not found.")
  #     return None
  options = QuestionOption.query.filter_by(question_id=question_id).all()
  body = json.loads(request.data)
  score = body.get("score")
  selected_option = next((option for option in options if option.score==score))
  return selected_option"""

@app.route("/api/surveys/<int:user_id>/results/")
def update_user_personality_type(user_id):
  """
  Update user with new personality type
  """
  user = User.query.filter_by(id = user_id).first()
  if user is None:
    return failure_response("No user found")
  if not user.is_verified:
    return failure_response("User not verified. Please verify your account.", 403)
  personality_id = helper.find_personality(user_id)
  if personality_id is None:
    return failure_response("Failed to get personality type for the user")
  personality = Personality.query.filter_by(id = personality_id).first()
  personality.number_of_each +=1 
  user.personality_id = personality_id
  db.session.commit()
  return success_response(user.simple_serialize())

if __name__ == "__main__":
    import helper_funcs as helper
    create_app().run(host="0.0.0.0", port=8000, debug=False)