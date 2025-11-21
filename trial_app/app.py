import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
from flask_session import Session
from datetime import date 

# --- Load environment variables from .env file ---
load_dotenv() 

app = Flask(__name__)

# --- Database Configuration ---
# Reads from your .env file
app.config['MYSQL_HOST'] = os.environ.get('DB_HOST')
app.config['MYSQL_USER'] = os.environ.get('DB_USER')
app.config['MYSQL_PASSWORD'] = os.environ.get('DB_PASS') 
app.config['MYSQL_DB'] = os.environ.get('DB_NAME')
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# --- Session Configuration ---
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY') 
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

mysql = MySQL(app)

# --- Routes ---

@app.route('/')
def home():
    """Renders the login page or redirects to the dashboard if already logged in."""
    if 'loggedin' in session:
        return redirect(url_for('dashboard')) 
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handles the user login form submission."""
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor = mysql.connection.cursor()
        try:
            # Check the Employee table for a matching user/password
            cursor.execute(
                'SELECT * FROM Employee WHERE username = %s AND password = %s', 
                (username, password)
            )
            account = cursor.fetchone()
            if account:
                # Create a session for the logged-in user
                session['loggedin'] = True
                session['id'] = account['employee_id']
                session['username'] = account['username']
                session['role'] = account['role'] # This is key for varied privileges
                return redirect(url_for('dashboard'))
            else:
                error = 'Incorrect username or password!'
        except Exception as e:
            error = f"An error occurred: {str(e)}"
        finally:
            cursor.close() # Ensure cursor is closed
            
    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    """Displays the dashboard appropriate for the user's role."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
        
    cursor = mysql.connection.cursor()
    try:
        if session['role'] == 'Manager':
            # --- "Procedures/Functions (With GUI)" ---
            cursor.execute("SELECT fn_GetTotalAnimalCount() AS animal_count")
            count_result = cursor.fetchone()
            cursor.execute("SELECT fn_GetTotalCapacity() AS total_capacity")
            capacity_result = cursor.fetchone()
            
            # --- "1 Aggregate Query (With GUI)" ---
            cursor.execute("""
                SELECT 
                    date, 
                    AVG(price) AS average_price,
                    COUNT(ticket_id) AS tickets_sold
                FROM Ticket
                GROUP BY date
                ORDER BY date DESC
            """)
            ticket_report = cursor.fetchall()
            return render_template(
                'manager_dashboard.html', 
                animal_count=count_result['animal_count'],
                total_capacity=capacity_result['total_capacity'],
                ticket_report=ticket_report
            )
        elif session['role'] == 'Zookeeper':
            return render_template('zookeeper_dashboard.html')
        else:
            # Fallback for other roles
            return render_template('layout.html')
    except Exception as e:
        flash(f"Error loading dashboard: {str(e)}", "danger")
        return render_template('layout.html')
    finally:
        cursor.close()

@app.route('/logout')
def logout():
    """Logs the user out by clearing the session."""
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('username', None)
    session.pop('role', None)
    return redirect(url_for('home'))

# --- ANIMAL MANAGEMENT ROUTES ---

@app.route('/animals')
def animals():
    """
    Displays the list of all animals.
    Hits "Read operations (With GUI)" and "1 Join Query (With GUI)".
    """
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session['role'] not in ['Manager', 'Zookeeper']:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))

    cursor = mysql.connection.cursor()
    try:
        # --- "1 Join Query (With GUI)" ---
        cursor.execute("""
            SELECT 
                A.animal_id,
                A.name AS animal_name,
                A.species,
                A.gender,
                A.age,
                H.name AS habitat_name,
                H.type AS habitat_type
            FROM Animal A
            JOIN Habitat H ON A.habitat_id = H.habitat_id
            ORDER BY A.name
        """)
        animals = cursor.fetchall()
    except Exception as e:
        flash(f"Error fetching animals: {str(e)}", "danger")
        animals = []
    finally:
        cursor.close()
        
    # --- "Read operations (With GUI)" ---
    return render_template('animals.html', animals=animals)

