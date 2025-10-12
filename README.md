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

# Microservice-system
## **Project Overview**
A real-time distributed messaging system built using microservices architecture with gRPC communication. Users can login/register, create/join public rooms, send/receive messages, and maintain presence information.

## **System Architecture**
- **6 Microservices**: UI, Gateway, Auth, Room, Message, Presence
- **Communication**: gRPC (inter-service), HTTP/REST (client)
- **Database**: SQLite with Docker volumes
- **Ports**: UI (8080), Gateway (50055), Auth (50051), Room (50052), Message (50054), Presence (50053)

## **Prerequisites**
- Docker and Docker Compose installed
- Git (for cloning)
- Make sure docker is up and running and all the required ports are free(8080, 50055, 50051, 50052, 50053, 50054)

## **Quick Start**

### **1. Clone the Repository**
```bash
#Clone Repository
git clone https://github.com/Arpita4196/Distributed-Chat-System.git

#Navigate to project folder/deploy
cd Distributed-Chat-System/Micriservice-System/deploy
```

### **2. Start the System**
```bash
docker-compose -f deploy/docker-compose.yml up --build -d
```

👉 This will build all services using the Dockerfiles and may take several minutes.

### **3. Access the Application**
- Open your browser and go to: **http://localhost:8080**
- Register a new account (Provide Username, Email, Password) or Can login with existing credentials.
- Directly will be joined to "Genaral Chat" and you can Start chatting in the "General Chat" room.
- Create/Join chat rooms by providing room id and name(Ex- room-id: 001, Room Name:Chat Room 1)


## ⚙️ Performance Analysis (Load Testing)

### Setup
```bash
# Create a new Virtual Environment
python3 -m venv .venv
source .venv/bin/activate
# Install Locust
pip install locust

# From the deploy folder - cd Distributed-Chat-System/Micriservice-System/deploy
# Skip this if Microservice system is already running
docker compose -f docker-compose.yml up

# In a new terminal (from project root) - cd Distributed-Chat-System/Micriservice-System
locust -f load/locust/locustfile_http.py --host http://localhost:8080

### 🖥️ Open the Web UI

Go to 👉 [http://localhost:8089](http://localhost:8089)

Then follow these steps:

1. **Enter number of users** — for example, `50` or `100`  
2. **Enter Ramp up** — for example, `5`  
3. Click **Start** to begin the load test
```

### **4. Stop the System**
```bash
docker-compose -f deploy/docker-compose.yml down
```
