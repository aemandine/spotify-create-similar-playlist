import spotipy
from numpy import random
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy.oauth2 import SpotifyOAuth
from track import Track

"""
export SPOTIPY_CLIENT_ID='fbfe32d5c5164e0dadee24a3f7159093'
export SPOTIPY_CLIENT_SECRET='ec2249d069be4506b68e22bb94dbb549'
export SPOTIPY_REDIRECT_URI='http://localhost:8888/callback'
"""

# scopes: https://developer.spotify.com/documentation/general/guides/scopes/#ugc-image-upload
scope = 'user-read-private user-read-email playlist-modify-public playlist-modify-private ugc-image-upload user-top-read'
spotify = spotipy.Spotify(client_credentials_manager=SpotifyClientCredentials())
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope = scope))
TEXT_WIDTH = 75
PLAYLIST_LENGTH = 25

LOW = 0
MED = 1
HIGH = 2

# Represents (parameter_name, MED_FLOOR, HIGH_FLOOR)
PARAMETERS = [("acousticness", 0.33, 0.66),
              ("danceability", 0.33, 0.66),
              ("energy", 0.33, 0.66),
              ("instrumentalness", 0.33, 0.66),
              ("liveness", 0.4, 0.8),
              ("valence", 0.33, 0.66),
              ("speechiness", 0.33, 0.66),
              ("mode", 0.5, 1), # Mode will either be LOW (0) or HIGH (2)
              ("tempo", 100, 150), # Tempo ranges from 0 to over 200
              ("loudness", -15, -7)] # Values range from -60 to 0 (distribution mostly -15 to 0)

