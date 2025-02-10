from dotenv import load_dotenv
import os
import requests
import json
import time
from discord_webhook import DiscordWebhook

load_dotenv()

CANVAS_BASE_URL = os.getenv("CANVAS_BASE_URL")
CANVAS_TOKEN = os.getenv("CANVAS_TOKEN")
USER_ID = os.getenv("USER_ID")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

CONFERENCE_CACHE_FILE = ".conference_cache.json"

COURSES_API = "https://{base_url}/api/v1/courses?per_page=100".format(base_url=CANVAS_BASE_URL)
CONFERENCES_API = "https://{base_url}/api/v1/courses/{course_id}/conferences".format(base_url=CANVAS_BASE_URL, course_id="{course_id}")

COURSES_PARAMETERS = {
    "per_page": 100,
    "enrollment_type": "student",
    "enrollment_state": "active",
    "state": "complete"
}

HEADERS = {"Authorization": "Bearer {key}".format(key=CANVAS_TOKEN)}

course_response = requests.get(COURSES_API, headers=HEADERS, params=COURSES_PARAMETERS)
courses_data = json.loads(course_response.text)

conference_cache = {}
try:
    with open(CONFERENCE_CACHE_FILE, 'r') as file:
        conference_cache = json.load(file)
except:
    print("No conference cache file, creating")
    file = open(CONFERENCE_CACHE_FILE, "w")
    file.write("{}")
    file.close()

def queryOngoingConferences():
    conference_detected = False

    for course in courses_data:
        course_id = course["id"]

        conference_url = CONFERENCES_API.format(course_id=course_id)
        conference_response = requests.get(conference_url, headers=HEADERS)
        conferences_rawdata = json.loads(conference_response.text)

        if str(course_id) not in conference_cache:
            print(conference_cache)
            conference_cache[str(course_id)] = ""

        if "conferences" in conferences_rawdata:
            conferences_data = conferences_rawdata["conferences"]

            latest_conference = conferences_data[0]
            conference_id = latest_conference["id"]

            if (conferences_data[0]["ended_at"] is None) and (conferences_data[0]["started_at"] is not None):
                print(course["name"], "conference in progress!")
                conference_detected = True
                if (conference_cache[str(course_id)] != str(conference_id)):
                    print(conference_cache[str(course_id)], str(conference_id))
                    conference_cache[str(course_id)] = str(conference_id)
                    webhook = DiscordWebhook(url=WEBHOOK_URL, content="{course_name} conference in progress".format(course_name=course["name"]))
                    webhook.execute()


    return conference_detected

try:
    webhook = DiscordWebhook(url=WEBHOOK_URL, content="Conference notifier started")
    webhook.execute()

    while True:
        if not queryOngoingConferences():
            print("No ongoing conferences found")
        time.sleep(2)
finally:
    with open(CONFERENCE_CACHE_FILE, 'w') as file:
        json.dump(conference_cache, file)
    
    webhook = DiscordWebhook(url=WEBHOOK_URL, content="Conference notifier stopped")
    webhook.execute()