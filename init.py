from dotenv import load_dotenv
import os
import requests
import json
import time

load_dotenv()

CANVAS_TOKEN = os.getenv("CANVAS_TOKEN")
USER_ID = os.getenv("USER_ID")

COURSES_API = "https://tip.instructure.com/api/v1/courses?per_page=100"
CONFERENCES_API = "https://tip.instructure.com/api/v1/courses/{course_id}/conferences"

COURSES_PARAMETERS = {
    "per_page": 100,
    "enrollment_type": "student",
    "enrollment_state": "active",
    "state": "complete"
}

HEADERS = {"Authorization": "Bearer {key}".format(key=CANVAS_TOKEN)}

course_response = requests.get(COURSES_API, headers=HEADERS, params=COURSES_PARAMETERS)
courses_data = json.loads(course_response.text)

def queryOngoingConferences():
    for course in courses_data:
        course_id = course["id"]

        conference_url = CONFERENCES_API.format(course_id=course_id)
        conference_response = requests.get(conference_url, headers=HEADERS)
        conferences_rawdata = json.loads(conference_response.text)

        if "conferences" in conferences_rawdata:
            conferences_data = conferences_rawdata["conferences"]

            latest_conference = conferences_data[0]
            if (conferences_data[0]["ended_at"] is None) and (conferences_data[0]["started_at"] is not None):
                print(course["name"], "conference in progress!")

while True:
    queryOngoingConferences()
    time.sleep(2)