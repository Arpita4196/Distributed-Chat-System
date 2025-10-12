import random, string, time
from urllib.parse import urlencode
from locust import FastHttpUser, task, between

def rand_email():
    sfx = f"{int(time.time()*1000)}{random.randint(1000,9999)}"
    return f"user_{sfx}@test.local"

def rand_text():
    n = random.randint(5, 20)
    return "".join(random.choices(string.ascii_letters + string.digits + " ", k=n))

ROOM_ID = "locust_test"

class ChatUser(FastHttpUser):
    """
    Simulates a real chat user hitting the FastAPI UI Service on port 8080.
    """
    wait_time = between(0.5, 1.5)

    def on_start(self):
        """Called when a simulated user starts — registers, logs in, and joins a room."""
        self.email = rand_email()
        self.password = "secret"
        self.last_seen = 0

        self.client.post("/api/register",
                         json={"email": self.email, "password": self.password, "display_name": self.email.split('@')[0]},
                         name="register")

        self.client.post("/api/login",
                         json={"email": self.email, "password": self.password},
                         name="login")

        self.client.post("/api/room/create",
                         json={"room_id": ROOM_ID, "name": ROOM_ID.capitalize()},
                         name="room_create")

        self.client.post("/api/room/join",
                         json={"room_id": ROOM_ID},
                         name="room_join")

    @task(4)
    def send_message(self):
        """Send a random message to the chat room."""
        msg = rand_text()
        self.client.post("/api/message/append",
                         json={"room_id": ROOM_ID, "text": msg},
                         name="send_message")

    @task(2)
    def fetch_history(self):
        """Fetch new messages since last_seen offset."""
        q = urlencode({"room_id": ROOM_ID, "from_offset": self.last_seen + 1, "limit": 50})
        self.client.get(f"/api/message/list?{q}", name="fetch_history")
