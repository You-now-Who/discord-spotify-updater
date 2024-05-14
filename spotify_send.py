import requests
import os
import dotenv
from flask import Flask, request, redirect, render_template
from urllib.parse import urlencode
from status_discord import set_status
import sys
from flask_cors import CORS
import requests
import json

global access_token
global refresh_token
global song_is_playing
global last_song

access_token = None
last_song = ""

dotenv.load_dotenv()

spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
port=os.environ.get('PORT')
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = "http://localhost:" + str(port) + "/callback"

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

def get_token_values():
    try:
        global access_token
        global refresh_token
        data = {}
        with open("tokens.json", "r") as f:
            data = json.load(f)
            access_token = data['access_token']
            refresh_token = data['refresh_token']
        return data
    except:
        access_token = None
        refresh_token = None
        return data

def write_token_values(data):
    with open("tokens.json", "w") as f:
        json.dump(data, f)


from flask import Flask, request
import requests
import base64

app = Flask(__name__)

# A replacement function to the get_new_token function
def get_refresh_token(refresh_token):

    auth_value = base64.b64encode(f'{spotify_client_id}:{spotify_client_secret}'.encode('utf-8')).decode('utf-8')

    headers = {
        'content-type': 'application/x-www-form-urlencoded',
        'Authorization': f'Basic {auth_value}'
    }

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    response = requests.post('https://accounts.spotify.com/api/token', headers=headers, data=data)

    if response.status_code == 200:
        body = response.json()
        body['refresh_token'] = refresh_token
        print(body)
        write_token_values(body)
        # access_token = body['access_token']
        # refresh_token = body['refresh_token']
        # return {
        #     'access_token': access_token,
        #     'refresh_token': refresh_token
        # }, 200

    return response.content, response.status_code

def get_new_token(refresh_token):
    data = {
        "grant_type": "refresh_token",
        "refresh_token": refresh_token,
        "client_id": spotify_client_id
    }

    payload = {
        "method": "POST",
        "headers": {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        "body": urlencode(data)

    }

    response = requests.post("https://accounts.spotify.com/api/token", payload)
    response_data = response.json()
    print(response_data)
    # access_token = response_data['access_token']
    print("Access token refreshed")
    # write_token_values(response_data)
    return response_data

def set_status_method():
    global last_song
    song = get_currently_playing()
    # print(song)
    if song['item'] is None:
        if last_song != "":
            set_status({"item": {"name": "🎵 Not listening to anything right now!"}})
        else:
            print("No new song detected, no request made")
        last_song = ""
        return {"current_song": None, "error": "An error occurred"}


    if song['item']['name'] != last_song and song['item']['name'] is not None:
        print("New song detected, sending request")
        set_status(song)
    else:
        print("Same song, no request made")
        print("Current song is", song['item']['name'])

    last_song = song['item']['name']
    return song

@app.route('/')
def index():
    params = {
        "client_id": spotify_client_id,
        "response_type": "code",
        "redirect_uri": redirect_uri,
        "scope": "user-read-currently-playing",  # Add other scopes if needed
    }
    url = "https://accounts.spotify.com/authorize?" + urlencode(params)
    return redirect(url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "redirect_uri": redirect_uri,
        "client_id": spotify_client_id,
        "client_secret": spotify_client_secret,
    }
    response = requests.post("https://accounts.spotify.com/api/token", data=data)
    response_data = response.json()
    # print(response_data)
    access_token = response_data['access_token']
    refresh_token = response_data['refresh_token']
    # Save the access token to a file
    print(refresh_token)
    write_token_values(response_data)
    return redirect("/user_interface")

@app.route('/get_currently_playing')
def get_currently_playing():
    get_token_values()
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    response = requests.get("https://api.spotify.com/v1/me/player/currently-playing", headers=headers)
    try:
        song_is_playing = response.json()
        return response.json()
    except:
        return {"current_song": None, "item": None}
    
@app.route('/set_status', methods=["GET"])
def set_status_route():
    global last_song
    global access_token
    try:
        song = set_status_method()
        return song
    except Exception as e:
        try:
            # Try to make a request to refresh the token and try again
            # return redirect("/")
            # get_new_token(refresh_token)
            get_refresh_token(refresh_token)
            song = set_status_method()
            return song
            
        except Exception as e:    
            print("Refreshing token failed", e)
            return {"error": "An error occurred", "error_code": str(e)}

@app.route('/user_interface')
def user_interface():
    global song_is_playing
    try:
        song_is_playing=get_currently_playing()
    except:
        song_is_playing = {"current_song": None}
    
    return render_template("index.html", song=song_is_playing)

if __name__ == "__main__":
    get_token_values()
    # get_refresh_token(refresh_token)
    app.run(port=int(port), debug=True)