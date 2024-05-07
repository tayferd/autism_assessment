from app import app, initialize_database

if __name__ == "__main__":
    initialize_database()  # Ensure DB is initialized
    app.run(debug=True, host='0.0.0.0')
