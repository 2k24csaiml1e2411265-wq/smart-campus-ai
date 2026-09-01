# 🏫 Smart Campus AI

> **AI-Powered Energy, Water & Sustainability Intelligence Platform**

Smart Campus AI is a full-stack IoT-ready sustainability management platform that monitors **energy, water, and solar consumption**, detects anomalies using **Machine Learning**, forecasts future usage, and provides actionable insights through an interactive dashboard.

**Status:** ✅ Fully Deployed & Demo Ready

---

## 🌐 Live Demo

| Service | Link |
|---------|------|
| Frontend (Vercel) | https://smart-campus-ai-pink.vercel.app |
| Backend (Render) | https://smart-campus-ai-api.onrender.com |
| API Documentation | https://smart-campus-ai-api.onrender.com/docs |

> **Note:** The project currently runs in **DEMO mode** using a built-in IoT simulator and is ready for future integration with real sensors.

---

## 🔑 Demo Credentials

| Role | Email | Password |
|------|-------|----------|
| Admin | `admin@psit.ac.in` | `admin123` |
| Facility Manager | `facility@psit.ac.in` | `facility123` |
| Department Manager | `cse.manager@psit.ac.in` | `manager123` |
| Viewer | `viewer@psit.ac.in` | `viewer123` |

---

# ✨ Features

## 📊 Smart Dashboard

- Real-time Energy Monitoring
- Water Consumption Tracking
- Solar Generation Monitoring
- CO₂ Avoided Calculation
- Green Score Leaderboard
- Department-wise Analytics

## 🤖 AI & Machine Learning

- Isolation Forest Anomaly Detection
- Random Forest Energy Forecasting
- AI-generated Recommendations
- Simulated Anomaly Testing

## 📈 Analytics

- 24h / 7d / 30d Trends
- Department Comparison
- Sustainability Metrics
- Historical Consumption Analysis

## 🔐 Administration

- JWT Authentication
- Role-Based Access Control (RBAC)
- Device Management
- Report Generation
- System Health Monitoring

## 🌐 IoT Ready

- MQTT Architecture
- WebSocket Real-time Updates
- Built-in Demo Simulator
- Future Hardware Integration

---

# 🏗️ System Architecture

```
 IoT Sensors
(Energy • Water • Solar • Weather)
          │
          ▼
     MQTT Broker
          │
          ▼
   IoT Gateway / ESP32
          │
          ▼
   FastAPI Backend
          │
    ┌─────┴─────┐
    ▼           ▼
PostgreSQL   ML Models
 Database    (Isolation Forest,
              Random Forest)
    └─────┬─────┘
          ▼
 React Dashboard
```

---

# ⚙️ Tech Stack

| Layer | Technology |
|--------|------------|
| Frontend | React, Vite, Tailwind CSS, Recharts |
| Backend | FastAPI, SQLAlchemy |
| Database | PostgreSQL |
| Machine Learning | Scikit-learn |
| Authentication | JWT |
| Communication | REST API, WebSocket, MQTT |
| Deployment | Vercel, Render |

---

# 📂 Project Structure

```
smart-campus-ai/
├── backend/
│   ├── app/
│   │   ├── routes/
│   │   ├── ml/
│   │   ├── models/
│   │   ├── mqtt/
│   │   ├── bootstrap.py
│   │   ├── database.py
│   │   └── main.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── services/
│   │   └── App.jsx
│
├── simulator/
└── README.md
```

---

# 🚀 Installation

## Clone Repository

```bash
git clone https://github.com/your-username/smart-campus-ai.git
cd smart-campus-ai
```

## Backend Setup

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Backend runs on:

```
http://localhost:8000
```

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on:

```
http://localhost:5173
```

---

# 🔧 Environment Variables

Create a `.env` file inside the backend folder.

```env
DATABASE_URL=your_postgresql_url
JWT_SECRET=your_secret_key
FRONTEND_URL=http://localhost:5173
DATA_MODE=DEMO
MQTT_BROKER=localhost
MQTT_PORT=1883
```

---

# 🧠 Machine Learning Pipeline

### Isolation Forest

- Detects abnormal energy consumption
- Generates anomaly alerts
- Supports preventive maintenance

### Random Forest Regression

- Predicts future energy usage
- Improves resource planning
- Supports sustainability decisions

```
Sensor Data
     │
     ▼
Data Cleaning
     │
     ▼
Feature Engineering
     │
     ▼
Machine Learning
(Isolation Forest + Random Forest)
     │
     ▼
Alerts • Forecast • Recommendations
```

---

# 🌱 Physical IoT Implementation (Future Ready)

The platform is designed for real hardware deployment using:

- Smart Energy Meters
- Water Flow Sensors
- Ultrasonic Water Level Sensors
- Solar Power Meters
- ESP32 IoT Gateway
- MQTT Communication
- Weather Sensors

```
Solar Panels ─┐
Energy Meter ─┤
Water Sensor ─┼──► ESP32 Gateway
Weather Node ─┘        │
                        ▼
                  MQTT Broker
                        ▼
                 FastAPI Backend
                        ▼
                  PostgreSQL
                        ▼
                  React Dashboard
```

---

# 📋 API Overview

| Endpoint | Purpose |
|-----------|----------|
| `/api/login` | User Authentication |
| `/api/dashboard` | Dashboard Data |
| `/api/analytics` | Analytics |
| `/api/alerts` | Alerts |
| `/api/forecast` | Forecast |
| `/api/admin` | Admin Controls |
| `/api/ws` | WebSocket Updates |

---

# 🧪 Testing Results

| Test | Status |
|------|--------|
| Login | ✅ Pass |
| Dashboard | ✅ Pass |
| Analytics | ✅ Pass |
| Forecast | ✅ Pass |
| Reports | ✅ Pass |
| Simulate Anomaly | ✅ Pass |
| Deployment | ✅ Pass |

---

# 📈 Project Workflow

1. Sensors generate Energy, Water, and Solar readings.
2. ESP32/IoT Gateway collects sensor data.
3. MQTT transfers readings.
4. FastAPI processes incoming data.
5. PostgreSQL stores readings.
6. Machine Learning analyzes data.
7. Dashboard displays analytics and alerts.

---

# 🎯 Future Scope

- Live ESP32 Sensor Integration
- Mobile Application
- Multi-campus Support
- QR-based Device Maintenance
- Carbon Footprint Analytics
- Predictive Maintenance
- AI Chatbot Assistant

---

# 📊 Project Highlights

- ✅ Full-Stack Cloud Deployment
- ✅ AI-Powered Anomaly Detection
- ✅ Energy Forecasting
- ✅ JWT Authentication
- ✅ Role-Based Access Control
- ✅ PostgreSQL Database
- ✅ WebSocket Support
- ✅ MQTT-ready Architecture
- ✅ Interactive Dashboard
- ✅ Built-in Demo Simulator

---

# 👨‍💻 Author

**Yash Kushwaha**

B.Tech – Computer Science & Engineering

Pranveer Singh Institute of Technology (PSIT), Kanpur

---

# ⭐ Acknowledgement

This project was developed as a **Final Year Major Project** for the Bachelor of Technology degree at **Pranveer Singh Institute of Technology (PSIT), Kanpur**, demonstrating the practical application of **Artificial Intelligence, IoT, Cloud Computing, and Web Technologies** for sustainable campus management.
