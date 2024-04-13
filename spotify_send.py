import requests
import os
import dotenv
from flask import Flask, request, redirect, render_template
from urllib.parse import urlencode
from status_discord import set_status
import sys
from flask_cors import CORS
import requests

global song_is_playing


dotenv.load_dotenv()

spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")
last_song = ""

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

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
    access_token = response_data['access_token']
    # Save the access token to a file
    with open("access_token.txt", "w") as f:
        f.write(access_token)
    return redirect("/user_interface")

@app.route('/get_currently_playing')
def get_currently_playing():
    with open("access_token.txt") as f:
        access_token = f.read()
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
    try:
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
    # except KeyError:
    #     print("KeyError occurred, reauthorizing...")
    #     # Reauthorize here
    #     return redirect("/")
    except Exception as e:
        try:
            # Try to make a request to refresh the token and try again
            return redirect("/")
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
    app.run(port=5000, debug=True)
