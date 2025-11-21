app.py
--------
Main Flask application. Contains all routes, session handling, role-based access control, and MySQL query execution.
Acts as the central controller of the system.

.env
-----------
Stores environment variables (DB host, username, password, DB name, secret key).
Keeps sensitive configuration separate from the code.

requirements.txt
------------

List of required Python packages (Flask, Flask-MySQLdb, Flask-Session, python-dotenv).
Used to install dependencies via:

pip install -r requirements.txt

zooDB_created_new.sql
------------

Database creation file.
Includes table definitions, relationships, and initial sample data to set up the ZooDB schema.

zoodb_procedures_queries.sql
------------

Contains stored procedures, triggers, functions, and advanced SQL queries.
Adds logic such as capacity checks, delete restrictions, and multi-table reports.

create_usernames.sql
------------

Assigns sample usernames and passwords to employee records for demonstration and login testing.

templates/
------------
Folder containing all HTML templates (login, dashboard, animals, habitats, etc.).
Rendered by Flask for the frontend UI.

flask_session/
------------

Folder used by Flask-Session to store server-side session data.
Enables persistent login sessions.

__pycache__/

Automatically generated Python cache folder.
Stores compiled bytecode to speed up execution.
