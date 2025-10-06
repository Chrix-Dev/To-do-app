To-Do App API

A simple and efficient To-Do List API built with FastAPI, designed to help users manage their daily tasks efficiently.
This project demonstrates backend development skills such as CRUD operations, authentication, and database integration using SQLAlchemy ORM.

Features

* User Authentication (JWT) for secure access

* CRUD operations for creating, reading, updating, and deleting tasks

* SQLite database integration with SQLAlchemy ORM

* Auto-generated API documentation via Swagger UI (/docs) and ReDoc (/redoc)

* Structured error handling with proper HTTP responses

* Built with FastAPI for high performance and easy scalability

Tech Stack

* Backend Framework: FastAPI

* Programming Language: Python

* Database: SQLite (via SQLAlchemy ORM)

* Authentication: JSON Web Token (JWT)

* Tools: Uvicorn, Pydantic, Passlib, Git, GitHub, Vs code

Installation and Setup

Follow these steps to set up and run the application locally:

# Clone the repository
git clone https://github.com/Chrix-Dev/To-do-app.git

# Navigate into the project directory
cd To-do-app

# Create and activate a virtual environment
python -m venv venv
venv\Scripts\activate      # On Windows
# source venv/bin/activate # On Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Run the FastAPI application
uvicorn main:app --reload


| Method | Endpoint           | Description                               | Auth Required |
| :----- | :----------------- | :---------------------------------------- | :------------ |
| POST   | `/register`        | Register a new user                       | No            |
| POST   | `/login`           | Login and receive a JWT token             | No            |
| POST   | `/tasks/`          | Create a new task                         | Yes           |
| GET    | `/tasks/`          | Retrieve all tasks for the logged-in user | Yes           |
| GET    | `/tasks/{task_id}` | Retrieve a specific task                  | Yes           |
| PUT    | `/tasks/{task_id}` | Update a task                             | Yes           |
| DELETE | `/tasks/{task_id}` | Delete a task                             | Yes           |
| DELETE | `/tasks/{task_id}` | Delete multiple tasks.                    | Yes.          |

Authentication

This project uses JWT (JSON Web Tokens) for authentication.
To access protected routes:

* Login to obtain a token.

* Click “Authorize” in the FastAPI docs.

* Enter your token.

Project Structure
To-do-app

* main.py   - Main application file containing CRUD, Auth, and DB setup.
 
* requirements.txt - Project dependencies.

* .gitignore - Hidden files and environment configuration.

* README.md - Project documentation.

Future Improvements

* Add email verification for new users

* Implement task priority and deadlines

* Support PostgreSQL for production environments

* Containerize the app using Docker
  
* Refactor code into smaller, modular files for better scalability and maintainability


Author

Umunna Chibuenyim Chiemere

Backend Developer Intern

Email: beingchris21@gmail.com

