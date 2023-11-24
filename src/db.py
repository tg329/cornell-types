"""
Models: Users, Personality_Type, (Post?), Questions (with text and options, Answers
"""
#NOTE: need Survey model 
#NOTE: when creating user in db(when they first sign up) need school, username too in addition to already configured email and password in create_user in users_dao.py
#NOTE: need an Asset model for the images


from flask_sqlalchemy import SQLAlchemy
import bcrypt
import datetime
import hashlib
import os
import base64 #for encoding images
import boto3
import io
from io import BytesIO
from mimetypes import guess_extension, guess_type #for guessing the file extension
from PIL import Image  # Correct import statement
import random #for generating random numbers.censor some file names
import re #for regular expressions
import string #for string manipulation

db = SQLAlchemy()


#TODO: check email field has @cornell.edu 
#TODO: class list for all schools 
#TODO: research email verification SQLAlchemy
class User(db.Model):
  """
  User Model
  """

  __tablename__ = "user"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)

  #user info.
  username = db.Column(db.String, nullable=False, unique=True)
  password_digest = db.Column(db.String, nullable=False)
  email = db.Column(db.String, nullable=False)
  posts = db.relationship("Post", cascade="delete")
  bio = db.Column(db.String, nullable=True)
  school = db.Column(db.String, nullable=False)
  personality_id = db.Column(db.String, db.ForeignKey("personality.id"), nullable=True)
  #personality=db.Column(db.String, nullable=True)
  verification_code = db.Column(db.String(10))
  is_verified = db.Column(db.Boolean, default=False)
  answers=db.relationship("UserAnswer", backref="user", lazy=True)
  is_active = db.Column(db.Boolean, default=True)
  #session info.
  session_token = db.Column(db.String, nullable=False, unique=True)
  session_expiration = db.Column(db.DateTime, nullable=False)
  update_token = db.Column(db.String, nullable=False, unique=True)

  def __init__(self, **kwargs):
      """
      Initializes a new User object.
      """
      self.username = kwargs.get("username", "")
      self.password_digest = bcrypt.hashpw(kwargs.get("password").encode("utf-8"), bcrypt.gensalt(rounds=13))
      self.email = kwargs.get("email", "")
      self.school = kwargs.get("school", "")
      self.verification_code = kwargs.get("verification_code", "")
      self.bio = "No bio provided"
      self.renew_session()

  def get_id(self):
    """
    Returns the id of the user.
    """
    return self.id
    
  def _urlsafe_base_64(self):
    """
    Randomly generates hashed tokens (used for session/update tokens)
    """
    return hashlib.sha1(os.urandom(64)).hexdigest()

  def renew_session(self):
    """
    Renews the session token and expiration time of session to be a day from now and creates new update token.
    """
    self.session_token=self._urlsafe_base_64()
    self.session_expiration=datetime.datetime.now() + datetime.timedelta(days=1)
    self.update_token=self._urlsafe_base_64()

  def verify_password(self, password):
    """
    Verifies the password of the user against the password_digest.
    """
    return bcrypt.checkpw(password.encode("utf-8"), self.password_digest)

  def verify_session_token(self, session_token):
    """
    Verifies the session token of the user against the session_token.
    """
    return self.session_token == session_token and datetime.datetime.now() < self.session_expiration

  def verify_update_token(self, update_token):
    """
    Verifies the update token of the user against the update_token.
    """
    return self.update_token == update_token

  def serialize(self):
      """
      Serializes a User object into a dictionary.
      """
      return {
          "id": self.id,
          
          "username": self.username,
          "school": self.school,
          "personality": Personality.query.filter_by(id=self.personality_id).first().personality_type,
          "bio": self.bio,
          "email": self.email,
          "password": self.password,
          "posts": [p.simple_serialize() for p in self.posts],
          
      }

  def simple_serialize(self):
      """
      Serializes User object into a dictionary with only id, username, personality, bio.
      """
      return {
          "id": self.id,       
          "username": self.username,
          "personality":Personality.query.filter_by(id=self.personality_id).first().personality_type,
          "bio": self.bio,
      }
  def optional_serialize(self):
    return {
        "id": self.id,
        "username": self.username,
        "answers": [answer.serialize() for answer in self.answers],
    }
    
