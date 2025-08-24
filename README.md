# Cloud Drive Django Project

This is a **Django project in Python**, focused on the enumeration of cloud drive functions. Users can upload files, manage folders, and maintain their data on a database. The project is designed to be dockerized for easy deployment.

---

## Features

- User authentication and management
- File upload and management
- Folder organization
- Trash/recycle functionality
- Cloud drive-like interface
- Dockerized for portability

---

## Technologies Used

- Python 3.12
- Django 5.1.1
- SQLite3 (default, can be configured to use external DB)
- Docker
- HTML/CSS for frontend

---

## Getting Started

### Prerequisites

- Python 3.12
- Docker (if using Docker)
- Git (for cloning the repository)

### Installation without Docker

1. Clone the repository:
 https://github.com/Greenchman/Project-drive-imagine_ai-.git
 cd Project-drive-imagine_ai
2. Create a virtual environment:
   python -m venv env


3. Activate the virtual environment:
   
    # Windows
    env\Scripts\activate
    
    # Linux / Mac
    source env/bin/activate


4. Install dependencies:
   pip install -r requirements.txt'

5. Apply migrations:
   python manage.py migrate

6. Run the development server:
   python manage.py runserver


Now you can Access the app
Open your browser and go to:

http://127.0.0.1:8000/
 

