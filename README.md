# 🏫 Smart Campus AI

> **An AI-powered smart campus management and monitoring platform for energy optimization, anomaly detection, forecasting, and sustainable campus operations.**

Smart Campus AI is a full-stack intelligent campus management system designed to monitor campus infrastructure, analyze real-time data, detect abnormal behavior, forecast energy consumption, calculate sustainability scores, and provide actionable recommendations.

The project combines **Artificial Intelligence, Machine Learning, IoT-style simulation, FastAPI, React, and data visualization** into a unified campus management dashboard.

---

## 🚀 Key Features

### 📊 Smart Dashboard

* Real-time campus KPIs
* Energy consumption monitoring
* Water usage monitoring
* Device status
* Campus Green Score
* Active alerts
* AI-generated recommendations
* Live system status

### 🤖 AI & Machine Learning

#### Anomaly Detection

Uses an **Isolation Forest** model to identify unusual campus behavior such as:

* Abnormal energy consumption
* Unexpected device activity
* Unusual environmental readings
* Potential infrastructure problems

#### Energy Forecasting

Machine learning models forecast future energy consumption using historical campus data.

The forecasting system helps administrators:

* Predict upcoming energy demand
* Identify consumption patterns
* Improve resource planning
* Reduce unnecessary energy usage

### 🌱 Green Score

The system calculates a sustainability-oriented campus score using factors such as:

* Energy consumption
* Water usage
* Renewable energy
* Environmental performance
* Operational efficiency

### 🔔 Intelligent Alerts

The platform can identify abnormal conditions and display alerts to campus administrators.

Examples:

* High energy consumption
* Device anomalies
* Forecasted high demand
* Infrastructure issues

### 💡 AI Recommendations

The system provides recommendations based on campus conditions and detected anomalies.

Examples:

* Reduce unnecessary energy consumption
* Investigate abnormal devices
* Optimize resource usage
* Monitor departments with unusual consumption

### 📈 Analytics

Interactive analytics provide insights into:

* Energy consumption
* Water usage
* Department performance
* Device activity
* Historical trends
* Forecasts
* Sustainability metrics

### 🏢 Department Management

Campus administrators can monitor individual departments and compare their operational performance.

### 🔌 Device Monitoring

The system provides device-level monitoring and status information.

Supported states include:

* Online
* Offline
* Warning
* Anomalous

### 📡 Real-Time Updates

The application supports real-time data updates through WebSockets.

### 🧪 Campus Simulator

A built-in simulator generates campus readings and can simulate abnormal conditions without requiring physical IoT hardware.

This makes the project suitable for:

* Demonstrations
* Testing
* Academic presentations
* AI/ML experimentation

### 👥 Role-Based Access

The application supports different user roles such as:

* Admin
* Facility Manager
* Department Manager
* Viewer

---

# 🏗️ System Architecture

```text
                    ┌─────────────────────────┐
                    │      React Frontend     │
                    │                         │
                    │ Dashboard / Analytics   │
                    │ Alerts / Devices        │
                    │ Departments / Reports   │
                    └────────────┬────────────┘
                                 │
                                 │ REST API / WebSocket
                                 ▼
                    ┌─────────────────────────┐
                    │      FastAPI Backend    │
                    │                         │
                    │ Authentication          │
                    │ Campus APIs             │
                    │ Device APIs             │
                    │ Analytics               │
                    │ Alerts                  │
                    │ Forecasts               │
                    └────────────┬────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
                    ▼                         ▼
          ┌──────────────────┐      ┌──────────────────┐
          │   ML Pipeline    │      │ Campus Simulator │
          │                  │      │                  │
          │ Anomaly Detect.  │      │ Energy           │
          │ Forecasting      │      │ Water            │
          │ Recommendations  │      │ Devices          │
          └────────┬─────────┘      └────────┬─────────┘
                   │                         │
                   └────────────┬────────────┘
                                ▼
                     ┌────────────────────┐
                     │ Campus Data / DB   │
                     └────────────────────┘
```