@app.route('/add_animal', methods=['GET', 'POST'])
def add_animal():
    """
    Handles adding a new animal (GET for form, POST for submission).
    Hits "Create operations (With GUI)" and "Procedures/Functions (With GUI)".
    """
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session['role'] not in ['Manager', 'Zookeeper']:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        # --- "Create operations (With GUI)" ---
        p_animal_id = request.form.get('animal_id')
        p_name = request.form.get('name')
        p_species = request.form.get('species')
        p_gender = request.form.get('gender')
        p_age = request.form.get('age')
        p_habitat_id = request.form.get('habitat_id')

        # Server-side validation
        error = None
        try:
            if not p_name or not p_species or not p_animal_id or not p_age or not p_habitat_id:
                error = 'Error: All fields are required.'
            elif int(p_age) < 0:
                error = 'Error: Age must be a positive number.'
            elif int(p_animal_id) <= 0:
                error = 'Error: Animal ID must be a positive number.'
        except (ValueError, TypeError):
            error = 'Error: Age and Animal ID must be valid numbers.'

        if error:
            flash(error, 'danger')
        else:
            # Validation passed, call the stored procedure
            cursor = mysql.connection.cursor()
            try:
                # --- "Procedures/Functions (With GUI)" ---
                cursor.execute("CALL sp_AddNewAnimal(%s, %s, %s, %s, %s, %s)",
                               (p_animal_id, p_name, p_species, p_gender, p_age, p_habitat_id))
                result = cursor.fetchall()
                # Exhaust the cursor to prevent "commands out of sync"
                while cursor.nextset(): pass 
                mysql.connection.commit() 
                
                # Show the message from the procedure (e.g., "Habitat full")
                if 'Error' in result[0]['message']:
                    flash(result[0]['message'], 'danger')
                else:
                    flash(result[0]['message'], 'success')
                    return redirect(url_for('animals'))
            except Exception as e:
                mysql.connection.rollback() 
                flash(f'Database Error: {str(e)}', 'danger')
            finally:
                cursor.close() 
    
    # GET request: Show the form, populating the habitat dropdown
    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT habitat_id, name, type FROM Habitat")
        habitats = cursor.fetchall()
    except Exception as e:
        flash(f"Error fetching habitats: {str(e)}", "danger")
        habitats = []
    finally:
        cursor.close()
    
    return render_template('add_animal.html', habitats=habitats)

