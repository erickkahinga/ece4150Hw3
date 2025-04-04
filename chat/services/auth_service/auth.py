from flask import Flask, request, jsonify, abort
from uuid import uuid4
import os
import pymysql
import sys

app = Flask(__name__)


# Configure the database URI using environment variables
def db_connect():
    db_host = os.environ['DB_HOST']
    db_name = os.environ['DB_NAME']
    db_user = os.environ['DB_USER']
    db_password = os.environ['DB_PASSWORD']
    connection = pymysql.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        db=db_name,
        charset='utf8mb4',
        cursorclass=pymysql.cursors.DictCursor
    )
    return connection



# Create a new access token for a profile
@app.route("/create_access_token", methods=["POST"])
def create_access_token():
    profile_data = request.json
    profile_id = profile_data.get("profile_id")
    if not profile_id:
        abort(400, description="Missing profile_id")

    access_token = str(uuid4())

    # Establish a connection to the database
    connection = db_connect()

    try:
        with connection.cursor() as cursor:
            # Execute the query to check if the profile_id already exists
            sql_check = "SELECT * FROM Auth WHERE profile_id=%s"
            cursor.execute(sql_check, (profile_id,))
            existing_record = cursor.fetchone()

            # already logged in
            if existing_record:
                access_token = existing_record['access_token']
                return jsonify({"access_token": access_token, "profile_id": profile_id}), 200

            # Execute the query to insert the new auth record
            sql_insert = "INSERT INTO Auth (profile_id, access_token) VALUES (%s, %s)"
            cursor.execute(sql_insert, (profile_id, access_token))
            connection.commit()
    finally:
        connection.close()

    return jsonify({"access_token": access_token, "profile_id": profile_id}), 200

# Authenticate an access token
@app.route("/authenticate_token", methods=["POST"])
def authenticate_token():
    auth_data = request.json
    access_token = auth_data.get("access_token")
    profile_id = auth_data.get("profile_id")
    if not access_token or not profile_id:
        abort(400, description="Both access_token and profile_id are required")

    # Establish a connection to the database
    connection = db_connect()


    try:
        with connection.cursor() as cursor:
            # Execute the query to find the auth record
            sql = "SELECT * FROM Auth WHERE profile_id=%s AND access_token=%s"
            cursor.execute(sql, (profile_id, access_token))
            auth_record = cursor.fetchone()
    finally:
        connection.close()

    # Commented out the old SQLAlchemy based db access
    # auth_record = db.session.query(Auth).filter(Auth.profile_id == profile_id, Auth.access_token == access_token).first()
    if not auth_record:
        abort(401, description="Invalid token or profile_id")
    return jsonify({"message": "Authentication successful"})

# Retrieve an existing access token for a profile
@app.route("/retrieve_token", methods=["POST"])
def retrieve_token():
    auth_data = request.json
    profile_id = auth_data.get("profile_id")
    if not profile_id:
        abort(400, description="profile_id is required")

    # Establish a connection to the database
    connection = db_connect()

    try:
        with connection.cursor() as cursor:
            # Execute the query to find the auth record
            sql = "SELECT * FROM Auth WHERE profile_id=%s"
            cursor.execute(sql, (profile_id,))
            auth_record = cursor.fetchone()
    finally:
        connection.close()

    if not auth_record:
        abort(404, description="No token found for the given profile_id")

    return jsonify({"access_token": auth_record['access_token']})

@app.route("/remove_token", methods=["GET"])
def remove_token():
    access_token = request.args.get("access_token")
    if not access_token:
        return jsonify({"error": "Access token missing"}), 400
    
    connection = db_connect()
    
    try:
        with connection.cursor() as cursor:
            sql = "DELETE FROM Auth WHERE access_token=%s"
            cursor.execute(sql, (access_token,))
        connection.commit()
        return jsonify({"message": "Access token removed"}), 200
    except pymysql.MySQLError as e:
        print(f"Error removing access token: {e}", file=sys.stderr)
        return jsonify({"error": "Database error"}), 500
    finally:
        connection.close()



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