---

# 🛠️ Technology Stack

## Frontend

* React
* Vite
* JavaScript
* Tailwind CSS
* Recharts / charting components
* WebSocket

## Backend

* Python
* FastAPI
* Pydantic
* SQLAlchemy
* Uvicorn
* WebSockets

## Artificial Intelligence / Machine Learning

* Python
* Scikit-learn
* Isolation Forest
* Forecasting models
* Feature Engineering
* Joblib

## Data & Simulation

* Campus data simulator
* Synthetic IoT-style readings
* Energy readings
* Water readings
* Device telemetry

## Development & Deployment

* Git
* GitHub
* Docker
* REST APIs
* Hugging Face / cloud deployment compatible architecture

---

# 📁 Project Structure

```text
smart-campus-ai/
│
├── backend/
│   ├── app/
│   │   ├── ml/
│   │   │   ├── anomaly_detection.py
│   │   │   ├── feature_engineering.py
│   │   │   ├── forecasting.py
│   │   │   ├── model_manager.py
│   │   │   └── recommendations.py
│   │   │
│   │   ├── models/
│   │   ├── mqtt/
│   │   ├── routes/
│   │   ├── schemas/
│   │   ├── services/
│   │   ├── utils/
│   │   │
│   │   ├── bootstrap.py
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── dependencies.py
│   │   └── main.py
│   │
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── services/
│   │   ├── utils/
│   │   ├── App.jsx
│   │   └── main.jsx
│   │
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
│
├── ml/
│   ├── train_anomaly.py
│   └── train_forecast.py
│
├── models/
│   ├── energy_forecast.joblib
│   ├── isolation_forest.joblib
│   └── metrics.joblib
│
├── simulator/
│   ├── engine.py
│   └── simulator.py
│
├── simulator.py
├── .env.example
├── .gitignore
├── LICENSE
└── README.md
```

---

# ⚙️ Installation

## 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/smart-campus-ai.git
cd smart-campus-ai
```

Replace `YOUR_USERNAME` with your GitHub username.

---

# 🐍 Backend Setup

Open a terminal inside the project directory.

### Create Virtual Environment

Windows:

```powershell
python -m venv .venv
```

Activate it:

```powershell
.venv\Scripts\activate
```

Install dependencies:

```powershell
pip install -r backend/requirements.txt
```

---

# ▶️ Run Backend

From the project root:

```powershell
python -m uvicorn backend.app.main:app --reload --port 8000
```

Backend should be available at:

```text
http://127.0.0.1:8000
```

FastAPI documentation:

```text
http://127.0.0.1:8000/docs
```

The `/docs` page provides an interactive interface for testing the APIs.

---

# 💻 Frontend Setup

Open another terminal.

```powershell
cd frontend
```

Install dependencies:

```powershell
npm install
```

Start the development server:

```powershell
npm run dev
```

The frontend will normally be available at:

```text
http://localhost:5173
```

---

# 🔗 Frontend ↔ Backend Configuration

Create a frontend environment file if required:

```text
frontend/.env
```

Configure the backend API URL:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

Restart the frontend after changing environment variables.

---

# 🧠 Machine Learning Models

The project contains trained machine learning models inside:

```text
models/
```

### Anomaly Detection

```text
models/isolation_forest.joblib
```

The Isolation Forest model identifies unusual patterns in campus data.

### Energy Forecasting

```text
models/energy_forecast.joblib
```

The forecasting model predicts future energy consumption.

### Metrics

```text
models/metrics.joblib
```

Stores model-related evaluation information.

---

# 🏋️ Training ML Models

The training scripts are located in:

```text
ml/
```

Anomaly detection:

```powershell
python ml/train_anomaly.py
```

Energy forecasting:

```powershell
python ml/train_forecast.py
```

After training, the generated models can be stored in the `models/` directory.

---

# 🧪 Campus Data Simulator

The project includes a simulator so that the system can operate without physical IoT devices.

The simulator can generate:

* Energy readings
* Water readings
* Device activity
* Environmental data
* Normal operating conditions
* Abnormal conditions

This allows the AI system to be demonstrated using simulated smart-campus data.

---

# 🚨 Simulating an Anomaly

The dashboard/admin functionality can be used to trigger an anomaly simulation.

This allows the complete pipeline to be demonstrated:

```text
Simulator
    ↓
