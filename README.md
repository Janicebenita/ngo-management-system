NGO Management System

A web-based NGO Management System built using Flask to help non-governmental organizations efficiently manage, track, and monitor their projects.
The system provides a clean dashboard with CRUD operations, search functionality, and date-based filtering for better organization and transparency.


---

Features

User authentication for authorized access

Add new projects

View project details

Edit and update existing projects

Delete projects

Search projects

Filter projects based on dates

Clean and user-friendly dashboard



---

Tech Stack

Backend: Flask (Python)

Frontend: HTML, CSS, Bootstrap

Database: SQLite / MySQL

Template Engine: Jinja2



---

Project Structure

ngo-management-system/
│
├── app.py
├── templates/
│   ├── login.html
│   ├── dashboard.html
│   ├── add_project.html
│   ├── edit_project.html
│   └── view_project.html
│
├── static/
│   ├── css/
│   └── js/
│
├── database.db
├── requirements.txt
└── README.md


---

Installation and Setup

1. Clone the repository

git clone https://github.com/your-username/ngo-management-system.git
cd ngo-management-system


2. Create a virtual environment

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate


3. Install dependencies

pip install -r requirements.txt


4. Run the application

python app.py


5. Open the browser and navigate to

http://127.0.0.1:5000/




---

Use Cases

NGOs managing multiple social projects

Tracking project timelines and progress

Monitoring ongoing and completed initiatives

Improving transparency and project organization



---

Future Enhancements

Role-based access control (Admin, Staff, Volunteers)

Report generation in PDF or Excel format

Donation and fund tracking

Email notifications

Cloud database integration