"""
Prints a message centered horizontally in the message output.
@input message (string): the message to be centered horizontally
"""
def print_centered(message):
    print(str(" " * ((TEXT_WIDTH - len(message)) // 2)) + message)

"""
Prints a message as a title (centered with dashes above and below)
@input messages (list of strings): the list of messages to be printed as title
"""
def print_title(messages):
    print(str("-" * TEXT_WIDTH))
    for message in messages:
        print_centered(message)
    print(str("-" * TEXT_WIDTH))

"""
Gets a valid playlist number to "Create Similar"
@input num_playlists (int): the number of playlists to choose from
@return playlist_index (int): a valid playlist index (0 -> num_playlists - 1)
"""
def get_valid_playlist_index(num_playlists):
    valid_num = False
    while not valid_num:
        user_input = input("Please enter a number 1 - " + str(num_playlists) + ": ")
        if user_input.isdigit():
            playlist_num = int(user_input)
            if 1 <= playlist_num <= num_playlists:
                valid_num = True
    playlist_index = playlist_num - 1
    return playlist_index

"""
Asks the user which playlist they want to "Create Similar" for
@return the playlist the user wants to create similar for
"""
def get_playlist_to_make_similar():
    print("Your public playlists are:")
    user_playlists = sp.current_user_playlists()["items"]
    for i in range(len(user_playlists)):
        print(str(i + 1) + ") " + user_playlists[i]["name"])
    playlist_index = get_valid_playlist_index(len(user_playlists))
    return user_playlists[playlist_index]

"""
Gets the audio features for every track in the list
@input tracks_raw (list): list of all the tracks in the playlist (raw data)
@return a list of Track objects
"""
def parse_tracks(tracks_raw):

    track_ids = []
    for track in tracks_raw:
        track_ids.append(track["track"]["id"])
    track_features = sp.audio_features(track_ids)

    tracks = []
    for track in track_features:
        track_object = Track(track, "dict")
        tracks.append(track_object)

    return tracks

"""
Fill buckets
@input tracks (list of Tracks): the tracks to parse
@returns a dictionary mapping parameters (acousticness, etc.) to list of three ints (# LOW, # MED, # HIGH)
"""
def fill_buckets(tracks):
    buckets = {}
    for PARAMETER_NAME, MED_FLOOR, HIGH_FLOOR in PARAMETERS:
        buckets[PARAMETER_NAME] = [0, 0, 0]
        for track in tracks:
            bucket = track.get_bucket(PARAMETER_NAME, MED_FLOOR, HIGH_FLOOR)
            buckets[PARAMETER_NAME][bucket] += 1
    return buckets

"""
Calculates the probability that a track belongs in the playlist.
@input track (Track): the track to find the probability for
@input frequency_buckets (dictionary): the frequencies of each parameter bucket
@return the probability that a track belongs in the playlist
"""
def track_probability(track, frequency_buckets, num_tracks):
    prob = 1
    for PARAMETER_NAME, MED_FLOOR, HIGH_FLOOR in PARAMETERS:
        bucket = track.get_bucket(PARAMETER_NAME, MED_FLOOR, HIGH_FLOOR)
        xj_prob = (frequency_buckets[PARAMETER_NAME][bucket] + 1) # Add 1 for Laplace smoothing
        xj_prob /= (num_tracks * len(PARAMETERS) + len(PARAMETERS)) # Add 1 per parameter for Laplace smoothing
        prob *= xj_prob
    return prob

"""
For use in sorted() function, gets the second element in a tuple.
"""
def get_second(x):
    return x[1]

"""
Create a new playlist
@input name (string): the name of the playlist to create
@return the id of the playlist created
"""
def create_new_playlist(name):
    # Create a new playlist
    user_id = sp.me()["id"]
    playlist_id = 0
    sp.user_playlist_create(user_id, name)
    playlists = sp.current_user_playlists()["items"]
    for playlist in playlists:
        if playlist["name"] == name:
            return playlist["id"]

"""
Generate title based on the emotion of the playlist
@input valence_score (float): the average emotional score of the playlist
@return the suggested title for the playlist
"""
def generate_title(valence_score):
    title = ""
    valence_dict = parse_lexicon()

    if valence_score not in valence_dict:
        values = sorted(valence_dict.keys())
        index = 0
        while index < len(values) and values[index] < valence_score:
            index += 1
        valence_score = values[index]

    word_list = valence_dict[valence_score]

    MIN_WORDS = 1
    MAX_WORDS = 3
    num_words = random.randint(MIN_WORDS, MAX_WORDS)
    for i in range(num_words):
        title += random.choice(word_list) + " "

    return title.strip()


"""
Parses the lexicon into a dictionary.
Uses valence dictionary (lexicon.txt) from cjhutto on Github (https://github.com/cjhutto/vaderSentiment)
-4 is worst negative sentiment, 4 is greatest positive sentiment (Normalized to 0 worst negative, 1 greatest positive)
Reversed to map floats to lists of words
@return the valence dictionary
"""
def parse_lexicon():
    LEXICON_FILE = "lexicon.txt"
    valence_dict = {}
    for line in open(LEXICON_FILE):
        options = line.strip().split("\t")
        sentiment = float(options[1])
        word = options[0]
        sentiment += 4 # turn into 0 - 8
        sentiment /= 8 # turn into 0 - 1
        if sentiment not in valence_dict:
            valence_dict[sentiment] = []
        valence_dict[sentiment].append(word)
    return valence_dict


"""
Creates a similar playlist
@input base_playlist (dictionary): the playlist to use as a base for "Create Similar"
"""
def create_similar_playlist(base_playlist):

    # Introduction
    print_title(["Creating similar playlist to \"" + base_playlist["name"] + "\"..."])
    tracks_raw = sp.playlist_items(base_playlist["id"])["items"]

    # Get the list of tracks in the playlist
    tracks = parse_tracks(tracks_raw)
    track_ids = []
    for track in tracks:
        track_ids.append(track.id)
    num_tracks = len(tracks)

    # Calculate the frequency buckets (LOW, MED, HIGH) for each parameter
    frequency_buckets = fill_buckets(tracks)

    # I've built up a songs.txt file of about 127,000 songs pulled from different Spotify categories
    SONGS_FILENAME = "songs.txt"
    potential_tracks = []
    for line in open(SONGS_FILENAME):
        parameters = line.split(",")
        potential_tracks.append(Track(parameters, "list"))

    # Get all the probabilities and then sort them in descending order
    probs = []
    for track in potential_tracks:
        track_prob = track_probability(track, frequency_buckets, num_tracks)
        probs.append((track.get_id(), track_prob, track))
    probs = sorted(probs, key=get_second, reverse=True)

    # Add the top 25 best songs to the playlist
    final_playlist = []
    valence_score = 0
    for id, prob, track in probs:
        if id not in track_ids and id not in final_playlist:
            final_playlist.append(id)
            valence_score += track.get_parameter("valence")
        if len(final_playlist) == PLAYLIST_LENGTH:
            break

    # Create a new playlist
    valence_score /= PLAYLIST_LENGTH
    playlist_name = generate_title(valence_score)
    playlist_id = create_new_playlist(playlist_name)

    # Add songs to the playlist
    print("Adding songs...")
    user_id = sp.me()["id"]
    for id in final_playlist:
        track = sp.track(id)
        print(track["name"])
    sp.user_playlist_add_tracks(user_id, playlist_id, final_playlist)

    print_title(["Your playlist \"" + playlist_name + "\" has been created!"])


def main():

    # Prints welcome message
    welcome_messages = ["Welcome to the SPOTIFY PLAYLIST GENERATOR, " + sp.current_user()["display_name"] + "!",
                        "This program replicates Spotify's \"Create Similar Playlist\" option."]
    print_title(welcome_messages)

    # Gets the playlist to make similar
    base_playlist = get_playlist_to_make_similar()

    # Makes a playlist similar to the base playlist
    create_similar_playlist(base_playlist)


# Start the program
main()
# undanceable_songs()