Campus Reading
    ↓
ML Model
    ↓
Anomaly Detection
    ↓
Backend
    ↓
Alert
    ↓
React Dashboard
```

This is especially useful during project demonstrations.

---

# 🔐 Authentication

The application includes authentication and role-based access control.

Example demonstration credentials used during development:

```text
Email: admin@psit.ac.in
Password: admin123
```

> **Important:** Change demonstration credentials before deploying the application publicly.

---

# 📊 Main Application Pages

## Dashboard

Provides a complete overview of campus operations.

Includes:

* KPIs
* Energy
* Water
* Green Score
* Alerts
* Recommendations
* Device status

## Analytics

Provides detailed historical analysis and visualizations.

## Departments

Shows department-wise performance and resource usage.

## Devices

Provides device-level status and monitoring.

## Alerts

Displays detected anomalies and system alerts.

## Forecast

Displays predicted future energy consumption.

## Reports

Provides campus performance and sustainability reports.

## Admin

Provides administrative controls and simulation functionality.

---

# 🌱 Problem Statement

Modern educational campuses consume large amounts of energy and water across classrooms, laboratories, hostels, offices, and other facilities.

Traditional campus management systems often rely on manual monitoring and historical reporting. This can make it difficult to:

* Detect abnormal consumption quickly
* Predict future energy requirements
* Identify inefficient devices
* Monitor sustainability
* Respond to infrastructure problems
* Make data-driven decisions

Smart Campus AI addresses these problems by combining real-time monitoring with artificial intelligence and machine learning.

---

# 💡 Proposed Solution

The proposed system continuously analyzes campus data and uses machine learning to identify patterns and abnormalities.

The system:

1. Collects campus data
2. Processes incoming readings
3. Performs feature engineering
4. Detects anomalies
5. Forecasts future energy usage
6. Calculates campus sustainability metrics
7. Generates recommendations
8. Displays results through a centralized dashboard

---

# 🔄 Data Flow

```text
Campus / Simulator
       ↓
Data Ingestion
       ↓
Data Processing
       ↓
Feature Engineering
       ↓
 ┌─────┴──────────┐
 ↓                ↓
Anomaly        Forecasting
Detection
 ↓                ↓
 └───────┬────────┘
         ↓
Recommendations
         ↓
FastAPI Backend
         ↓
React Dashboard
         ↓
Administrator
```

---

# 🤖 Machine Learning Approach

## Anomaly Detection

The system uses Isolation Forest for unsupervised anomaly detection.

The model learns the normal behavior of campus data and assigns anomaly scores to new observations.

Conceptually:

```text
Normal Data
    ↓
Learn Normal Patterns
    ↓
New Reading
    ↓
Anomaly Score
    ↓
Normal / Anomalous
```

This approach is useful when large amounts of labeled anomaly data are unavailable.

---

## Energy Forecasting

Historical energy consumption data is used to identify consumption patterns and estimate future demand.

The forecasting pipeline includes:

```text
Historical Data
      ↓
Data Cleaning
      ↓
Feature Engineering
      ↓
Model Training
      ↓
Evaluation
      ↓
