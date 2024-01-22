import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import error, login_required

# Configure application
app = Flask(__name__)


# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///exercise_data.db")

workout_types = db.execute("SELECT * FROM Exercises ORDER BY ExerciseName")

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    user_id = session["user_id"]
    if request.method == "POST":
        exercise_id = request.form.get("exercise_id")
        if not exercise_id:
            return error("Please insert exercise type")
        else:
            # Insert the workout data
            db.execute("INSERT INTO Workouts (UserID, WorkoutDate) VALUES (?, CURRENT_DATE)", user_id)

            # Get the last inserted row's WorkoutID for the current user
            result = db.execute("SELECT WorkoutID FROM Workouts WHERE UserID = ? ORDER BY WorkoutID DESC LIMIT 1", user_id)
            workout_id = result[0]['WorkoutID']

            # Insert a record into WorkoutExercises to link the workout and exercise
            try:
                db.execute("INSERT INTO WorkoutExercises (WorkoutID, ExerciseID) VALUES (?, ?)", workout_id, exercise_id)
            except Exception as e:
                print(f"Error while inserting into WorkoutExercises: {e}")

            workout_exercise_data = db.execute("SELECT * FROM WorkoutExercises WHERE WorkoutID = ?", workout_id)[0]
            # workout_exercise_id = result[0]['WorkoutExerciseID']

            exercise_data = db.execute("SELECT * FROM Exercises WHERE ExerciseID = ?", exercise_id)[0]
            workout_data = db.execute("SELECT * FROM Workouts WHERE WorkoutID = ?", workout_id)[0]

            rep_data = []

            return render_template("workout.html", exercise_data=exercise_data, workout_id=workout_id, workout_exercise_data=workout_exercise_data, rep_data=rep_data, workout_types=workout_types)

    else:
        """Show history of workouts"""
        user_id = session["user_id"]
        workout_history = db.execute("""
            SELECT 
                W.WorkoutID, 
                W.WorkoutDate, 
                E.ExerciseName, 
                WE.Sets, 
                WR.RepNumber,
                WE.Weight
            FROM 
                Workouts W 
            JOIN 
                WorkoutExercises WE on W.WorkoutID = WE.WorkoutID 
            JOIN 
                Exercises E on WE.ExerciseID = E.ExerciseID 
            JOIN 
                WorkoutReps WR on WE.WorkoutExerciseID = WR.WorkoutExerciseID
            WHERE 
                W.UserID = ? 
            ORDER BY 
                W.WorkoutDate DESC, 
                W.WorkoutID, 
                E.ExerciseName
        """, user_id)
        processed_workouts = []
        current_workout = {}

        for row in workout_history:
            if current_workout.get('WorkoutID') != row['WorkoutID']:
                if current_workout:
                    processed_workouts.append(current_workout)
                current_workout = {
                    'WorkoutID': row['WorkoutID'],
                    'WorkoutDate': row['WorkoutDate'],
                    'Exercises': [row['ExerciseName']],
                    'TotalSets': row['Sets'],
                    'TotalReps': row['RepNumber'],
                    'TotalWeight': row['Weight']
                }
            else:
                current_workout['Exercises'].append(row['ExerciseName'])
                current_workout['TotalSets'] += row['Sets']
                current_workout['TotalReps'] += row['RepNumber']
                current_workout['TotalWeight'] += row['Weight']

        if current_workout:
            processed_workouts.append(current_workout)
            print(processed_workouts)

        return render_template("index.html", workout_types=workout_types, processed_workouts=processed_workouts)


@app.route("/add", methods=["POST"])
def add():
    exercise_id = request.form.get("exercise_id")
    workout_id = request.form.get("workout_id")
    workout_exercise_id = request.form.get("workout_exercise_id")
    reps = request.form.get("reps")
    weight = request.form.get("weight")
    exercise_data = db.execute("SELECT * FROM Exercises WHERE ExerciseID = ?", exercise_id)[0]

    workout_exercise_data = db.execute("SELECT * FROM WorkoutExercises WHERE WorkoutID = ?", workout_id)[0]
    exercise_data = db.execute("SELECT * FROM Exercises WHERE ExerciseID = ?", exercise_id)[0]
    workout_data = db.execute("SELECT * FROM Workouts WHERE WorkoutID = ?", workout_id)[0]

    if not reps:
        return error("Must provide reps")
    elif not weight:
        return error("Must provide weight")
    
    try:
        reps = int(reps)
        weight = float(weight)
    except ValueError:
        return error("Reps and Weight must be valid numbers")

    # Find the current set number based on the existing rows in WorkoutReps for the given WorkoutExerciseID
    set_count = db.execute("SELECT COUNT(*) AS RepCount FROM WorkoutReps WHERE WorkoutExerciseID = ?", workout_exercise_id)
    current_set = set_count[0]['RepCount'] + 1

    # Insert a new row into WorkoutReps
    db.execute("INSERT INTO WorkoutReps (WorkoutExerciseID, SetNumber, RepNumber, Weight) VALUES (?, ?, ?, ?)",
            workout_exercise_id, current_set, reps, weight)

    # Now that the new rep has been added, recalculate total sets and total weight
    total_sets = db.execute("SELECT COUNT(*) AS TotalSets FROM WorkoutReps WHERE WorkoutExerciseID = ?", workout_exercise_id)[0]['TotalSets']
    total_weight = db.execute("SELECT SUM(Weight) AS TotalWeight FROM WorkoutReps WHERE WorkoutExerciseID = ?", workout_exercise_id)[0]['TotalWeight']
    total_reps = db.execute("SELECT SUM(RepNumber) AS TotalReps FROM WorkoutReps WHERE WorkoutExerciseID = ?", workout_exercise_id)[0]['TotalReps']

    # Update the WorkoutExercises table with the new totals
    db.execute("UPDATE WorkoutExercises SET Sets = ?, Weight = ? WHERE WorkoutExerciseID = ?", total_sets, total_weight, workout_exercise_id)


    rep_data = db.execute("SELECT * FROM WorkoutReps WHERE WorkoutExerciseID = ?", workout_exercise_id)
    return render_template("workout.html", exercise_data=exercise_data, workout_id=workout_id, workout_exercise_data=workout_exercise_data, rep_data=rep_data, workout_types=workout_types, total_sets=total_sets, total_weight=total_weight, total_reps=total_reps)



