import random
from locust     import HttpUser, task, between

class FakeUsers(HttpUser):
    wait_time = between(1, 3)

    @task(5)
    def view_items(self):
        self.client.get("/items", name="/items (Main List)")

    @task(2)
    def search_item(self):
        search_terms = ["Lorem", "Ipsum", "Dolor", "Sit", "Amet"]
        term = random.choice(search_terms)
        with self.client.get(f"/items?name={term}", name="/items?name=[term]", catch_response=True) as response:
            if response.status_code == 200 or 404:
                response.success()
            else:
                response.failure(f"UNEXPECTED STATUS CODE: {response.status_code}")

    @task(3)
    def view_page(self):
        random_page = random.randint(1, 100)
        self.client.get(f"/items?page={random_page}", name="/items?page=[random]")

    @task(1)
    def stress_test_heavy_query(self):
        self.client.get("/items/?name=ThisIsNeverExistProduct", name="/items/?name=[empty]")