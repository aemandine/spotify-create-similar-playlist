# Spotify "Create Similar Playlist"
Spotify "Create Similar Playlist" program, created using Naive Bayes classification!
The parameters used to classify each song are: acousticness, danceability, energy, instrumentalness, liveness, valence, speechiness, mode, tempo, and loudness

## Credits
The `lexicon.txt` file is from cjhutto's Github project (https://github.com/cjhutto/vaderSentiment).

## Instructions
1. (Optional, you can also just use the `songs.txt` file I've included) Run `build_song_list.py`, which combs over about 127,000 songs on Spotify from 50 different categories of music. This front-loads the work so when the user runs the main program, they don’t have to wait 15 minutes for all the songs to be added to `songs.txt`, my dataset of Spotify songs which contains the ID of each song along with all of its parameters (acousticness, speechiness, loudness, tempo, etc). Now that the dataset is ready, you can run the actual program!

2. When you run `app.py`, it connects to your Spotify account (if it’s your first time running the program, it opens a browser window asking for permission to modify your Spotify account). Once you've given the program access to your Spotify account, it welcomes you and lists all your public playlists.

3. Enter the number corresponding to the playlist you want to use as your base playlist for the "Create Similar Playlist" function—that's it! The program will do the rest of the work for you, creating the playlist and adding songs. It will also print out all the songs it's adding to the terminal.

## How it works
1. When you select a public playlist, `app.py` runs through every song in the playlist and pings Spotify for the parameters of each song (acousticness, etc). Since the parameters are relatively continuous from 0 to 1, I created LOW, MED, and HIGH buckets for each parameter.

2. The program creates a dictionary that maps each parameter to its three buckets (low, medium, and high), and for every song in the playlist I add to one of each parameter’s three buckets. At the end of this step, the dictionary contains a count of how many songs fall into the low, medium, and high buckets for each parameter.

3. I then run through each of the 127,000 songs from `songs.txt` and use Naive Bayes to calculate the probability that each song belongs in the playlist. Essentially, I do MAP with Laplace smoothing (since there are so many parameters, it’s very likely that some of the buckets will have zero in them, so we need Laplace smoothing):

`[#(X_1 = x_1 | Y = 1) + 1][#(X_2 =x_2 | Y = 1) + 1]...[#(X_n = x_n | Y = 1) + 1] / [#(Y = 1) + n]`

  In this case, Y = 1 means the song is in the playlist! And n = 10, since there are 10 parameters (acousticness, danceability, energy, instrumentalness, liveness, valence, speechiness, mode, tempo, and loudness). The x_i for each parameter is either 0, 1, or 2, based on the buckets LOW, MED, and HIGH. To get the counts for each X_i, I just look into the dictionary, which maps each parameter to the number of songs in the playlist with that bucket value!

4. I put all of these probabilities into a list (as part of a tuple containing the track ID) and then sort the list in descending order according to the probability of each tuple. That means the items at the front of the list belong most in the “Create Similar” playlist.

5. I run through the list of sorted probabilities and add songs into the similar playlist as long as they (1) are not already in the similar playlist, and (2) are not in the original playlist.

6. Now that I have all my songs, I get the valence (emotion) value of each song and calculate the average valence of the playlist. I parse through my `lexicon.txt` document (which maps words to valence values, created by cjhutto on Github: https://github.com/cjhutto/vaderSentiment) and make a dictionary mapping valence scores to words. Then, I find the closest dictionary key to the playlist’s real valence score, and choose 1-3 words that match that score to generate the playlist title.

7. Once I have the playlist title, I tap into the Spotify API again and create the playlist with the relevant emotional title, and then I add all 25 most similar songs!
