# utils/emotion_to_song.py
# Maps emotion → playlist URI or keyword
PLAYLISTS = {
    "anger": "spotify:playlist:37i9dQZF1DX8tZsk68tuDw",     # Rock Hard
    "content": "spotify:playlist:37i9dQZF1DX4WYpdgoIcn6",   # Chill Vibes
    "disgust": "spotify:playlist:37i9dQZF1DX4VvfRBFClxm",   # Intense Beats
    "fear": "spotify:playlist:37i9dQZF1DWXRqgorJj26U",      # Calm Down
    "happy": "spotify:playlist:37i9dQZF1DXdPec7aLTmlC",     # Happy Hits
    "neutral": "spotify:playlist:37i9dQZF1DX4sWSpwq3LiO",   # Acoustic Chill
    "sad": "spotify:playlist:37i9dQZF1DX7qK8ma5wgG1",       # Sad Songs
    "surprise": "spotify:playlist:37i9dQZF1DXcBWIGoYBM5M",  # Top Hits
}

def get_playlist_for_emotion(emotion: str):
    return PLAYLISTS.get(emotion.lower())
