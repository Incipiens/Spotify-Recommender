import spotipy
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, render_template, redirect, url_for

app = Flask(__name__)

# Spotify API credentials
CLIENT_ID = '#'
CLIENT_SECRET = '#'
REDIRECT_URI = 'http://localhost:1410/'

# Authentication scope (for reading top tracks and getting recommendations)
SCOPE = 'user-top-read playlist-modify-public playlist-modify-private'

# Create a Spotify API client instance with OAuth
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope=SCOPE))

def get_top_tracks(time_range='short_term', limit=50):
    """
    Fetch the user's top tracks based on recent listening history.
    """
    top_tracks = sp.current_user_top_tracks(time_range=time_range, limit=limit)
    
    track_info = []
    for item in top_tracks['items']:
        track_info.append({
            'name': item['name'],
            'artist': item['artists'][0]['name'],
            'spotify_url': item['external_urls']['spotify'],
            'embed_url': f"https://open.spotify.com/embed/track/{item['id']}"
        })
    
    return track_info

def get_recommendations(track_ids, limit=5):
    """
    Get music recommendations based on top track IDs.
    """
    recommendations = sp.recommendations(seed_tracks=track_ids[:2], limit=limit)
    
    recommended_tracks = []
    for track in recommendations['tracks']:
        recommended_tracks.append({
            'name': track['name'],
            'artist': track['artists'][0]['name'],
            'spotify_url': track['external_urls']['spotify'],
            'embed_url': f"https://open.spotify.com/embed/track/{track['id']}"
        })
    
    return recommended_tracks

def create_playlist(playlist_name, track_uris):
    """
    Create a new Spotify playlist and add recommended tracks to it.
    """
    user_id = sp.current_user()['id']
    playlist = sp.user_playlist_create(user_id, playlist_name)
    sp.playlist_add_items(playlist['id'], track_uris)
    return playlist['external_urls']['spotify']

@app.route('/')
def index():
    # Fetch the user's top tracks
    top_tracks = get_top_tracks(time_range='short_term', limit=5)
    top_track_ids = [track['embed_url'].split('/')[-1] for track in top_tracks]
    
    # Get recommendations based on the top tracks
    recommended_tracks = get_recommendations(track_ids=top_track_ids, limit=5)
    recommended_track_uris = [f"spotify:track:{track['embed_url'].split('/')[-1]}" for track in recommended_tracks]
    
    # Create a playlist with the recommended tracks
    playlist_url = create_playlist("My New Music Recommendations", recommended_track_uris)
    
    return render_template('index.html', top_tracks=top_tracks, recommended_tracks=recommended_tracks, playlist_url=playlist_url)

if __name__ == '__main__':
    app.run(debug=True)