import spotipy
from numpy import random
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth

"""
export SPOTIPY_CLIENT_ID='fbfe32d5c5164e0dadee24a3f7159093'
export SPOTIPY_CLIENT_SECRET='ec2249d069be4506b68e22bb94dbb549'
export SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'
"""

# scopes: https://developer.spotify.com/documentation/general/guides/scopes/#ugc-image-upload
scope = 'user-read-private user-read-email playlist-modify-public playlist-modify-private ugc-image-upload user-top-read'
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope = scope))

PARAMETERS = ["acousticness", "danceability", "energy", "instrumentalness",
              "liveness", "valence", "speechiness", "mode", "tempo", "loudness"]

def add_line(file, line):
    file.write(line)
    file.write("\n")

def main():
    file = open("songs.txt", "w")
    category_num = 1

    categories = sp.categories(limit = 50)["categories"]["items"]
    for category in categories:
        print(str(category_num) + ") " + str(category["name"]))
        playlists = sp.category_playlists(category_id = category["id"], limit = 50)["playlists"]["items"]
        for playlist in playlists:
            songs = sp.playlist_items(playlist_id = playlist["id"], limit = 100)["items"]
            song_ids = []
            for song in songs:
                if song is not None and song["track"] is not None:
                    track_id = song["track"]["uri"]
                    song_ids.append(track_id)
            track_features = sp.audio_features(song_ids)
            for track in track_features:
                if track is None:
                    continue
                line = track["id"]
                #print(track)
                for PARAMETER in PARAMETERS:
                    if track is not None:
                        line += "," + str(track[PARAMETER])
                    else:
                        line += ",0"
                #print(line)
                add_line(file, line)
        category_num += 1
    file.close()

main()
