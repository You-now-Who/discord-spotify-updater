# Spotify Discord Status Updater

This is a flask server, that fetches the current song played on your Spotify account and updates your Discord status to reflect the same


## Getting Started

### 1. Environment Variables
You will need a Spotify application API `Client ID` and `Client Secret` in order to run the server locally and implement the Spotify authentication. You can make an application at Spotify [developer home](https://developer.spotify.com/). Further you will need to get your Discord User Token. A guide to get your Discord token is [available here](https://www.geeksforgeeks.org/how-to-get-discord-token/).

Add the environment variables to the `.env` file in the following format
```env
DISCORD_TOKEN="YOUR_DISCORD_TOKEN_HERE"
SPOTIFY_CLIENT_ID="YOUR_CLIENT_ID_HERE"
SPOTIFY_CLIENT_SECRET="YOUR_CLIENT_SECRET_HERE"
REDIRECT_URI="http://localhost:5000/callback"
```

#### Warning: Do not share your Discord token with anyone!
It can be used as a potential vulnerablity to access your Discord account.

### 2. Install this project with

```bash
  pip install -r requirements.txt
  python spotify_send.py
```
### 3. Authenticate 
Visit `http://localhost:5000/` and authenticate the application to access user's current playing song.

Thats it!
## Demo

![status updater](https://i.imgur.com/WVQ6hGh.png)
![discord profile](https://i.imgur.com/sL5A0ZD.png)