class Post(db.Model):
  """
  Post Model
  """

  __tablename__ = "post"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  text = db.Column(db.String, nullable=False)
  
  userid = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
  #can have image col (for that rectangle with a cross mark in design)??

  def __init__(self, **kwargs):
      """
      Initializes a new Post object.
      """
      self.text = kwargs.get("text", "")
      self.userid=kwargs.get("user_id", "")

  def serialize(self):
      """
      Serializes a Post object into a dictionary.
      """
      return {
          "id": self.id,
          "text": self.text,
          
          "user":User.query.filter_by(id=self.userid).first().username
      }
  #need simple serialize??

class Personality(db.Model):
  """
  Personality Model
  """

  __tablename__ = "personality"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  personality_type = db.Column(db.String, nullable=False)
  number_of_each= db.Column(db.Integer, nullable=False)
  users=db.relationship("User", cascade="delete")
   
  #TODO: add description 

  def __init__(self, **kwargs):
      """
      Initializes a new Personality object.
      """
      self.personality_type= kwargs.get("personality", "")
      self.number_of_each=kwargs.get("number_of_each", "")

  def serialize(self):
      """
      Serializes a Personality object into a dictionary.
      """
      return {
          "id": self.id,
          "personality": self.personality_type,

          "number":self.number_of_each,
          #need the image (most imp)
      }

#split into Question{constant model}  Response Model



# class Survey(db.Model):
#   """
#   Survey Model
#   """
#   __tablename__ = "survey"
#   id = db.Column(db.Integer, primary_key=True)
#   user_id = db.Column(db.Integer, db.ForeignKey("user.id"))
#   questions = db.Column(db.JSON, nullable=False)
#   responses = db.Column(db.JSON, nullable=True) #TODO: DICTIONARY key: "E" value: # of E's

#   def __init__(self, **kwargs):
#       self.user_id = kwargs.get("user_id")
#       self.questions = kwargs.get("questions")
#       #self.responses = kwargs.get("responses")

#   def serialize(self):
#       return {
#           "id": self.id,
#           "user_id": self.user_id,
#           "questions": self.questions,
#           "responses": self.responses,
#       }

#   #TODO: make each questions type odd 
#   def find_personality(self):
#       """
#       Finds personality type from responses
#       """
#       #figure out how many E, I, N,S,T,F,J,P
#       personality = ""
#       if self.responses["E"] > self.responses["I"]:
#           personality += "E"
#       else:
#           personality += "I"
#       if self.responses["N"] > self.responses["S"]:
#           personality += "N"
#       else:
#           personality += "S"
#       if self.responses["T"] > self.responses["F"]:
#           personality += "T"
#       else:
#           personality += "F"
#       if self.responses["J"] > self.responses["P"]:
#           personality += "J"
#       else:
#           personality += "P"
#       return personality

#new models
class Question(db.Model):
  """
  Question Model
  """
  __tablename__ = "questions"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  question_no = db.Column(db.Integer, nullable=False)
  question_text = db.Column(db.String, nullable=False)
  options = db.relationship("QuestionOption", backref="question", lazy=True)
  answers = db.relationship("UserAnswer", backref="question", uselist=False, lazy=True) #Hannah Note: more for debugging? 

  def __init__(self, question_no, question_text):
      self.question_no = question_no
      self.question_text = question_text

  def serialize(self):
      return {
          "id": self.id,
          "question_no": self.question_no,
          "question_text": self.question_text,
          "options": [option.serialize() for option in self.options],
          "answers": self.answers.serialize() if self.answers else None,
      }

