import json

# Read JSON data from file
with open('exercises.json', 'r') as json_file:
    json_data = json.load(json_file)

# Import the necessary modules
import sqlite3
import json

# Connect to the SQLite database
conn = sqlite3.connect('exercise_data.db')

# Define the cursor
cursor = conn.cursor()

# Read JSON data from file
with open('exercises.json', 'r') as json_file:
    json_data = json.load(json_file)

# Existing insert SQL command
insert_data_sql = "INSERT INTO Exercises (ExerciseID, ExerciseName, Description, MuscleGroup) VALUES (?, ?, ?, ?)"

# Insert data from JSON into the table
for index, exercise in enumerate(json_data):
    exercise_id = index + 1  # Adding 1 so the first ID is 1, not 0
    name = exercise['name']
    description = exercise['instructions']
    muscle_group = exercise['muscle']
    cursor.execute(insert_data_sql, (exercise_id, name, description, muscle_group))

# Don't forget to commit the changes
conn.commit()

# And finally, close the connection
conn.close()
