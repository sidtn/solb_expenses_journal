import random
import threading

import requests
from faker import Faker

fake = Faker()


def create_user():
    url = "http://0.0.0.0:8000/register/"
    username = fake.user_name()
    email = fake.email()
    password = fake.password()
    data = {"username": username, "email": email, "password": password}
    response = requests.post(url, data=data)
    if response.status_code == 201:
        with open("users.txt", "a+", encoding="utf-8") as file:
            file.write(f"{username} - {email} - {password}\n")
        print(f"user {data} created")
    else:
        print("something wrong")


def login_user_and_add_expense():
    url_login = "http://0.0.0.0:8000/auth/login/"
    url_expense = "http://0.0.0.0:8000/api/v1/expenses/"

    session = requests.Session()
    r = session.get(url_login)
    csrf_token = r.cookies["csrftoken"]

    with open("users.txt", "r", encoding="utf-8") as file:
        user_data = random.choice(file.read().split("\n")[:-1]).split(" - ")
        email = user_data[1]
        password = user_data[2]
        login_data = {
            "username": email,
            "password": password,
            "csrfmiddlewaretoken": csrf_token,
        }
        login_response = session.post(url_login, data=login_data)
        add_expense_data = {
            "amount": random.randint(1, 1000),
            "category": random.randint(1, 42),
            "short_description": "test description",
            "csrfmiddlewaretoken": login_response.cookies["csrftoken"],
        }
        response = session.post(url_expense, data=add_expense_data)
        if response.status_code == 201:
            print(f"{add_expense_data} has been added")


def main():
    while True:
        for _ in range(3):
            create_user()
        for _ in range(50):
            login_user_and_add_expense()


if __name__ == "__main__":
    for i in range(10):
        my_thread = threading.Thread(target=main)
        my_thread.start()
