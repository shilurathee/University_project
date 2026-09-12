# University Management System

A web-based **University Management System** developed using **Flask and MySQL** that allows administrators, teachers, and students to manage academic information such as courses, registrations, assessments, marks, and results.

---

## Project Overview

This system was developed as a **Database Systems project**.
It integrates **student registration and course performance tracking** in a single platform.

The system supports:

* Recording student registrations for courses
* Creating assessments dynamically (assignments/exams)
* Recording marks for each assessment
* Computing weighted total marks
* Assigning grades based on configurable grade cutoffs

The application uses **Flask for backend routing**, **MySQL as the database**, and **HTML/CSS for the frontend interface**.

---

## Tech Stack

Backend

* Python
* Flask

Database

* MySQL

Frontend

* HTML
* CSS
* Jinja2 Templates

Tools

* Git
* GitHub
* GitHub Desktop

---

## System Architecture

Browser (User Interface)
↓
Flask Application (Routing + Logic)
↓
MySQL Database (Data Storage)

---

## Features

### Admin

Admin manages the entire system.

Capabilities:

* Add, edit, and delete **students**
* Add, edit, and delete **teachers**
* Add and manage **courses**
* Register students into courses
* View registrations
* Manage grade cutoffs

---

### Teacher

Teachers manage academic performance.

Capabilities:

* View assigned courses
* Create and manage **assessments**
* Enter marks for students
* View computed results
* Calculate final course marks using **weighted assessments**

Assessments are **dynamic**, meaning teachers can add new assignments or exams anytime.

---

### Student

Students can view their academic information.

Capabilities:

* View registered courses
* View marks for assessments
* View total marks and grades

---

## Key Functionalities

### Student Registration System

Students can be registered for courses through the admin dashboard.

### Dynamic Assessments

Assignments and exams are **not predefined**. Teachers can add assessments at any time.

### Marks Recording

Marks are stored for every student in each assessment.

### Weighted Grade Calculation

Each assessment has a weight, and the system calculates the final course marks automatically.

Example:

Assignment 1 → 20%
Midterm → 30%
Final Exam → 50%

Total Marks = Weighted sum of all assessments.

### Grade Cutoffs

Grades are assigned based on defined cutoffs.

Example:

A → 85+
B → 70–84
C → 55–69
D → 40–54
F → Below 40

---

## Folder Structure

```
university_project
│
├── app.py
├── db.py
├── requirements.txt
├── README.md
│
├── templates/
│   ├── login.html
│   ├── admin_dashboard.html
│   ├── teacher_dashboard.html
│   ├── student_dashboard.html
│   ├── students.html
│   ├── teachers.html
│   ├── courses.html
│   ├── registrations.html
│   ├── teacher_courses.html
│   ├── teacher_assessments.html
│   ├── teacher_marks.html
│   └── teacher_results.html
│
├── static/
│   └── style.css
│
└── database/
    └── schema.sql
```

---

## Installation and Setup

### 1. Clone the Repository

```
git clone https://github.com/yourusername/university_management_system.git
cd university_management_system
```

### 2. Install Dependencies

```
pip install flask mysql-connector-python
```

### 3. Setup MySQL Database

Create a database:

```
CREATE DATABASE university;
```

Run the SQL schema file to create tables.

---

### 4. Configure Database Connection

Update database credentials in `db.py`:

```
host="localhost"
user="root"
password="yourpassword"
database="university"
```

---

### 5. Run the Application

```
python app.py
```

Open the browser:

```
http://127.0.0.1:5000
```

---


## Future Improvements

* Password hashing and authentication security
* Search and filtering features
* Export results to CSV/PDF
* Improved UI using Bootstrap
* Graphical analytics for course performance

---

## Author

Romansh Rathee
Aanya Gupta
Vijval Gupta


Database Systems Project