@app.route('/delete_animal', methods=['POST'])
def delete_animal():
    """
    Handles deleting an animal.
    Hits "Delete operations (With GUI)".
    """
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    # Both Managers and Zookeepers can delete animals
    if session['role'] not in ['Manager', 'Zookeeper']:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))

    # --- "Delete operations (With GUI)" ---
    animal_id = request.form['animal_id']
    cursor = mysql.connection.cursor()
    
    try:
        cursor.execute("DELETE FROM Animal WHERE animal_id = %s", [animal_id])
        mysql.connection.commit()
        flash('Animal deleted successfully.', 'success')
        
    except Exception as e:
        mysql.connection.rollback()
        # Check for foreign key constraint errors (e.g., if animal is in 'Visits' table)
        if "1451" in str(e) or "foreign key constraint" in str(e).lower():
            flash('Error: Cannot delete animal. It is referenced by other records (e.g., visits).', 'danger')
        else:
            flash(f'Database Error: {str(e)}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('animals'))

# --- HABITAT MANAGEMENT ROUTES ---

@app.route('/habitats')
def habitats():
    """Displays the list of habitats and their current occupancy."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session['role'] != 'Manager':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))

    cursor = mysql.connection.cursor()
    try:
        # A subquery to count animals in each habitat
        cursor.execute("""
            SELECT 
                H.habitat_id, H.name, H.type, H.capacity,
                (SELECT COUNT(*) FROM Animal A WHERE A.habitat_id = H.habitat_id) AS current_occupancy
            FROM Habitat H
            ORDER BY H.name
        """)
        habitats = cursor.fetchall()
    except Exception as e:
        flash(f"Error fetching habitats: {str(e)}", "danger")
        habitats = []
    finally:
        cursor.close()
        
    return render_template('habitats.html', habitats=habitats)

@app.route('/delete_habitat', methods=['POST'])
def delete_habitat():
    """
    Handles deleting a habitat.
    Hits "Delete operations (With GUI)" and "Triggers (With GUI)".
    """
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session['role'] != 'Manager':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))

    # --- "Delete operations (With GUI)" ---
    habitat_id = request.form['habitat_id']
    cursor = mysql.connection.cursor()
    
    try:
        cursor.execute("DELETE FROM Habitat WHERE habitat_id = %s", [habitat_id])
        mysql.connection.commit()
        flash('Habitat deleted successfully.', 'success')
        
    except Exception as e:
        # --- "Triggers (With GUI)" ---
        # Catches the error from trg_Before_Habitat_Delete
        mysql.connection.rollback()
        if "Cannot delete habitat. It still contains animals" in str(e):
            flash('Error: Cannot delete habitat. It still contains animals.', 'danger')
        else:
            flash(f'Database Error: {str(e)}', 'danger')
    finally:
        cursor.close()

    return redirect(url_for('habitats'))

# --- VISITOR MANAGEMENT ROUTES ---

@app.route('/visitors')
def visitors():
    """Displays the list of all visitors."""
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session['role'] != 'Manager':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))

    cursor = mysql.connection.cursor()
    try:
        cursor.execute("SELECT * FROM Visitor ORDER BY l_name, f_name")
        visitors = cursor.fetchall()
    except Exception as e:
        flash(f"Error fetching visitors: {str(e)}", "danger")
        visitors = []
    finally:
        cursor.close()
        
    return render_template('visitors.html', visitors=visitors)

@app.route('/visitors/unvisited')
def visitors_unvisited():
    """
    Displays the report of visitors who haven't visited any animal.
    Hits "1 Nested Query (With GUI)".
    """
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session['role'] != 'Manager':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))

    cursor = mysql.connection.cursor()
    try:
        # --- "1 Nested Query (With GUI)" ---
        cursor.execute("""
            SELECT visitor_id, f_name, l_name
            FROM Visitor
            WHERE visitor_id NOT IN (SELECT DISTINCT visitor_id FROM Visits)
        """)
        visitors = cursor.fetchall()
    except Exception as e:
        flash(f"Error running report: {str(e)}", "danger")
        visitors = []
    finally:
        cursor.close()
        
    return render_template('visitors_unvisited.html', visitors=visitors)

@app.route('/edit_visitor/<int:visitor_id>', methods=['GET', 'POST'])
def edit_visitor(visitor_id):
    """
    Handles editing a visitor's details (GET for form, POST for update).
    Hits "Update operations (With GUI)".
    """
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session['role'] != 'Manager':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))

    cursor = mysql.connection.cursor()

    # --- "Update operations (With GUI)" ---
    if request.method == 'POST':
        f_name = request.form['f_name']
        l_name = request.form['l_name']
        age = request.form['age']
        phone_no = request.form['phone_no']

        # Server-side validation
        error = None
        try:
            if not f_name or not l_name or not phone_no:
                error = 'Error: Name and Phone Number fields cannot be empty.'
            elif int(age) <= 0:
                error = 'Error: Age must be a positive number.'
        except (ValueError, TypeError):
            error = 'Error: Age must be a valid number.'
        
        if error:
            flash(error, 'danger')
            # Re-fetch data to render the form again
            cursor.execute("SELECT * FROM Visitor WHERE visitor_id = %s", [visitor_id])
            visitor = cursor.fetchone()
            cursor.close()
            return render_template('edit_visitor.html', visitor=visitor)
            
        # Validation passed, run UPDATE
        try:
            cursor.execute("""
                UPDATE Visitor 
                SET f_name = %s, l_name = %s, age = %s, phone_no = %s
                WHERE visitor_id = %s
            """, (f_name, l_name, age, phone_no, visitor_id))
            mysql.connection.commit()
            flash('Visitor updated successfully.', 'success')
        except Exception as e:
            mysql.connection.rollback()
            flash(f"Error updating visitor: {str(e)}", "danger")
        finally:
            cursor.close()
            
        return redirect(url_for('visitors'))

    # --- GET request: Show the pre-filled form ---
    try:
        cursor.execute("SELECT * FROM Visitor WHERE visitor_id = %s", [visitor_id])
        visitor = cursor.fetchone()
        if not visitor:
            flash('Visitor not found.', 'danger')
            return redirect(url_for('visitors'))
    except Exception as e:
        flash(f"Error fetching visitor: {str(e)}", "danger")
        return redirect(url_for('visitors'))
    finally:
        cursor.close()

    return render_template('edit_visitor.html', visitor=visitor)

@app.route('/veterinary')
def view_veterinary_records():
    """
    Displays the list of all veterinary records.
    Uses JOINs to show animal and vet names.
    """
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    
    # Allow Managers, Zookeepers, and Vets to see this page
    if session['role'] not in ['Manager', 'Zookeeper', 'Veterinarian']:
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('dashboard'))

    cursor = mysql.connection.cursor()
    try:
        # This query JOINS 3 tables to get all the info we need
        cursor.execute("""
            SELECT 
                V.record_id,
                V.checkup_date,
                V.status,
                V.notes,
                A.name AS animal_name,
                E.name AS vet_name
            FROM Veterinary_Status V
            JOIN Animal A ON V.animal_id = A.animal_id
            JOIN Employee E ON V.vet_id = E.employee_id
            ORDER BY V.checkup_date DESC
        """)
        records = cursor.fetchall()
    except Exception as e:
        flash(f"Error fetching veterinary records: {str(e)}", "danger")
        records = []
    finally:
        cursor.close()
        
    return render_template('veterinary.html', records=records)

@app.route('/add_vet_record', methods=['GET', 'POST'])
def add_vet_record():
    """
    Handles adding a new veterinary record (GET for form, POST for submission).
    """
    if 'loggedin' not in session:
        return redirect(url_for('login'))
    if session['role'] not in ['Manager', 'Zookeeper', 'Veterinarian']:
        flash('You do not have permission to perform this action.', 'danger')
        return redirect(url_for('dashboard'))

    cursor = mysql.connection.cursor()

    if request.method == 'POST':
        # Get data from the form
        p_record_id = request.form.get('record_id')
        p_animal_id = request.form.get('animal_id')
        p_vet_id = request.form.get('vet_id')
        p_checkup_date = request.form.get('checkup_date')
        p_status = request.form.get('status')
        p_notes = request.form.get('notes')

        # --- Basic Validation ---
        error = None
        try:
            if not all([p_record_id, p_animal_id, p_vet_id, p_checkup_date, p_status]):
                error = 'Error: Record ID, Animal, Vet, Date, and Status are required fields.'
            elif int(p_record_id) <= 0:
                 error = 'Error: Record ID must be a positive number.'
        except (ValueError, TypeError):
             error = 'Error: Record ID must be a valid number.'
        
        if error:
            flash(error, 'danger')
            # If validation fails, we must re-load the data for the dropdowns
            cursor.execute("SELECT animal_id, name, species FROM Animal ORDER BY name")
            animals = cursor.fetchall()
            cursor.execute("SELECT employee_id, name FROM Employee WHERE role = 'Veterinarian' ORDER BY name")
            vets = cursor.fetchall()
            cursor.close()
            return render_template('add_vet_record.html', animals=animals, vets=vets)
        
        # --- Insert into DB ---
        try:
            cursor.execute("""
                INSERT INTO Veterinary_Status (record_id, animal_id, vet_id, checkup_date, status, notes)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (p_record_id, p_animal_id, p_vet_id, p_checkup_date, p_status, p_notes))
            
            mysql.connection.commit()
            flash('New veterinary record added successfully!', 'success')
            cursor.close()
            return redirect(url_for('view_veterinary_records'))
            
        except Exception as e:
            mysql.connection.rollback()
            # Check for duplicate primary key
            if "1062" in str(e) or "duplicate entry" in str(e).lower():
                 flash('Error: A record with this ID already exists.', 'danger')
            else:
                flash(f'Database Error: {str(e)}', 'danger')
            
            # Re-load dropdown data even after a DB error
            cursor.execute("SELECT animal_id, name, species FROM Animal ORDER BY name")
            animals = cursor.fetchall()
            cursor.execute("SELECT employee_id, name FROM Employee WHERE role = 'Veterinarian' ORDER BY name")
            vets = cursor.fetchall()
            cursor.close()
            return render_template('add_vet_record.html', animals=animals, vets=vets)

    # --- GET Request: Show the form ---
    try:
        # Fetch animals for the dropdown
        cursor.execute("SELECT animal_id, name, species FROM Animal ORDER BY name")
        animals = cursor.fetchall()
        
        # Fetch employees who are veterinarians for the dropdown
        cursor.execute("SELECT employee_id, name FROM Employee WHERE role = 'Veterinarian' ORDER BY name")
        vets = cursor.fetchall()
        
    except Exception as e:
        flash(f"Error fetching data for form: {str(e)}", "danger")
        animals = []
        vets = []
    finally:
        cursor.close()
        
    return render_template('add_vet_record.html', animals=animals, vets=vets)


# --- End of routes ---

if __name__ == '__main__':
    app.run(debug=True)

