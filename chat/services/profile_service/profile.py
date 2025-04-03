from flask import Flask
# TODO add any necessary imports here

import os
import sys
import pymysql
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# TODO add an appropriate Dockerfile and requirements.txt (separate files)

# TODO add any necessary helper functions here
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=pymysql.cursors.DictCursor
    )

# TODO add any other necessary API endpoint handlers here

@app.route("/new_profile", methods=["POST"])
def new_profile():
    # TODO
    # Create a new profile based on the parameters passed
    # in the POST body as JSON. There will be three parameters:
    # user_name, password, bio. Each is a string.
    # On error, respond with JSON as follows:
    # {"error": "<Your error message here>"}
    # On success, respond with JSON as follows:
    # {"profile_id": <unique profile identifier here>}
    # where the profile identifier is an integer.
    # You must store the profile info the MySQL database.
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({"error": "No data provided"}), 400

    username = data.get("user_name")
    password = data.get("password")
    biography = data.get("biography", "")

    print(f"What form data looks like: {data}", file=sys.stderr)

    if not username or not password:
        return jsonify({"error": "Username or password missing"}), 400

    password_hash = generate_password_hash(password)

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO profiles (username, password_hash, biography)
                VALUES (%s, %s, %s)
            """
            cursor.execute(sql, (username, password_hash, biography))
        conn.commit()
    except pymysql.MySQLError as e:
        print(f"Error creating profile: {e}", file=sys.stderr)
        return jsonify({"error": "Could not create profile"}), 500
    finally:
        conn.close()

    return jsonify({"status": "profile_created"}), 201


@app.route("/validate_user", methods = ["POST"])
def validate_user():
    # TODO
    # Determine if the given login credentials are valid.
    # There will be two parameters passed in the POST
    # body as JSON: user_name and password. Each is a string.
    # On failure, respond with JSON as follows:
    # {"profile_id": None}
    # On success, respond with JSON as follows:
    # {"profile_id": <unique profile identifier here>}
    # where the profile identifier is an integer.
    data = request.get_json(silent=True) or request.form
    if not data:
        return jsonify({"error": "No data provided"}), 400

    username = data.get("user_name")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Username or password missing"}), 400

    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT profile_id, password_hash FROM profiles WHERE username=%s"
            cursor.execute(sql, (username,))
            row = cursor.fetchone()

            if not row:
                return jsonify({"error": "User not found"}), 404
            
            stored_hash = row["password_hash"]

            if check_password_hash(stored_hash, password):
                return jsonify({"profile_id": row["profile_id"]}), 200
            else:
                return jsonify({"error": "Invalid password"}), 401
    except pymysql.MySQLError as e:
        print(f"Error validating user: {e}", file=sys.stderr)
        return jsonify({"error": "DB error"}), 500
    finally:
        conn.close()
    

@app.route('/get_username/<int:profile_id>', methods=['GET'])
def get_username(profile_id):
    # TODO
    # Respond with the user name of the given profile, 
    # expresesd as an integer identifier, passed
    # as a URI parameter.
    # On failure, respond with JSON as follows:
    # {"message": "<Your error message here>"}
    # On success, respond with JSON as follows:
    # {"username": <the user's username>}
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            sql = "SELECT username FROM profiles WHERE profile_id=%s"
            cursor.execute(sql, (profile_id,))
            row = cursor.fetchone()

            if not row:
                return jsonify({"error": "User not found"}), 404
            
            return jsonify({"username": row["username"]}), 200
    except pymysql.MySQLError as e:
        print(f"Error retrieving username: {e}", file=sys.stderr)
        return jsonify({"error": "DB error"}), 500
    finally:
        conn.close()


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
