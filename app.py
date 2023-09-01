import os, base64, json
from dotenv import load_dotenv
from requests import post, get
from flask import Flask, render_template, request

app = Flask(__name__)

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_token():
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("utf-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "utf-8")

    url = "https://accounts.spotify.com/api/token"
    headers = {
        "Authorization": "Basic " + auth_base64,
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {"grant_type": "client_credentials"}
    result = post(url, headers=headers, data=data)
    json_result = json.loads(result.content)
    token = json_result["access_token"]
    return token


def get_auth_header(token):
    return {"Authorization": "Bearer " + token}


def search_for_artist(token, artist_name):
    url = "https://api.spotify.com/v1/search"
    headers = get_auth_header(token)
    query = f"?q={artist_name}&type=artist&limit=1" # type could also be artist,track and limit is how many results appear

    query_url = url + query
    result = get(query_url, headers=headers)
    json_result = json.loads(result.content)["artists"]["items"]
    if len(json_result) == 0:
        print("No Artist with this name exists.")
        return None
    return json_result[0]

def get_songs_by_artist(token, artist_id):
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers = headers)
    json_result = json.loads(result.content)["tracks"]
    return json_result




@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/', methods=['POST'])
def handle_form():
    artist_name = request.form['artist_name']
    token = get_token()
    result = search_for_artist(token, artist_name)
    if result is not None:
        artist_id = result['id']
        songs = get_songs_by_artist(token, artist_id)
        return render_template('results.html', artist_name=artist_name, songs=songs)
    return render_template('index.html')  # You can customize this further, e.g., display an error message

if __name__ == '__main__':
    app.run(debug=True)





# print("Enter an Artist Name: ")
# artist_name = input()

# token = get_token()
# result = search_for_artist(token, artist_name)
# if result != None:
#     artist_id = result["id"]
#     songs = get_songs_by_artist(token, artist_id)
#     for idx, song in enumerate(songs):
#         print(f"{idx + 1}. {song['name']}")
