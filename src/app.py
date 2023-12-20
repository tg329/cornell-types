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
from db import User, Personality, Post, Question, QuestionOption, UserAnswer, Asset
from questions import question_data
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
db_filename = "users.db"

secret_key = os.environ.get('SECRET_KEY')
app.secret_key = secret_key
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
    "cals",
    "aap",
    "a&s",
    "engineering",
    "ilr",
    "hotel/dyson",
    "hum ec"
]

db.init_app(app)
def create_app():
    # Check if the initialization status file exists
    if not os.path.exists(INITIALIZATION_FILE):
        with app.app_context():
            db.create_all()
            helper.create_survey_questions()
            helper.create_personalities()
            # Create the initialization status file
            with open(INITIALIZATION_FILE, 'w') as file:
                file.write("initialized")
    return app

#generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code

def failure_response(message, code=404):
    return json.dumps({"error": message}), code

#authentication functions
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

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# This can be used to log all incoming requests
@app.before_request
def log_request_info():
    app.logger.info('Headers: %s', request.headers)
    app.logger.info('Body: %s', request.get_data(as_text=True))
    #print all request and errors 
    print(request.headers)
    print(request.get_data(as_text=True))

#ROUTES
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
    DELETE: From the database, delete all the personalities models
    """
    for personality in Personality.query.all():
        db.session.delete(personality)
    db.session.commit()
    return success_response("Successfully deleted all personalities")

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

#---AUTHENTICATION---
@app.route("/api/users/register/", methods=["POST"])
def register_account():
    try:
        """
        POST: Endpoint for creating a new user
            Requires email
            Requires password 
            Requires username 
            Requires school
        """
        body = json.loads(request.data)
        email = body.get("email")
        username = body.get("username")
        password = body.get("password")
        school = body.get("school")

        if email is None or password is None or username is None or school is None:
            return failure_response("Email, password, username, or school not provided")

        if "@cornell.edu" not in email:
            return failure_response("Email not a valid Cornell email")

        if school not in cornell_schools:
            return failure_response("School not a valid Cornell school")

        # Generate a random verification code
        verification_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        created, user = users_dao.create_user(email, username, password, school, verification_code=verification_code)

        if not created:
            return failure_response("User already exists")

        send_verification_email(email, verification_code)
        flash('Check your email for the verification code', 'success')

        return success_response({
            "message": "Check your email for the verification code",
            "session_token": user.session_token,
            "session_expiration": str(user.session_expiration),
            "update_token": user.update_token
        })

    except Exception as e:
        # Print the error to the console
        print(f"Error in register_account: {str(e)}")

        # Return a generic failure response to the client
        return failure_response("An unexpected error occurred. Please try again.")

@app.route("/api/users/login/", methods=["POST"])
def login():
    """
    POST: Endpoint for logging in
        Requires user verification 
        Requires email/username
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
    if user is None:
        return failure_response("Invalid update token")
    return success_response({
        "session_token": user.session_token,
        "session_expiration": str(user.session_expiration),
        "update_token": user.update_token
    })

### --- Other Routes --- 
@app.route("/api/posts/")
def get_posts():
    """
    GET: Feed of ALL posts --> related to users and all of the 16 personalities.
    """
    return success_response([p.serialize() for p in Post.query.all()])

@app.route("/api/personalities/<int:personality_id>/", methods=["GET"])
def get_personality_type(personality_id):
  """
  GET: Personality by personality_id
  """
  personality = Personality.query.filter_by(id = personality_id).first()
  if personality is None:
    return failure_response("Personality not found")
  return success_response(personality.serialize()) 

