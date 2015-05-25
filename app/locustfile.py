from locust import HttpLocust, TaskSet, task
import random

class UserBehavior(TaskSet):
    def on_start(self):
        """ on_start is called when a Locust start before any task is scheduled """
        self.login()

    def login(self):
        self.client.get("/")

    @task(1)
    def index(self):
        """We test the main page (static)."""
        self.client.get("/")

    @task(2)
    def about(self):
        """We test the /about page (static)."""
        self.client.get("/about")

    @task(3)
    def matches(self):
        """We test the /match page (dynamic). Same query every time."""
        self.client.get("/match")

    @task(4)
    def query(self):
        """We test the /sarch page (dynamic). We vary the query a bit."""
        fulltext = random.choice('NYU|CTO|CIO|Government'.split('|'))
        self.client.post("/search", {'fulltext': fulltext})

    @task(5)
    def dashboard(self):
        """We test the /dashboard page (dynamic). Triggers multiple queries."""
        self.client.get("/dashboard")

class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 5000
    max_wait = 9000
