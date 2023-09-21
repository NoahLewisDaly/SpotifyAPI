import os, base64, json
import spotipy
import time
from dotenv import load_dotenv
from requests import post, get
from flask import Flask, render_template, request, url_for, redirect, session
from spotipy.oauth2 import SpotifyOAuth

app = Flask(__name__)

load_dotenv()

app.config['SESSION_COOKIE_NAME'] = os.getenv("CLIENT_ID")
app.secret_key = os.getenv("CLIENT_SECRET")
TOKEN_INFO = 'token_info'

@app.route('/')
def login() :
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@app.route('/redirect')
def redirect_page():
    # clear the session
    session.clear()
    # get the authorization code from the request parameters
    code = request.args.get('code')
    # exchange the authorization code for an access token and refresh token
    token_info = create_spotify_oauth().get_access_token(code)
    # save the token info in the session
    session[TOKEN_INFO] = token_info
    # redirect the user to the save_discover_weekly route
    # return redirect(url_for('save_discover_weekly',_external=True))
    return render_template('index.html')






def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        # if the token info is not found, redirect the user to the login route
        redirect(url_for('login', _external=False))

    # check if the token is expired and refresh it if necessary
    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60
    if(is_expired):
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])

    return token_info


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id = os.getenv("CLIENT_ID"),
        client_secret = os.getenv("CLIENT_SECRET"),
        redirect_uri = url_for('redirect_page', _external=True),
        scope='user-library-read playlist-modify-public playlist-modify-private'
    )

app.run(debug=True)


# def get_token():
#     auth_string = client_id + ":" + client_secret
#     auth_bytes = auth_string.encode("utf-8")
#     auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

#     url = "https://accounts.spotify.com/api/token"
#     headers = {
#         "Authorization": "Basic " + auth_base64,
#         "Content-Type": "application/x-www-form-urlencoded"
#     }
#     data = {"grant_type": "client_credentials"}
#     result = post(url, headers=headers, data=data)
#     json_result = json.loads(result.content)
#     token = json_result["access_token"]
#     return token


# def get_auth_header(token):
#     return {"Authorization": "Bearer " + token}


# def search_for_artist(token, artist_name):
#     url = "https://api.spotify.com/v1/search"
#     headers = get_auth_header(token)
#     query = f"?q={artist_name}&type=artist&limit=1" # type could also be artist,track and limit is how many results appear

#     query_url = url + query
#     result = get(query_url, headers=headers)
#     json_result = json.loads(result.content)["artists"]["items"]
#     if len(json_result) == 0:
#         print("No Artist with this name exists.")
#         return None
#     return json_result[0]

# def get_songs_by_artist(token, artist_id):
#     url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
#     headers = get_auth_header(token)
#     result = get(url, headers = headers)
#     json_result = json.loads(result.content)["tracks"]
#     return json_result




# @app.route('/', methods=['GET'])
# def index():
#     return render_template('index.html')

# @app.route('/', methods=['POST'])
# def handle_form():
#     artist_name = request.form['artist_name']
#     token = get_token()
#     result = search_for_artist(token, artist_name)
#     if result is not None:
#         artist_id = result['id']
#         songs = get_songs_by_artist(token, artist_id)
#         return render_template('results.html', artist_name=artist_name, songs=songs)
#     return render_template('index.html')  # You can customize this further, e.g., display an error message

# if __name__ == '__main__':
#     app.run(debug=True)





# print("Enter an Artist Name: ")
# artist_name = input()

# token = get_token()
# result = search_for_artist(token, artist_name)
# if result != None:
#     artist_id = result["id"]
#     songs = get_songs_by_artist(token, artist_id)
#     for idx, song in enumerate(songs):
#         print(f"{idx + 1}. {song['name']}")


# @app.route('/saveDiscoverWeekly')
# def save_discover_weekly():
#     try:
#         # get the token info from the session
#         token_info = get_token()
#     except:
#         # if the token info is not found, redirect the user to the login route
#         print('User not logged in')
#         return redirect("/")

#     # create a Spotipy instance with the access token
#     sp = spotipy.Spotify(auth=token_info['access_token'])

#     # get the user's playlists
#     current_playlists =  sp.current_user_playlists()['items']
#     discover_weekly_playlist_id = None
#     saved_weekly_playlist_id = None

#     for playlist in current_playlists:
#         print(playlist['name'])

#     # find the Discover Weekly and Saved Weekly playlists
#     for playlist in current_playlists:
#         if(playlist['name'] == 'Discover Weekly'):
#             discover_weekly_playlist_id = playlist['id']
#         if(playlist['name'] == 'Saved Weekly'):
#             saved_weekly_playlist_id = playlist['id']

#     # if the Discover Weekly playlist is not found, return an error message
#     if not discover_weekly_playlist_id:
#         return 'Discover Weekly not found.'

#     # get the tracks from the Discover Weekly playlist
#     discover_weekly_playlist = sp.playlist_items(discover_weekly_playlist_id)
#     song_uris = []
#     for song in discover_weekly_playlist['items']:
#         song_uri= song['track']['uri']
#         song_uris.append(song_uri)

#     # add the tracks to the Saved Weekly playlist
#     sp.user_playlist_add_tracks("YOUR_USER_ID", saved_weekly_playlist_id, song_uris, None)

#     # return a success message
#     return ('Discover Weekly songs added successfully')

# function to get the token info from the session
