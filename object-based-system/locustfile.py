from locust import HttpUser, task, between

class ChatUser(HttpUser):
    wait_time = between(1, 3)  # seconds between tasks

    def on_start(self):
        """
        Called when a simulated user starts.
        We register and login once before sending messages.
        """
        self.username = f"user{self.environment.runner.user_count}"  # unique usernames
        self.password = "pass"

        # Register
        self.client.post("/register", data={
            "username": self.username,
            "password": self.password
        })

        # Login
        self.client.post("/login", data={
            "username": self.username,
            "password": self.password
        })

    @task
    def send_message(self):
        """
        Send a chat message (repeated during the test).
        Adjust 'room_id' if needed.
        """
        self.client.post("/send", data={
            "room_id": "room1",
            "username": self.username,
            "text": "hello from locust"
        })
