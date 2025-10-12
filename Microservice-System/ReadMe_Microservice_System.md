# Distributed-Chat-System

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

#Navigate to project folder
cd Distributed-Chat-System/Microservice-System
```

### **2. Start the System**
```bash
docker-compose -f deploy/docker-compose.yml up --build -d

#Check if all the services are up and running
docker-compose -f deploy/docker-compose.yml ps
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

# From the Project folder - cd Distributed-Chat-System/Microservice-System
# Skip this if Microservice system is already running
docker compose -f docker-compose.yml up

# In a new terminal (from project root) - cd Distributed-Chat-System/Microservice-System
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
