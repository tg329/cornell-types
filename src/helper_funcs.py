
from questions import question_data
from db import db
from db import Question, QuestionOption, UserAnswer, Personality

def create_survey_questions():
  """
  Creates survey questions and options
  """
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


def create_personalities():
    """
    Creates personalities with descriptions and adds them to the database
    """
    mbti_types = [
    "ISTJ", "ISFJ", "INFJ", "INTJ",
    "ISTP", "ISFP", "INFP", "INTP",
    "ESTP", "ESFP", "ENFP", "ENTP",
    "ESTJ", "ESFJ", "ENFJ", "ENTJ"
    ]

    mbti_descriptions = [
        "The Inspector - ISTJs are quiet, serious individuals who are responsible, reliable, and practical...",
        "The Protector - ISFJs are warm, friendly, and responsible individuals who value harmony and cooperation...",
        "The Counselor - INFJs are insightful, empathetic, and organized individuals. They possess a deep understanding of human emotions and motivations...",
        "The Mastermind - INTJs are independent, original thinkers who are analytical, determined, and visionary...",
        "The Craftsman - ISTPs are tolerant, analytical, and hands-on individuals who enjoy exploring how things work...",
        "The Composer - ISFPs are gentle, sensitive, and artistic individuals who appreciate beauty and harmony...",
        "The Healer - INFPs are idealistic, sensitive, and caring individuals with a deep commitment to their values...",
        "The Architect - INTPs are innovative, logical, and curious individuals who enjoy exploring abstract concepts and ideas...",
        "The Dynamo - ESTPs are energetic, outgoing, and adventurous individuals who thrive on action and excitement...",
        "The Performer - ESFPs are outgoing, lively, and fun-loving individuals who enjoy being the center of attention...",
        "The Champion - ENFPs are enthusiastic, creative, and optimistic individuals who are driven by a desire for exploration and inspiration...",
        "The Visionary - ENTPs are inventive, enthusiastic, and analytical individuals who enjoy exploring new ideas and possibilities...",
        "The Supervisor - ESTJs are practical, realistic, and decisive individuals who value order, efficiency, and organization...",
        "The Provider - ESFJs are warm, outgoing, and conscientious individuals who value connection and service to others...",
        "The Teacher - ENFJs are warm, empathetic, and responsible individuals who are dedicated to the personal growth of those around them...",
        "The Commander - ENTJs are strategic, assertive, and confident individuals who excel in leadership roles. They are goal-oriented and enjoy taking charge to achieve results..."
    ]

    for i in range(0,16):
        personality = Personality(personality_type = mbti_types[i], description = mbti_descriptions[i])
        db.session.add(personality)
    db.session.commit()


def find_personality(user_id):
  """
  Finds personality type from responses
  """
  answers = UserAnswer.query.filter_by(user_id = user_id).all()
  if len(answers) != 36:
    print("ran into error")
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
  
  for user_answer in answers: 
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
  personality = Personality.query.filter_by(personality_type = personality_type).first()
  return personality.id