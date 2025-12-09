# User-Friendly-System-Call-Interface-for-Enhanced-security

This project is a mini Operating System simulation built using **Python (Flask)** for the backend and **HTML/CSS/JS** for the frontend.  
It demonstrates core OS concepts such as:

- Process scheduling  
- Memory management  
- File system simulation  
- User authentication & session handling  
- System call handling  

This project is part of an academic assignment for learning OS fundamentals and implementing them through a working web-based simulation.

---

## 🚀 Features

### 🔹 1. **User Authentication (Login System)**
- User login, logout, session tracking  
- Implements `flask-login` for authentication  
- Stores user details securely  

### 🔹 2. **Process Scheduling Simulator**
- Add, remove, and view processes  
- Supports scheduling algorithms (FCFS, SJF, RR, Priority etc.)  
*(If you want, I can update this section based on your actual algorithms.)*

### 🔹 3. **Memory Management**
- Page table simulation  
- Allocation & deallocation visualisation  
- Shows how frames and pages are filled

### 🔹 4. **File System Module**
- Create, delete, view files  
- Simulated directory structure  

### 🔹 5. **Interactive Frontend**
- Clean UI  
- Built using HTML, CSS, JavaScript  
- Communicates with Flask APIs

---

## 🧩 Project Structure



OS 2/
│
├── backend/
│ ├── app.py # Main Flask application
│ ├── models/ # Database models
│ ├── routes/ # API route handlers
│ ├── static/ # Images, JS, CSS
│ ├── templates/ # HTML frontend
│ └── utils/ # Helper functions
│
└── frontend/
├── index.html # Home UI
├── styles.css # Styling
└── app.js # Frontend logic
