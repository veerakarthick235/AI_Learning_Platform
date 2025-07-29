import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
from db import get_db_connection

load_dotenv()

genai.configure(api_key=os.environ["GEMINI_API_KEY"])

def get_quiz(course, topic, subtopic, description):
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 20000,
        "response_mime_type": "application/json",
    }

    safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    ]

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        safety_settings=safety_settings,
        generation_config=generation_config,
        system_instruction="""You are an AI agent who provides quizzes to test understanding of user on a topic. The quiz will be based on topic, subtopic and the description of subtopic which describes what exactly to learn. Output questions in JSON format. The questions must be Multiple Choice Questions, can include calculation if necessary. Decide the number of questions based on description of the subtopic. Try to make as many questions as possible. Include questions that require deep thinking. output in format {questions:[ {question: "...", options:[...], answerIndex:"...", reason:"..."}]}"""
    )

    chat_session = model.start_chat(history=[])

    response = chat_session.send_message(
        f'The user is learning the course {course}. In the course the user is learning topic "{topic}". Create quiz on subtopic "{subtopic}". The description of the subtopic is "{description}".',
        stream=False,
    )

    response_text = response.text
    print(response_text)

    try:
        questions_json = json.loads(response_text)
    except json.JSONDecodeError:
        questions_json = {"questions": []}

    # Store in MySQL
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO quiz_logs (course, topic, subtopic, description, questions_json)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (course, topic, subtopic, description, json.dumps(questions_json))
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"MySQL Insert Error: {e}")

    return questions_json
