# Hospital Management System (HMS)

A **Hospital Management System (HMS)** web application developed using **HTML, CSS, JavaScript, Python (Flask),** and **MySQL**. This project aims to streamline hospital processes such as patient registration, appointment scheduling, doctor management, and more through an easy-to-use web interface.

---

## Features

- **User Authentication:** Secure login and registration for admins, doctors, and patients.
- **Patient Management:** Add, update, view, and delete patient records.
- **Doctor Management:** Manage doctor profiles and their schedules.
- **Appointment Scheduling:** Book, view, and manage appointments.
- **Billing Module:** Generate and manage patient bills.
- **Dashboard:** Visual overview of key statistics for admins.
- **Responsive Design:** Works seamlessly on desktops, tablets, and mobile devices.

---

## Tech Stack

- **Frontend:** HTML5, CSS3, JavaScript
- **Backend:** Python with Flask framework
- **Database:** MySQL

---

## How to Run the Project

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/hms.git
cd hms
```

### 2. Set Up Python Environment

It is recommended to use a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Set Up MySQL Database

- Install MySQL and ensure it is running.
- Create a database for the project:

```sql
CREATE DATABASE hospital_system;
```

- Update the database configuration in your Flask app (`config.py` or similar):

```python
DB_HOST = 'localhost'
DB_USER = 'your_mysql_user'
DB_PASSWORD = 'your_mysql_password'
DB_NAME = 'hospital_system'
```

- Import required tables. You may find a `schema.sql` file in the project. Run:

```bash
mysql -u your_mysql_user -p hospital_system < schema.sql
```

### 5. Run the Application

```bash
flask run
```

or

```bash
python app.py
```

The application will be available at [http://localhost:5000](http://localhost:5000).

---

## Folder Structure

```
hms/
│
├── static/
│   ├── css/
│   └── js/
├── templates/
│   └── (HTML files)
├── app.py
├── requirements.txt
├── schema.sql
└── README.md
```
