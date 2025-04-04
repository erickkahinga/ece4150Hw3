from flask import Flask, request, render_template, redirect, url_for, jsonify, make_response
import requests 
import os
import sys

app = Flask(__name__)

CHAT_SERVICE_PORT=5003

# Directly set the port number

@app.route("/", methods=['GET'])
def home():
    # redirect to login
    return redirect(url_for('login'))


@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == 'GET':
        return render_template("register.html")

    form_data = request.form

    profile_response = requests.post("http://profile_service/new_profile", json={
        "user_name": form_data["username"],
        "password": form_data["password"],
        "bio": form_data["bio"]
    })

    if profile_response.status_code != 200:
        print(f"profile_response.status_code: {profile_response.status_code}", file=sys.stderr)
        if profile_response.status_code == 400:
            return render_template("register_bad_field_blank.html")
        elif profile_response.status_code == 500:
            return render_template("register_bad_username_taken.html")
        else:
            return profile_response.text

    profile_data = profile_response.json()
    profile_id = profile_data.get("profile_id")
    
    if not profile_id:
        return make_response(jsonify({"error": "Invalid profile response"}), 400)

    return redirect(url_for('login'))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == 'GET':
        return render_template("login.html")

    # Get form data
    form_data = request.form
    username = form_data.get("username")
    password = form_data.get("password")
    # make this endpoint return profile id
    profile_response = requests.post("http://profile_service/validate_user", json={
        "user_name": username,
        "password": password
    })
    
    profile_response = profile_response.json()
    
    try:
        profile_id = profile_response["profile_id"]
    except:
        print(f"profile response: {profile_response}", file=sys.stderr)
        return render_template('login_bad.html')

    if profile_id:

        token_response = requests.post("http://auth_service/create_access_token", json={"profile_id": profile_id})
        if token_response.status_code != 200:
            return token_response.text
        access_token = token_response.json().get("access_token")

        if access_token:
            # Redirect directly with the profile_id and access_token as query parameters
            return render_template('login_ok.html', profile_id=profile_id, access_token=access_token, chat_service_port=CHAT_SERVICE_PORT)


    # If profile ID or access token is not found, redirect back to login page
    return render_template('login.html', app_message="Login failed")

@app.route("/logout", methods=["GET"])
def logout():
    access_token = request.args.get("access_token")
    if not access_token:
        print(f"error: Access token missing, 400", file=sys.stderr)
        return redirect(url_for('login'))
    
    print(f"access token: {access_token}", file=sys.stderr)
    
    auth_url = f"http://auth_service/remove_token?access_token={access_token}"

    try:
        response = requests.get(auth_url)
        if response.status_code == 200:
            print(f"message: Logged out successfully {response.status_code}", file=sys.stderr)
            return redirect(url_for('login'))
        else:
            return jsonify({"error": "Logout failed", "details": response.json()}), response.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=80)
