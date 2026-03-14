# FCAI-University

A **web-based platform** built with **Flask** that allows university doctors to **upload course materials** and students to **browse departments, view subjects, and download files**.

---

## Features

- Browse departments
- View subjects under each department
- Download course files
- Doctor login system for secure access
- Upload, replace, and delete files from dashboard

---

## Technologies Used

- **Backend:** Python, Flask
- **Database:** SQLite
- **Frontend:** HTML, CSS
- **File Handling:** `werkzeug` for secure file uploads
- **Other:** `datetime` for timestamps, `os` for file management

---

## Project StructureFCAI-University/

│
├─ app.py # Main Flask application
├─ university.db # SQLite database
├─ static/
│ └─ uploads/ # Folder for uploaded course files
├─ templates/
│ ├─ departments.html
│ ├─ index.html
│ ├─ subject.html
│ ├─ login.html
│ └─ dashboard.html
└─ README.md


---

## Setup Instructions

1. **Clone the repository**

```bash
git clone <repository-url>
cd FCAI-University
```
2. **Create a virtual environment**
```bash
python -m venv venv
source venv/bin/activate    # Linux/macOS
venv\Scripts\activate       # Windows
```
3. **Install dependencies**
```bash
pip install Flask werkzeug
```
4. **Initialize the database**
   ```bash
   python
    >>> from app import init_db
    >>> init_db()
    >>> exit()
   ```
   Usage

## Students:

Browse departments and subjects

Download course files directly

## Doctors:

Log in using your credentials

Upload new files, replace existing files, or delete files

Files are saved in static/uploads/ with unique timestamps

## Security & Notes

All uploaded files are sanitized using secure_filename to prevent malicious uploads.

Maximum upload file size is 50 MB.

Only logged-in doctors can manage files.

Database is SQLite, suitable for small projects or testing. For production, consider upgrading to MySQL/PostgreSQL.