class QuestionOption(db.Model):
  """
  QuestionOption Model
  """
  __tablename__ = "question_options"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
  option_text = db.Column(db.String, nullable=False)
  score=db.Column(db.String, nullable=False)

  def __init__(self, question_id, option_text):
      self.question_id = question_id
      self.option_text = option_text

  def serialize(self):
      return {
          "id": self.id,
          "question_id": self.question_id,
          "option_text": self.option_text,
          "score": self.score
      }


class UserAnswer(db.Model):
  """
  UserAnswer Model
  """
  __tablename__ = "user_answers"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
  question_id = db.Column(db.Integer, db.ForeignKey("questions.id"))
  option_id = db.Column(db.Integer, db.ForeignKey("question_options.id"))
 # final_answer = db.Column(db.String, nullable=True)

  def __init__(self, user_id, question_id, option_id):
      self.user_id = user_id
      self.question_id = question_id
      self.option_id = option_id
      #self.final_answer = final_answer

  def serialize(self):
      return {
          "id": self.id,
          "user_id": self.user_id,
          "question_id": self.question_id,
          "option_id": self.option_id
         # "final_answer": self.final_answer,
      }

#encode the image in base64 
#send the encode to AMAZON WEB SERIVCES to store the image 
#retrive the image url link from amazon web services
#url link stored in model


#NOTE: a Asset model for the images copied from demo. Not sure if needed 
class Asset(db.model):
  __tablename__ = "asset"
  id = db.Column(db.Integer, primary_key=True, autoincrement = True)
  base_url = db.Column(db.String, nullable=True)
  salt = db.Column(db.String, nullable=False) #a tool to make the file name unique/random
  extension = db.Column(db.String, nullable=False)
  width = db.Column(db.Integer, nullable=False)
  height = db.Column(db.Integer, nullable=False)
  created_at = db.Column(db.DateTime, nullable=False)

  def __init__(self, **kwargs):
    """Initialize a new Asset"""
    self.create(kwargs.get("image_data"))
  
  def serialize(self):
    """
    Returns a dictionary representation of the Asset
    """
    return {
        "url": f"{self.base_url}/{self.salt}.{self.extension}",
        "created_at": str(self.created_at)
    }
  def create(self, image_data):
    """
    Given an image in base64 encoding, does the following:
    1. Rejects the image if it is not a supported filename
    2. Generate a random string for the image filename 
    3. Decodes the image and attemps to upload to AWS
    """
    #if amazon goes down, we can still run our app
    try:
        ext = guess_extension(guess_type(image_data)[0])[1:]
        if ext not in EXTENSIONS:
            raise Exception(f"Extesnsion {ext} not supported!")
        salt = "".join(
            random.SystemRandom().choice(
                string.ascii_uppercase + string.digits
            )
            for _ in range(16)
        )
        # now, we only want the very ugly encoding part, so trim everything elses out
        img_str = re.sub("^data:image/.+;base64,", "", image_data)
        img_data = base64.b64decode(img_str)
        img = Image.open(io.BytesIO(img_data))
  
        self.base_url = S3_BASE_URL
        self.salt = salt
        self.extension = ext
        self.wiidth = img.width
        self.height = img.height
        self.create_at = datetime.datetime.now()
  
        img_filename = f"{self.salt}.{self.extension}"
        self.upload(img, img_filename)
    except Exception as e:
        print(f"Error when creating image: {e}")
  
  def upload(self, img, img_filename):
      """
      Uploads the image to AWS
      """
      try:
          #save image into temporary
          img_temp_loc = f"{BASE_DIR/{img_filename}}"
          img.save(img_temp_loc)
    
          #upload to AWS bucket
          s3_client = boto3.client("s3")
          s3_client.upload_file(img_temp_loc,S3_BUCKET_NAME,img_filename)
    
          s3_resource = boto3.resource("s3") #for manipulating the image
          object_acl = s3_resource.ObjectAcl(S3_BUCKET_NAME, img_filename)
          object_acl.put(ACL = "public-read") #anybody can view image
    
          os.remove(img_temp_loc) #remove image from temporary location
    
      except Exception as e:
          print(f"Error when uploading image: {e}")