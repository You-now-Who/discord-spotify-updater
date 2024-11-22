import requests
from dotenv import load_dotenv
import json
import os
import time  # Import the time module
import logging  # Import the logging module

load_dotenv()  # Load environment variables from .env file

global prev_song_is_none
prev_song_is_none = False

url = 'https://discord.com/api/v9/users/@me/settings'
headers = {
    'authorization': os.getenv('DISCORD_TOKEN'),
    'content-type': 'application/json',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/95.0.4638.69 Safari/537.36',
    'accept': '*/*',
}
PORT=os.environ.get('PORT')

def get_current_song():
    response = requests.get('http://localhost:'+str(PORT)+'/get_currently_playing')
    if response.status_code != 200:
        return None
    return response.json()

# Set up logging
# Replace yashy with your username
logging.basicConfig(filename='/Users\yashy\.custom-discord-status/discord_status.log', level=logging.INFO, format='%(asctime)s %(message)s')

def set_status(song):
    global prev_song_is_none
    res = get_current_song()
    if song is None:
        if prev_song_is_none:
            return
        i = '🎧 Not listening to anything'
        prev_song_is_none = True
    elif res is None:
        i = '🎧 Not listening to anything'
        prev_song_is_none = True
    elif 'item' in res:
        song = res['item']['name']
        artist = res['item']['artists'][0]['name']
        i = f'Currently listening 🎧 {song} - {artist}'
        prev_song_is_none = False
    else:
        i = '🎧 Not listening to anything'
        prev_song_is_none = True
    data = json.dumps({
        "custom_status": {
            "text": i
        }
    })
    response = requests.patch(url, headers=headers, data=data)
    print(response)
    print('for I: ', i)
    logging.info(f'Response Code: {response.status_code}')

    return response
