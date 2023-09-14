from flask import Flask, request, jsonify
import json, time, jwt
import mysql.connector
from functools import wraps
from flask_httpauth import HTTPBasicAuth
from datetime import datetime, timedelta

db_config = {
    "host": "127.0.0.1",
    "user": "root",
    "password": "",
    "database": "test",
    "port": 3306,  #  port - MySQL server
}

# Create a database connection
conn = mysql.connector.connect(**db_config)
cursor = conn.cursor()

# Create a table to store user data if it doesn't exist
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS users (
        
        username VARCHAR(255),  
        password VARCHAR(255),
        email VARCHAR(255)  
    );
     CREATE TABLE IF NOT EXISTS matches (
       match_id VARCHAR(25),
       team1 VARCHAR(25),
       team2 VARCHAR(25),
       date VARCHAR(25),
       venue VARCHAR(25)
      
    )
    """
)
cursor.close()


app = Flask(__name__)
auth = HTTPBasicAuth()
app.config["SECRET_KEY"] = "kjasdhlundaujw"


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get("token")
        if not token:
            return jsonify({"message": "token is missing"}), 403
        try:
            data = jwt.decode(token, app.config["SECRET_KEY"])
            expiration_time = data.get("exp")
            current_time = datetime.utcnow()
            if current_time > expiration_time:
                return jsonify({"message": "token has expired"}), 403
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "token has expired"}), 403
        except:
            return jsonify({"message": "invalid token"}), 403
        return f(*args, **kwargs)

    return decorated


@auth.verify_password
def verify_password(username, password):
    return username == "user" and password == "password123"


@app.route("/", methods=["GET"])
def home_page():
    data_set = {
        "Page": "Home",
        "Message": "This is the home page",
        "Timestamp": time.time(),
    }
    json_dump = json.dumps(data_set)
    return json_dump


@app.route("/api/matches", methods=["POST"])
@token_required
# @auth.login_required  # cache based. Dosent prompt till user closes the browser
def create_matches():
    data = request.get_json()  # Retrieve JSON data from request body
    match_id = data.get("match_id")
    team1 = data.get("team1")
    team2 = data.get("team2")
    date = data.get("date")
    venue = data.get("venue")

    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO matches ( match_id, team1, team2, date, venue ) VALUES (%s, %s, %s, %s, %s)",
        (
            match_id,
            team1,
            team2,
            date,
            venue,
        ),
    )
    cursor.close()

    # query = str(request.args.get("user"))  # /user/?user=ABC
    return jsonify({"message": "match created successfully", "match_id": "3"})


@app.route("/api/matches", methods=["GET"])
def matches():
    return jsonify(
        {
            "matches": [
                {
                    "match_id": "1",
                    "team_1": "India",
                    "team_2": "England",
                    "date": "2023-07-10",
                    "venue": "Lord's Cricket Ground",
                },
                {
                    "match_id": "2",
                    "team_1": "Australia",
                    "team_2": "New Zealand",
                    "date": "2023-07-11",
                    "venue": "Eden Garden Ground",
                },
            ]
        }
    )


@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()  # Retrieve JSON data from request body
    username = data.get("username")  # Get 'usr' from JSON data
    password = data.get("password")  # Get 'pwd' from JSON data
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    query = "SELECT username, password FROM users WHERE username = %s"
    cursor.execute(
        query,
        (username,),
    )
    result = cursor.fetchone()
    conn.commit()
    if result and result[1] == password:
        # Username and password match -> geenrate token
        expiration_time = datetime.utcnow() + timedelta(hours=1)
        token = jwt.encode(
            {"token ": "session", "exp": expiration_time},
            app.config["SECRET_KEY"],
        )
        return jsonify(
            {
                "status": "Login successful",
                "status_code": 200,
                "user_id": "12345",
                "token": token,
            }
        )
    else:
        # Username or password is incorrect
        return jsonify(
            {
                "status": "Invalid username or password, please retry ",
                "status_code": 401,
            }
        )


@app.route("/api/signup", methods=["POST"])
def signup():
    data = request.get_json()  # Retrieve JSON data from request body
    username = data.get("username")  # Get 'usr' from JSON data
    password = data.get("password")  # Get 'pwd' from JSON data
    email = data.get("email")
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO users (username, password,email) VALUES (%s, %s,%s)",
        (username, password, email),
    )
    conn.commit()
    cursor.close()
    conn.close()
    return (
        jsonify(
            {
                "status": "Admin account created successfully",
                "status_code": 200,
                "user_id": 12345,
            }
        ),
        200,
    )


# Sample match data
matches_data = {
    "1": {
        "match_id": "1",
        "team_1": "India",
        "team_2": "England",
        "date": "2023-07-10",
        "venue": "Lord's Cricket Ground",
        "status": "upcoming",
        "squads": {
            "team_1": [
                {"player_id": "123", "name": "Virat Kohli"},
                {"player_id": "124", "name": "Rohit Sharma"},
            ],
            "team_2": [
                {"player_id": "125", "name": "Joe Root"},
                {"player_id": "126", "name": "Ben Stokes"},
            ],
        },
    }
}

player_stats_data = {
    "123": {
        "player_id": "123",
        "name": "Virat Kohli",
        "matches_played": 200,
        "runs": 12000,
        "average": 59.8,
        "strike_rate": 92.5,
    },
    "456": {
        "player_id": "456",
        "name": "Jadeja",
        "matches_played": 350,
        "runs": 11000,
        "average": 79.8,
        "strike_rate": 62.5,
    },
}


@app.route("/api/players/<player_id>/stats", methods=["GET"])
def get_player_stats(player_id):
    if player_id in player_stats_data:
        player_stats = player_stats_data[player_id]
        return jsonify(player_stats)
    else:
        return jsonify({"message": "Player stats not found"}), 404


@app.route("/api/matches/<match_id>", methods=["GET"])
def get_match_details(match_id):
    if match_id in matches_data:
        match_details = matches_data[match_id]
        return jsonify(match_details)
    else:
        return jsonify({"message": "Match not found"}), 404


if __name__ == "__main__":
    app.run(port=7777)
