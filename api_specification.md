# API Specification

Values wrapped in `< >` are placeholders for what the field values should be. Also, be sure to read the request route carefully when you implement it.

## Expected Functionality

### Register User
`POST /api/users/register/`

Request Body:
```json
{
    "email": "hyz41@cornell.edu",
    "username": "plumshum",
    "password": "secure",
    "school": "College of Engineering"
}
```

Response: 
```json
{
    "session_token": <session_token>,
    "session_expiration": <session_expiration>,
    "update_token": <update_token>
}
```

### Login User ###
`POST /api/users/login/`

Request Body:
```json
{
    "email": "hyz41cornell.edu",
    "username": "plumshum",
    "password": "secure"
}
```

Response:
```json
{
    "session_token": <session_token>,
    "session_expiration": <session_expiration>,
    "update_token": <update_token>
}
```
*Note:*
- Either email or username can be provided. Not both at once. 


### Logout User ###
`POST /api/users/logout/`

Request Header:
| Key          | Value                    |
| ------------ | ------------------------ |
| Authorization| Bearer <session_token> |


Response:
```json
{"message": "Successfully logged out!"}
```
*Note:*
- If no user is found: `{"message": "Invalid session token"}`
- If user's session token is invalid:`{"message": "Invalid session token"}`

### Update Session ###
`POST /api/users/session/`

Request Header:
| Key          | Value                    |
| ------------ | ------------------------ |
| Authorization| Bearer <update_token> |

Response:
```json
{
    "session_token": <session_token>,
    "session_expiration": <new session_expiration>,
    "update_token": <new update_token>
}
```

### Get All Posts from Feed (WORK IN PROGRESS) ###
`GET /api/users/`

Response:
```json
{
    "posts" = [
        {
            "id": <id>,
            "text": <text>,
            "user": <username>,
            "url": <"{base_url}/{salt}.{extension}">
        },
        ...
    ]
}
```
*Note:* 
- `url` is a work in progress. the format might change a bit later. not sure if we should add `created_at`

### Get Personality Type ###
`GET /api/users/<int:personality_id>/`

Response:
```json
{
    "id": <id>,
    "personality": <personality_type>,
    "description": <description>,
    "number": <number_of_each>
}
```
*Note:*
- An example of `personality_type` is "ENTP"
- `number_of_each` represents the number of users of that personality 

### Get User by post_id ###
`GET /api/users/posts/<int:post_id>/`

Response:
```json
{
    "id": <id>,
    "username": <username>,
    "personality": <personality_type>,
    "bio": <bio>
}
```
*Note:*
- An example of `personality_type` is "ENTP"

### Get User by username ###
`GET /api/users/username/<String:username>/`
Response:
```json
{
    "id": <id>,
    "username": <username>,
    "personality": <personality_type>,
    "bio": <bio>
}
```
*Note:*
- Case Senstitive

### Delete User's Personality ###
`DELETE /api/users/<int:user_id>/`
Response:
```json
{
    "id": <id>,
    "username": <username>,
    "personality": <personality_type>,
    "bio": <bio>
}
```
*Note:*
- Frontend should call request to conduct new survey

### Create new Post (WORK IN PROGRESS) ###
`POST /api/users/<int:user_id>/`

Request Body:
```json
{
    "text": <text>,
    "url": <url>
}
```

Response:
```json
{
    "id": <id>,
    "text": <text>,
    "user": <username>,
    "url": <"{base_url}/{salt}.{extension}">
}
```
*Note:*
- `url` is a work in progress. the format might change a bit later. not sure if we should add `created_at`

### GET Statistics (WORK IN PROGRESS) ###
Response:
```json
{
    "personality_type" : {<school>, <percentage>},
    ... (16 pairs total)
}
```
*NOTE:*
- For this personality type x, % are students from y school

## Expected Routes for Survey WORK IN PROGRESS ##

### GET Specific Question w/ Options (WORK IN PROGRESS)
`GET /api/surveys/<int:question_id>/`

Response:
```json
{
  "id": <id>,
  "question_no": <question_no>,
  "question_text": <question_text>,
  "options": <json format for options>,
  "answers": self.answers.serialize() if self.answers else None
}
```
*NOTE:*
- `id` and `question_no` serve basically the same purpose. it is repetitive but helps with debugging
- `question_text` is the text for the questions
- `options` provide the two valid answers to the question. the format is
  ```json
  {
    "id": <id of option>,
    "question_id": <id of question>,
    "option_text": <text for the option>
  }
  ```
- `answers` is more for debugging purposes 

### POST Submit specific response (WORK IN PROGRESS) ###
`POST /api/surveys/<int:user_id>/<int:question_id>/`

Request Body:
```json
{
    "score": <score> 
}
```

Response:
```json
{
    "id": <id>,
    "user_id": <user_id>,
    "question_id": <question_id>,
    "option_id": <option_id> 
}
```

<<<<<<< Updated upstream
### GET SURVEY RESULTS ###
`GET /api/surveys/<int: user_id>/results/`
=======
### UPDATE USER BY SURVEY PERSONALITY TYPE ###
`UPDATE /api/surveys/<int:user_id>/`
>>>>>>> Stashed changes

Reponse:
```json
{
<<<<<<< Updated upstream
    "user_id": <user_id>,
    "probably serialize Personality model"
=======
  "id": <id>,       
  "username": <username>,
  "personality": <UPDATED personality type>,
  "bio": <bio>
>>>>>>> Stashed changes
}
```