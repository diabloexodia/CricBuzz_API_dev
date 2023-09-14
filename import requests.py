import requests
import json

# Define the URL of your Flask API
url = "http://127.0.0.1:7777/api/matches"

# Create a dictionary with data to send in the POST request
data = {
    "match_id": "1234",
    "team1": "Team A",
    "team2": "Team B",
    "date": "10-11-2000",
    "venue": "Eden Gards",
}

# Send the POST request to the API with the data as paramenters
# to send it as JSON , use => json=data
# to send as params , use params=data
response = requests.post(url, json=data)

# Check the response
if response.status_code == 200:
    print("POST request successful:")
    print(response.json())
else:
    print("POST request failed with status code:", response.status_code)