@app.route("/login", methods=["GET", "POST"])
def login():

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return error("Must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return error("Must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM Users WHERE Username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["Password"], request.form.get("password")):
            return error("Invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["UserID"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")
    
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure all form data was submitted
        if not request.form.get("username") or not request.form.get("password"):
            return error("Must provide all fields")

        if request.form.get("password") != request.form.get("confirmation"):
            return error("Passwords don't match")

        username = request.form.get("username")
        hash = generate_password_hash(request.form.get("password"))

        # Check if the username already exists in the database
        rows = db.execute("SELECT * FROM Users WHERE Username = ?", username)
        if len(rows) != 0:
            return error("This username is already registered")

        # Insert new user into the database
        db.execute("INSERT INTO Users (Username, Password) VALUES(?, ?)", username, hash)

        # Query database for the ID of the newly created user
        rows = db.execute("SELECT * FROM Users WHERE Username = ?", username)
        session["user_id"] = rows[0]["UserID"]

        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")

@app.route("/search", methods=["GET"])
@login_required
def search():
    user_id = session["user_id"]
    exercise_data = db.execute("SELECT * FROM Exercises")
    return render_template("search.html", exercise_data=exercise_data)


@app.route("/statistics", methods=["GET"])
@login_required
def statistics():
    user_id = session["user_id"]

    # Total Workouts
    total_workouts_result = db.execute(
        "SELECT COUNT(WorkoutID) AS TotalWorkouts FROM Workouts WHERE UserID = ?",
        user_id
    )
    total_workouts = total_workouts_result[0]["TotalWorkouts"]

    # Total Reps
    total_reps_result = db.execute(
        "SELECT SUM(RepNumber) AS TotalReps "
        "FROM WorkoutReps "
        "JOIN WorkoutExercises ON WorkoutReps.WorkoutExerciseID = WorkoutExercises.WorkoutExerciseID "
        "JOIN Workouts ON WorkoutExercises.WorkoutID = Workouts.WorkoutID "
        "WHERE Workouts.UserID = ?",
        user_id
    )
    total_reps = total_reps_result[0]["TotalReps"]

    # Total Weight Lifted
    total_weight_lifted_result = db.execute(
        "SELECT SUM(WorkoutReps.Weight * WorkoutReps.RepNumber) AS TotalWeightLifted "
        "FROM WorkoutReps "
        "JOIN WorkoutExercises ON WorkoutReps.WorkoutExerciseID = WorkoutExercises.WorkoutExerciseID "
        "JOIN Workouts ON WorkoutExercises.WorkoutID = Workouts.WorkoutID "
        "WHERE Workouts.UserID = ?",
        user_id
    )
    total_weight_lifted = total_weight_lifted_result[0]["TotalWeightLifted"]

    # Total Sets
    total_sets_result = db.execute(
        "SELECT SUM(Sets) AS TotalSets "
        "FROM WorkoutExercises "
        "JOIN Workouts ON WorkoutExercises.WorkoutID = Workouts.WorkoutID "
        "WHERE Workouts.UserID = ?",
        user_id
    )
    total_sets = total_sets_result[0]["TotalSets"]

    # Heaviest Weight
    heaviest_weight_result = db.execute(
        "SELECT MAX(WorkoutReps.Weight) AS HeaviestWeight "
        "FROM WorkoutReps "
        "JOIN WorkoutExercises ON WorkoutReps.WorkoutExerciseID = WorkoutExercises.WorkoutExerciseID "
        "JOIN Workouts ON WorkoutExercises.WorkoutID = Workouts.WorkoutID "
        "WHERE Workouts.UserID = ?",
        user_id
    )
    heaviest_weight = heaviest_weight_result[0]["HeaviestWeight"]

    return render_template(
        "statistics.html",
        total_workouts=total_workouts,
        total_reps=total_reps,
        total_weight_lifted=total_weight_lifted,
        total_sets=total_sets,
        heaviest_weight=heaviest_weight
    )
