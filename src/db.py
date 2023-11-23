"""
Models: Users, Personality_Type, (Post?)
"""
#NOTE: need Survey model 
#NOTE: when creating user in db(when they first sign up) need school, username too in addition to already configured email and password in create_user in users_dao.py


from flask_sqlalchemy import SQLAlchemy
import bcrypt
import datetime
import hashlib
import os
import base64 #for encoding images
#import boto3
import io
from io import BytesIO
from mimetypes import guess_extension, guess_type #for guessing the file extension
#from PIL import Image  # Correct import statement
import random #for generating random numbers.censor some file names
import re #for regular expressions
import string #for string manipulation
db = SQLAlchemy()


class User(db.Model):
  """
  User Model
  """

  __tablename__ = "user"
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)

  #user info.
  username = db.Column(db.String, nullable=False)
  password_digest = db.Column(db.String, nullable=False)
  email = db.Column(db.String, nullable=False)
  #posts = db.relationship("Post", cascade="delete")
  bio = db.Column(db.String, nullable=True)
  school = db.Column(db.String, nullable=False)
  #personality_id = db.Column(db.String, db.ForeignKey("personality.id"), nullable=True)
  verification_code = db.Column(db.String(10))
  is_verified = db.Column(db.Boolean, default=False)
  #personality=db.Column(db.String, nullable=True)
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
          #"personality": Personality.query.filter_by(id=self.personality_id).first().personality_type,
          "bio": self.bio,
          "email": self.email,
          "password": self.password,
          #"posts": [p.simple_serialize() for p in self.posts],
          
      }

  def simple_serialize(self):
      """
      Serializes course object into a dictionary with only id, code and name.
      """
      return {
          "id": self.id,
          
          "username": self.username,
          #"personality":Personality.query.filter_by(id=self.personality_id).first().personality_type,
          "bio": self.bio,
      }
