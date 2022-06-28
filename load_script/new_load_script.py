import random
import time
from multiprocessing.pool import ThreadPool

import requests
from faker import Faker


class AppLoader:
    # IP = "52.148.211.104:8000"
    IP = "0.0.0.0:8000"
    fake = Faker()
    REGISTER_URL = f"http://{IP}/register/"
    TOKEN_URL = f"http://{IP}/api/token/"
    EXPENSES_URL = f"http://{IP}/api/v1/expenses/"
    CATEGORIES_URL = f"http://{IP}/api/v1/categories/"
    TOTAL_EXPENSES_URL = f"http://{IP}/api/v1/expenses/total/"

    @classmethod
    def create_user(cls):
        username = cls.fake.user_name()
        email = cls.fake.email()
        password = cls.fake.password()
        data = {"username": username, "email": email, "password": password}
        response = requests.post(cls.REGISTER_URL, data=data)
        if response.status_code == 201:
            with open("users.txt", "a+", encoding="utf-8") as file:
                file.write(f"{username} - {email} - {password}\n")
            print(f"user {data} has been created")
        else:
            print("something is wrong")

    def get_headers(self):
        with open("users.txt", "r", encoding="utf-8") as file:
            user_data = random.choice(file.read().split("\n")[:-1]).split(
                " - "
            )
            email = user_data[1]
            password = user_data[2]
            login_data = {
                "email": email,
                "password": password,
            }
            json_response = requests.post(
                self.TOKEN_URL, data=login_data
            ).json()
            token = json_response.get("access")
            return {"Authorization": f"Bearer {token}"}

    def get_random_category(self):
        json_response = requests.get(
            url=self.CATEGORIES_URL, headers=self.get_headers()
        ).json()
        category = random.choice(json_response)["id"]
        return category

    def add_new_category(self):
        data = {"name": self.fake.bothify(text="Category: ????????")}
        json_response = requests.post(
            url=self.CATEGORIES_URL, data=data, headers=self.get_headers()
        )
        if json_response.status_code == 201:
            print(f"record {json_response.json()} has been created")
        else:
            print("something is wrong")

    def add_expense(self):
        data = {
            "category": self.get_random_category(),
            "amount": random.randint(1, 500),
            "short_description": "test_description",
            "currency": random.choice(["USD", "BYN", "UAH"]),
        }
        json_response = requests.post(
            url=self.EXPENSES_URL, data=data, headers=self.get_headers()
        )
        if json_response.status_code == 201:
            print(f"record {json_response.json()} has been created")
        else:
            print("something is wrong")

    def get_to_expenses(self):
        response = requests.get(
            url=self.EXPENSES_URL, headers=self.get_headers()
        )
        if response.status_code == 200:
            print("get request to expenses")

    def get_to_total_expenses(self):
        response = requests.get(
            url=self.TOTAL_EXPENSES_URL, headers=self.get_headers()
        )
        if response.status_code == 200:
            print("get request to total expenses")

    def load(self):
        try:
            while True:
                self.create_user()
                for _ in range(100):
                    self.add_expense()
                for _ in range(10):
                    self.add_new_category()
                for _ in range(10):
                    self.get_to_expenses()
                for _ in range(10):
                    self.get_to_total_expenses()
        except requests.exceptions.RequestException:
            print("no connection to server")
            time.sleep(10)
            self.load()


if __name__ == "__main__":
    instances = [AppLoader() for _ in range(8)]
    pool = ThreadPool(8)
    pool.map(lambda x: x.load(), instances)
    pool.close()
    pool.join()
