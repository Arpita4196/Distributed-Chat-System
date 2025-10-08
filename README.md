# Distributed-Chat-System

# Object-based-system

This is a simple distributed chat system built with **gRPC**, **Flask**, and **Docker Compose**.  
It consists of multiple services:

- **gateway-svc** → main entrypoint, routes requests
- **user-svc** → handles user registration/login
- **room-svc** → manages chat rooms
- **message-svc** → stores & retrieves messages
- **presence-svc** → tracks online presence
- **ui-svc** → simple Flask UI for chatting
### Option 1 — Build from Source (GitHub clone)
If you want to build each service locally from Dockerfiles:

```bash
# Clone the repo
git clone https://github.com/Arpita4196/Distributed-Chat-System.git

# Move into your project folder
cd Distributed-Chat-System/object-based-system  #give your project folder path where it is stored

# Start the system (will build automatically if needed)
docker compose up

```

👉 This will build all services using the Dockerfiles inside the repo.  
First run may take several minutes as dependencies are installed

### Option 2 — Use Prebuilt Docker Hub Images
If you prefer to **skip building** and pull prebuilt images from Docker Hub:

```bash
git clone https://github.com/Arpita4196/Distributed-Chat-System.git
cd Distributed-Chat-System/object-based-system   #give your project folder path where it is stored
docker compose -f docker-compose.prod.yml up
```


## 🌐 Access the App
- **UI** → http://localhost:5000  
- **Gateway (gRPC)** → localhost:8080  
- Other services run internally on their mapped ports (50052–50055).
- First Register, Then login to send messages

## 📝 Notes
- Make sure you have **Docker** and **Docker Compose** installed.  
- If you use **Option 1**, every service is rebuilt from source.  
- If you use **Option 2**, services are pulled from Docker Hub and run directly.

## For performance analysis
```
pip install locust
# Inside the object-based-system folder
docker compose up
#or
docker compose -f docker-compose.prod.yml up
#In a new terminal (same folder):
locust --host http://localhost:5000
#Open the Web UI
Go to http://localhost:8089 in your browser.
1.Enter number of users (e.g., 50 or 100).

2.Enter spawn rate (e.g., 5).

3.Start test.
```

# Microservice-based-system
