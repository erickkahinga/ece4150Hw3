from flask import Flask
# TODO add any necessary imports here

app = Flask(__name__)

# TODO add an appropriate Dockerfile and requirements.txt (separate files)

# TODO add any necessary helper functions here

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
    pass


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
    pass
    

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
    pass


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=80)
