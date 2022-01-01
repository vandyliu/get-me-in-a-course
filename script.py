import json
import os
import sys
import time
import random

from enum import Enum

from fake_useragent import UserAgent
import undetected_chromedriver as uc
import boto3
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class SeatType(Enum):
    ALL = "all"
    GENERAL = "general"

def send_notification(subject, course_no, section, phone_number):
    if (
        os.getenv("AWS_ACCESS_KEY_ID")
        and os.getenv("AWS_SECRET_ACCESS_KEY")
        and phone_number
    ):
        client = boto3.client(
            "sns",
            region_name="us-west-2",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )
        message = "COURSE AVAILABLE!: {} {} {} has a spot available.".format(
            subject, course_no, section
        )
        client.publish(
            Message=json.dumps({"default": message}),
            Subject="Course Available",
            MessageStructure="json",
            PhoneNumber=phone_number,
        )

def get_course_link(subject, course_no, section):
    url = "https://courses.students.ubc.ca/cs/courseschedule?pname=subjarea&tname=subj-section&dept={}&course={}&section={}".format(
        subject, course_no, section
    )
    return url


def remove_course_from_file(courses_file, subject, course, section):
    string = "{} {} {}".format(subject, course, section)
    with open(courses_file, "r+") as f:
        lines = f.readlines()
        f.seek(0)
        for l in lines:
            if string not in l:
                f.write(l)
        f.truncate()


def load_courses(file_path):
    courses = []
    with open(file_path, "r") as f:
        for line in f:
            courses.append(line.rstrip())
    return courses


def setup():
    if len(sys.argv) > 1:
        person = sys.argv[1]
    else:
        person = "vandy"

    print(f"person: {person}")
    load_dotenv(f"./.envs/.{person}")
    load_dotenv()
    print(f"user: {os.getenv('USER')}")


class Driver:
    def __init__(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--enable-javascript")
        self.driver = uc.Chrome(options=chrome_options)
    
        self.driver.implicitly_wait(10)

    def click_button(self, element):
        self.driver.execute_script("arguments[0].click();", element)

    ## Change to SeatType.ALL for restricted seating and SeatType.GENERAL for general seating
    def course_has_space(self, url, type_of_seats=SeatType.GENERAL):
        ua = UserAgent()
        userAgent = ua.random
        print(userAgent)
        headers = {'User-Agent': str(userAgent)}
        
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.content, features="html.parser")

        if type_of_seats == SeatType.ALL:
            look_for = "Total Seats Remaining:"
        elif type_of_seats == SeatType.GENERAL:
            look_for = "General Seats Remaining:"
        seats_remaining = soup.find("td", string=look_for).next_sibling()[0].string
        return int(seats_remaining) > 0

    def login(self, url):
        user = os.getenv("USER")
        pw = os.getenv("PASSWORD")
        self.driver.get(url)

        try:
            self.driver.find_element(By.XPATH,'//*[@id="cwl-logout"]/form/input')
            # Logged in
        except NoSuchElementException as e:
            # Not logged in
            login_button = self.driver.find_element(
                By.XPATH, '//*[@id="cwl"]/form/input'
            )
            self.click_button(login_button)

            time.sleep(random.randint(5, 10))

            user_elem = self.driver.find_element(By.XPATH, '//*[@id="username"]')
            user_elem.clear()
            user_elem.send_keys(user)

            pw_elem = self.driver.find_element(By.XPATH, '//*[@id="password"]')
            pw_elem.clear()
            pw_elem.send_keys(pw)

            submit_button = self.driver.find_element(By.NAME, "submit")
            self.click_button(submit_button)
            
        # Needs to successfully login
        time.sleep(5)
        return True

    def register_course(self, url):
        self.driver.get(url)
        reg_button = self.driver.find_element(By.XPATH, "/html/body/div[2]/div[4]/a[2]")
        self.click_button(reg_button)
        print("Register button pressed")
        time.sleep(5)

    def is_register_button_disabled(self, url):
        self.driver.get(url)
        reg_button = self.driver.find_element(By.XPATH, "/html/body/div[2]/div[4]/a[2]")
        # Register button should be disabled now because we are registered
        return "btn-disabled" in reg_button.get_attribute("class")

    def quit(self):
        print("Quitting")
        self.driver.quit()


def main():
    courses_file = "./courses.txt"
    setup()
    f = Driver()
    courses = load_courses(courses_file)
    for course_name in courses:
        subject, course_no, section = tuple(course_name.split())
        url = get_course_link(subject, course_no, section)
        time.sleep(random.randint(30,60))
        if f.course_has_space(url):
            print("There is space in {} {} {}.".format(subject, course_no, section))
            time.sleep(random.randint(10, 20))
            f.login(url)
            time.sleep(random.randint(10,20))
            f.register_course(url)
            if f.is_register_button_disabled(url):
                print(
                    "Should have registered in {} {} {}.".format(
                        subject, course_no, section
                    )
                )
                remove_course_from_file(courses_file, subject, course_no, section)
            else:
                print(
                    "Should have registered in {} {} {} but likely failed.".format(
                        subject, course_no, section
                    )
                )
            send_notification(subject, course_no, section, os.getenv("PHONE_NUMBER"))
        else:
            print("No space in {} {} {}.".format(subject, course_no, section))
    f.quit()


if __name__ == "__main__":
    while(True):
        main()
        time.sleep(random.randint(120,180))