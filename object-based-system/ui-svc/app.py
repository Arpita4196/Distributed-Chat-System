import grpc
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import gateway_pb2, gateway_pb2_grpc
import user_pb2, user_pb2_grpc
import message_pb2, message_pb2_grpc

app = Flask(__name__)
app.secret_key = "supersecret"

# === gRPC channel to gateway-svc ===
channel = grpc.insecure_channel("gateway-svc:50051")
gateway_stub = gateway_pb2_grpc.GatewayServiceStub(channel)

# === Home page (index) ===
@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

# === Registration ===
@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    req = user_pb2.RegisterRequest(username=username, password=password)
    res = gateway_stub.RegisterUser(req)

    if res.success:
        session["username"] = username
        return redirect(url_for("chat"))
    return "Registration failed", 400

# === Login ===
@app.route("/login", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    req = user_pb2.LoginRequest(username=username, password=password)
    res = gateway_stub.LoginUser(req)

    if res.success:
        session["username"] = username
        return redirect(url_for("chat"))
    return "Login failed", 400

# === Chat page ===
@app.route("/chat")
def chat():
    if "username" not in session:
        return redirect(url_for("index"))
    return render_template("chat.html", username=session["username"])

# === Send a message ===
# === Chat: Send a message ===
@app.route("/send", methods=["POST"])
def send():
    if "username" not in session:
        return redirect(url_for("index"))

    content = request.form["message"]  # matches chat.html input name
    req = message_pb2.Message(
        room_id="general",
        sender=session["username"],   # proto field
        content=content               # proto field
    )
    gateway_stub.SendMessage(req)
    return ("", 204)


# === Chat: Fetch message history ===
@app.route("/history")
def history():
    if "username" not in session:
        return jsonify([])

    req = message_pb2.HistoryRequest(room_id="general")
    res = gateway_stub.GetMessages(req)

    return jsonify([
        {"sender": m.sender, "content": m.content}   # matches chat.html JS
        for m in res.messages
    ])


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
