# Exercise Logger - Track and Analyze Your Workouts

#### Video Demo: https://youtu.be/FVPnNtJor8E


#### Description:

Workout Logger is a web application designed to help users keep track of their exercise routines and view statistical insights over time. With this app, users can easily log their workouts and monitor their progress through interactive charts and tables.


#### Features:

1. **Exercise Logging:** Users can log their exercise sessions by selecting the exercise type and entering details like the number of sets, repetitions, and weight lifted.
2. **Statistics:** The app provides users with insightful statistics on their workout history, including the total number of workouts, reps, weight lifted, sets, and the heaviest weight lifted.
3. **Interactive Charts:** The application utilizes JavaScript to display dynamic charts, making it easier for users to visualize their progress over time.
4. **User Authentication:** To ensure data privacy, the app implements password hashing using Werkzeug's security library for user authentication.
5. **Minimalistic Design:** The app's design focuses on simplicity and ease of use, providing users with a clean and intuitive interface to make the exercise logging process hassle-free.


#### Challenges Faced:

During development, one of the main challenges was to display data in different relations and properly link exercise logs to specific workouts. To overcome this, the project employed table joins in SQL to establish the necessary connections between the workout data and exercise details.


#### Technologies Used:

1. Flask: The web application is built using Flask, a micro web framework in Python, to handle routing and HTTP requests.
2. CS50's SQL Library: This library is utilized to interact with the SQLite database, allowing for efficient storage and retrieval of exercise and user data.
3. Werkzeug.Security: Used for password hashing to securely store user credentials in the database.
4. JavaScript: To enhance the user experience, JavaScript is incorporated to generate interactive charts for visualizing workout progress.
5. Bootstrap: The app utilizes Bootstrap's CSS styling to maintain a simple and aesthetically pleasing design.


#### Design Choices:

The design of the Exercise Logger prioritizes simplicity and usability, as the main objective was to create a user-friendly and minimalistic exercise logger. Bootstrap was chosen for its responsive layout and pre-designed components, which allowed for quicker development and ensured a consistent look across different devices.


#### Instructions:

To run the Exercise Logger, follow these steps:  

1. Ensure you have Python and Flask installed on your system.
2. Clone the project repository to your local machine.
3. Open a terminal and navigate to the project directory.
4. Create a virtual environment (optional but recommended).
5. Install the required dependencies listed in the requirements.txt file.
6. Set up the SQLite database by running the provided exercise_data.db file.
7. Execute the command ```flask run ``` to start the Flask development server.
8. Access the application by navigating to http://localhost:5000 in your web browser.

#### Additional Information:

The Exercise Logger was developed as part of a personal project to enhance programming skills while building a practical and useful application. The app is still a work in progress, and future updates may include more features, such as workout plan customization and social sharing capabilities. Feedback and suggestions are always welcome to improve the app further.