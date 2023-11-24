#TODO: put in a separate file 


#helper function

# Create questions and options at beginning of app
def create_survey_questions():
  for q_data in question_data:
      question = Question(question_no=q_data["question_no"], question_text=q_data["question_text"])
      db.session.add(question)
      options = [
          QuestionOption(question_id=question.id, option_text=q_data["options"][i], score=q_data["score"][i])
          for i in range(0,2)
      ]
      db.session.add_all(options)
      question.options.extend(options)
  db.session.commit()

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

def find_personality(user_id):
  """
  Finds personality type from responses
  """
  user_answers= UserAnswer.query.filter_by(user_id=user_id).all()

  #might to .count() intead for this
  if len(user_answers) != 36:
    return None
  
  personality_type = ""
  count_E=0
  count_I=0
  count_N=0
  count_S=0
  count_T=0
  count_F=0
  count_P=0
  count_J=0  
  
  for user_answer in user_answers: 
    option = QuestionOption.query.filter_by(id = user_answer.option_id).first()
    if option.score == "E":
        count_E+=1
    elif option.score == "I":
        count_I+=1
    elif option.score == "N":
        count_N+=1
    elif option.score == "S":
        count_S+=1
    elif option.score == "T":
        count_T+=1
    elif option.score == "F":
        count_F+=1
    elif option.score == "P":
        count_P+=1
    elif option.score == "J":
        count_J+=1
  
    if count_E > count_I:
        personality_type += "E"
    else:
        personality_type += "I"
    if count_N > count_S:
        personality_type += "N"
    else:
        personality_type += "S"
    if count_T > count_F:
        personality_type += "T"
    else:
        personality_type += "F"
    if count_J > count_P:
        personality_type += "J"
    else:
        personality_type += "P"
  
  return personality_type