Forecast
```

---

# 📡 API

The backend provides REST APIs for different parts of the application.

Major API categories include:

```text
/api/auth
/api/campus
/api/devices
/api/anomalies
/api/forecasts
/api/admin
/api/health
/api/ingest
```

Interactive API documentation is available through:

```text
http://127.0.0.1:8000/docs
```

---

# 🧪 Testing

Backend tests are located inside:

```text
backend/tests/
```

Run the tests using:

```powershell
pytest backend/tests
```

or:

```powershell
python -m pytest backend/tests
```

---

# 🔒 Environment Variables

Do not commit sensitive credentials to GitHub.

Use:

```text
.env
```

for local secrets and:

```text
.env.example
```

as a template.

Example:

```env
DATABASE_URL=your_database_url
SECRET_KEY=your_secret_key
```

> Never upload real API keys, passwords, database credentials, or secret tokens to GitHub.

---

# 🐳 Docker

The project architecture can be containerized for deployment.

A typical deployment architecture is:

```text
                 Internet
                    │
                    ▼
             ┌─────────────┐
             │   Frontend  │
             │    React    │
             └──────┬──────┘
                    │
                    ▼
             ┌─────────────┐
             │   FastAPI   │
             │   Backend   │
             └──────┬──────┘
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
     Database            ML Models
```

---

# ☁️ Deployment

The frontend and backend can be deployed separately.

### Frontend

Suitable platforms include:

* Vercel
* Netlify
* Cloudflare Pages

### Backend

Suitable platforms include:

* Render
* Railway
* Hugging Face Spaces
* AWS
* Google Cloud
* Azure

For production deployment, configure:

```text
Frontend
    ↓
Public Backend URL
```

instead of:

```text
http://127.0.0.1:8000
```

---

# 📸 Screenshots

Add screenshots of the application here after deployment.

Recommended screenshots:

```text
1. Login Page
2. Dashboard
3. Analytics
4. Anomaly Alert
5. Energy Forecast
6. Departments
7. Devices
8. Reports
9. Admin Panel
```

Example:

```markdown
## Dashboard

![Smart Campus Dashboard](screenshots/dashboard.png)
```

---

# 🎯 Project Objectives

The major objectives of Smart Campus AI are:

* Develop an intelligent campus monitoring platform
* Monitor energy and resource consumption
* Detect abnormal campus behavior
* Forecast future energy demand
* Provide actionable recommendations
* Improve campus sustainability
* Reduce resource wastage
* Provide centralized campus analytics
* Demonstrate practical applications of AI/ML

---

# 🌍 Future Scope

The project can be extended with real IoT hardware and additional AI capabilities.

Potential future improvements include:

### IoT Integration

Connect real sensors for:

* Electricity
* Water
* Temperature
* Air quality
* Occupancy
* Smart meters

### Advanced AI

Future versions could include:

* Deep learning forecasting
* Large Language Model based recommendations
* AI-powered campus assistant
* Natural language analytics
* Automated root-cause analysis

### Predictive Maintenance

The system could predict device failures before they occur.

### Mobile Application

A mobile application could provide:

* Push notifications
* Alerts
* Campus statistics
* Admin controls

### Smart Automation

AI predictions could automatically control:

* Lighting
* HVAC
* Smart appliances
* Water systems

---

# 👨‍🎓 Academic Information

**Project:** Smart Campus AI

**Degree:** B.Tech Computer Science & Engineering — Artificial Intelligence & Machine Learning

**Project Type:** Final Year / Major Project

**Domain:**

```text
Artificial Intelligence
Machine Learning
IoT
Smart Campus
Sustainability
Full-Stack Development
```

---

# 👨‍💻 Author

**Yash Kushwaha**

B.Tech CSE — Artificial Intelligence & Machine Learning

---

# 📄 License

This project is licensed under the terms specified in the `LICENSE` file.

---

# ⭐ Acknowledgement

This project was developed as an academic AI/ML project to demonstrate how artificial intelligence, machine learning, real-time monitoring, and full-stack technologies can be applied to smart campus management and sustainability.

---

## ⭐ If You Find This Project Useful

Give the repository a ⭐ on GitHub and feel free to explore, modify, and improve the project.