@app.route("/api/users/<string:username>/personality/", methods = ["POST"])
def enter_personality_type(username):
    """
    POST: Enter personality type for specific user
    """
    body = request.get_json()
    personality_type = body.get("personality_type")
    if personality_type is None:
        return failure_response("Personality type not provided")
    personality = Personality.query.filter_by(personality_type = personality_type).first()
    if personality is None:
        return failure_response("Personality not found")
    user = User.query.filter_by(username = username).first()
    if user is None:
        return failure_response("User not found")
    if user.is_verified != True:
        return failure_response("User not verified. Please verify your account.", 403)
    user.personality_id = personality.id
    personality.number_of_each +=1
    db.session.commit()
    return success_response(user.simple_serialize())

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
    GET: Search feed for a specific user by username (case sensitive)
    """
    user = User.query.filter_by(username=username).first()
    if user is None:
        return failure_response("User not found!")
    if user.is_verified != True:
        return failure_response("The user found is not verified.")
    return success_response(user.simple_serialize())

@app.route("/api/users/<string:username>/bio/", methods = ["POST"])
def edit_user_bio(username):
  """
  Edit bio for specific user
  """
  body = request.get_json()
  text = body.get("text")
  if text is None: text = "No bio provided"
  
  user = User.query.filter_by(username=username).first()
  if user is None:
    return failure_response("No user found")
  if user.is_verified != True:
    return failure_response("User not verified. Please verify your account.", 403)
  user.bio = text
  db.session.commit()
  return success_response(user.simple_serialize())

@app.route("/api/users/<string:username>/", methods=["DELETE"])
def delete_user_personality(username):
    """
    DELETE can delete personality type from user info 
    """
    user = User.query.filter_by(username = username).first()
    if user is None:
        return failure_response("User not found!")
    if user.is_verified != True:
        return failure_response("User not verified. Please verify your account.", 403)
    personality = Personality.query.filter_by(id=user.personality_id).first()
    personality.num_of_each -=1
    user.personality_id = None
    db.session.commit()
    return success_response(user.simple_serialize())

@app.route("/api/users/<string:username>/posts/", methods=["POST"])
def create_post(username):
    """
    POST: Create post with text for the associated user
    """
    body = json.loads(request.data)
    text = body.get("text")
    if text is None:
        return failure_response("Text not provided")
    user = User.query.filter_by(username = username).first()
    if user is None:
        return failure_response("User not found!")
    if user.is_verified != True:
        return failure_response("User not verified. Please verify your account.", 403)
    post = Post(text=text, userid=user.id)
    db.session.add(post)
    db.session.commit()
    return success_response(post.serialize())

@app.route("/api/users/statistics/", methods=["GET"])
def get_statistics():
    """
    GET: Statistics for cornell community
    """
    dict = {}

    for personality in Personality.query.all():
      max = 0.0
      max_school = ""
      lst = [] #lst of dictionaries. dictionary key is school, value is % 
      for school in cornell_schools:
        num_users = len(User.query.filter_by(personality_id=personality.id, school = school, is_verified = True).all())
        if personality.number_of_each == 0: percentage = 0.0
        else: percentage = num_users / personality.number_of_each
        if percentage > max: 
          max = percentage
          max_school = school
      if max != 0.0: lst.append({f"{max_school}": max})
      else: lst.append({f"No users found for {personality.personality_type}": 0.0})
      dict[personality.personality_type] = lst
    return success_response(dict)   

# --- Survey Routes

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

@app.route("/api/surveys/<string:username>/<int:question_id>/", methods = ["POST"])
def submit_answer(username, question_id):
  """
    POST: Submit specific user's response to a specific question
  """
  question = Question.query.filter_by(id = question_id).first()
  options = QuestionOption.query.filter_by(question_id = question.id).all()
  user = User.query.filter_by(username = username).first()

  if question is None:
    return failure_response("No question found")
  if options is None:
    return failure_response("No options found")
  if user is None:
    return failure_response("No user found")
  if not user.is_verified:
    return failure_response("User not verified. Please verify your account.", 403)

  body = json.loads(request.data)
  score = body.get("score")
  # find the option that correleates with the correct option.id and score
  selected_option = next((option for option in options if option.score==score), None)
 
  if selected_option is None:
    return failure_response("No option based on user's response is found")
    
  previous_answer = UserAnswer.query.filter_by(user_id=user.id, question_id=question.id).first()
  if previous_answer is not None:
    db.session.delete(previous_answer)
  user_answer = UserAnswer(user_id=user.id, question_id=question.id, option_id=selected_option.id)
  db.session.add(user_answer)
  db.session.commit()
  return success_response(user_answer.serialize())

@app.route("/api/surveys/<string:username>/results/")
def update_user_personality_type(username):
  """
  Update user with new personality type
  """
  user = User.query.filter_by(username = username).first()
  if user is None:
    return failure_response("No user found")
  if not user.is_verified:
    return failure_response("User not verified. Please verify your account.", 403)
  personality_id = helper.find_personality(user.id)
  if personality_id is None:
    return failure_response("Failed to get personality type for the user")
  personality = Personality.query.filter_by(id = personality_id).first()
  personality.number_of_each +=1 
  user.personality_id = personality_id
  db.session.commit()
  return success_response(user.simple_serialize())

if __name__ == "__main__":
    import helper_funcs as helper
    create_app().run(host="0.0.0.0", port=8000, debug=True)