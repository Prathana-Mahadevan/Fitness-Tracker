from flask import Flask, render_template, request, redirect, url_for, session,jsonify
from flask import json
import mysql.connector
from datetime import datetime
from flask_cors import CORS
import matplotlib.pyplot as plt
from io import BytesIO
import base64

app = Flask(__name__)
CORS(app)

#secret key for secure session manegemnt
import secrets
app.secret_key = secrets.token_hex(16)  # Generates a 32-character random hexadecimal string as a secret key


db = mysql.connector.connect(
    host='localhost',
    user='root',
    password='hiru@MySql0307',
    database='fitness_app'
)

# Create a cursor to execute SQL queries
cursor = db.cursor()

# Function to get the user's ID from the session
def get_user_id():
    return session.get('user_id')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

       
        # Query the database to check if the user exists
        cursor.execute("SELECT * FROM users WHERE name = %s AND password = %s", (username, password))
        user_id = cursor.fetchone()

        if user_id:
            # User exists, store user_id in the session
            session['user_id'] = user_id[0]
            return redirect(url_for('personal_info'))
        else:
            return "Invalid credentials. Please try again."
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        phone_number = request.form['phone_number']
        address = request.form['address']

        # Insert user data into the MySQL database
        insert_query = "INSERT INTO users (name, password, phone_number, address) VALUES (%s, %s, %s, %s)"
        user_data = (name, password, phone_number, address)
        cursor.execute(insert_query, user_data)
        db.commit()  # Commit the transaction


        # Redirect to the user profile or another page after registration.
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/personal_info', methods=['GET', 'POST'])
def personal_info():
    if request.method == 'POST':
        # Retrieve personal information from the form
        user_id = get_user_id()  # Get the user's ID from the session

        if user_id is not None:
            fitness_level = request.form['fitness_level']
            age_category = request.form['age_category']
            gender = request.form['gender']
            weight = request.form['weight']
            height = request.form['height']
            exercise_goal = request.form['exercise_goal']
            time_frame = request.form['time_frame']

            # Insert personal information into the personal_info table
            insert_query = "INSERT INTO personal_info (user_id, fitness_level, age_category, gender, weight, height, exercise_goal, time_frame) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            personal_data = (user_id, fitness_level, age_category, gender, weight, height, exercise_goal, time_frame)

            cursor.execute(insert_query, personal_data)
            db.commit()

        # Redirect to the user profile or another page after submitting personal information.
            return redirect(url_for('customized_exercises'))
        else:
            return "user not logged in."

     # If the request method is 'GET', simply render the 'personal_info.html' template.
    return render_template('personal_info.html')
    
@app.route('/customized_exercises', methods=['GET', 'POST'])
def customized_exercises():
    # Retrieve user data from the database based on the user's ID
    user_id = get_user_id()
    if user_id is not None:
        cursor.execute("SELECT fitness_level, age_category, gender, exercise_goal, time_frame FROM personal_info WHERE user_id = %s", (user_id,))
        user_data = cursor.fetchone()

        if user_data:
            fitness_level, age_category, gender, exercise_goal, time_frame = user_data

            # Define exercises for different conditions
            exercises = []

            if fitness_level == 'beginner' and age_category == '10-19' and gender == 'Female' and exercise_goal == 'lose_weight':
                if time_frame == '3_months':
                    exercises = [
                        "March on Spot",
                        "Knee Bends",
                        "Arm Swing",
                        "Arm Circles",
                        "Bicep curls",
                        "Back Turns",
                        "Lunges",
                        "Leg Press",
                        "Side Legs",
                        "High Knees",
                        "Burpees",
                        "Warrior Pose",
                        "Bridge Pose",
                    ]
                elif time_frame == '6_months':
                    exercises = [
                        "March on Spot",
                        "Knee Bends",
                        "Arm Swing",
                        "Front Raises",
                        "Bicycle",
                        "Calf Raise",
                        "Side Leg",
                        "High Knees",
                        "Mountain Climbers",
                        "Tuck Jumps",
                        # Add more exercises for 6 months
                    ]
                elif time_frame == '9_months':
                    exercises = [
                        "March on Spot",
                        "Knee Bends",
                        "Arm Swing",
                        "Arm Circles",
                        "Lateral Raises",
                        "Back Turns",
                        "Lunges",
                        "Leg Press",
                        "Side Legs",
                        "High Knees",
                        "Front Raises",
                        "Bicycle",
                        "Calf Raise",
                        "Side Leg",
                        "High Knees",
                        "Mountain Climbers",
                        "Tuck Jumps",
                        # Add more exercises for 9 months
                    ]
            else:
                # Handle other combinations of user selections
                exercises = []

            return render_template('customized_exercises.html', exercises=exercises)
        else:
            return "user data not found"
    else:
        return "user not logged in."
    
@app.route('/exercise_bicep_curls', methods=['GET', 'POST'])
def exercise_bicep_curls():
    if request.method == 'POST':
        # Handle POST request
        time = request.json.get('time')
        rep_count = request.json.get('rep_count')

        user_id = get_user_id()  # Get the user's ID from the session

        if user_id is not None:
            try:
                # Get the current timestamp
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                # Initialize a new cursor
                with db.cursor() as cursor:
                    # Insert the exercise data into the MySQL database
                    insert_query = "INSERT INTO exercise_data (user_id, time, rep_count, timestamp) VALUES (%s, %s, %s, %s)"
                    exercise_data = (user_id, time, rep_count, timestamp)
                    cursor.execute(insert_query, exercise_data)
                    db.commit()
                return jsonify({'success': True}), 200
            except Exception as e:
                print("Error: ", str(e))
                db.rollback()  # Rollback the transaction in case of an error
                return jsonify({'error': str(e)}), 500  # Internal Server Error
        else:
            return jsonify({'error': 'User not logged in'}), 401  # Unauthorized
    else:
        # Handle GET request
        return render_template('gym_tracker.html')

@app.route('/exercise_data', methods=['POST'])
def exercise_data():
    if request.method == 'POST':
        time = request.json.get('time')
        rep_count = request.json.get('rep_count')

        user_id = get_user_id()  # Get the user's ID from the session

        if user_id is not None:
            try:
                # Get the current timestamp
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                # Initialize a new cursor
                with db.cursor() as cursor:
                    # Insert the exercise data into the MySQL database
                    insert_query = "INSERT INTO exercise_data (user_id, time, rep_count, timestamp) VALUES (%s, %s, %s, %s)"
                    exercise_data = (user_id, time, rep_count, timestamp)
                    cursor.execute(insert_query, exercise_data)
                    db.commit()
                return jsonify({'success': True}), 200
            except Exception as e:
                print("Error: ", str(e))
                db.rollback()  # Rollback the transaction in case of an error
                return jsonify({'error': str(e)}), 500  # Internal Server Error
        else:
            return jsonify({'error': 'User not logged in'}), 401  # Unauthorized

    return jsonify({'error': 'Invalid request'}), 400

@app.route('/exercise_webcam')
def exercise_webcam():
    return render_template('exercise_webcam.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

@app.route('/get_dashboard_data')
def get_dashboard_data():
    user_id = get_user_id()  # Get the user's ID from the session
    cursor.execute("SELECT timestamp, rep_count, time FROM exercise_data WHERE user_id = %s", (user_id,))
    data = cursor.fetchall()

    return jsonify(data)



if __name__ == '__main__':
    app.run(debug=True)
