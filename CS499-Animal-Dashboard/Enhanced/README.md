# Grazioso Salvare Dashboard

## Overview
This project is a dashboard built around an animal shelter dataset. It allows users to view records, apply filters, and explore trends in outcomes. I also added an admin section where records can be created, updated, and deleted, along with a simple login and password system.

## Features
- View animal records in a table
- Filter by rescue type and breed
- See a map of selected animals
- View analytics like age breakdown and outcome trends
- Admin tools for adding, editing, and deleting records
- Password-protected admin access

## Tech Used
- Python
- Dash / Plotly
- Pandas
- MongoDB
- PyMongo
- Werkzeug (for password hashing)

## How to run
1. Make sure MongoDB is running locally
2. Install dependencies:
pip install -r requirements.txt
3. Run the app:
python app.py
4. Open in your browser:
http://127.0.0.1:8050/

## Notes
- The database should be named AAC with a collection called animals
- Animal ID must be unique when creating a record
- Admin login is required to access create/edit/delete features

## Final Note
This project started as a class assignment and I expanded it to make it more complete. I focused on improving structure, adding analytics, and building out admin functionality.

Portions of this project were developed with the assistance of ChatGPT. It was used to help refine code structure, improve readability, and troubleshoot issues. All implementation decisions, logic, and final code adjustments were completed by me.

## Admin Access
Default admin login:

Username: backup_admin  
Password: admin123  