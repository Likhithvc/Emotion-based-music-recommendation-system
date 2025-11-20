# utils/spotify_client.py
"""
Spotify helpers with local token cache.
- Caches token info to disk (.cache-spotify by default).
- Reuses and refreshes token silently (no browser) when possible.
- Falls back to interactive auth if needed (first run or cache invalid).
"""

import os
import json
import webbrowser
import subprocess
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotify_config import CLIENT_ID, CLIENT_SECRET, REDIRECT_URI
import time

# Path to cache file (relative). Keep this file private.
CACHE_PATH = ".cache-spotify"

# OAuth scopes required
SCOPE = "user-read-playback-state user-modify-playback-state user-read-currently-playing"

def _write_cache(path, token_info):
    try:
        with open(path, "w") as fh:
            json.dump(token_info, fh)
    except Exception as e:
        print("Failed writing token cache:", e)

def _read_cache(path):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r") as fh:
            return json.load(fh)
    except Exception as e:
        print("Failed reading token cache:", e)
        return None

def _build_oauth():
    return SpotifyOAuth(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri=REDIRECT_URI,
        scope=SCOPE,
        cache_path=None,  # we manage cache file ourselves
        show_dialog=False  # don't force showing consent again if cached
    )

def run_interactive_auth():
    """
    Run interactive auth (opens browser), returns token_info dict.
    Also writes cache to CACHE_PATH.
    """
    oauth = _build_oauth()
    auth_url = oauth.get_authorize_url()
    print("Opening browser for Spotify authorization (first-time only).")
    print(auth_url)
    webbrowser.open(auth_url, new=1)

    # Manual redirect capture: instruct user to paste redirect URL OR use a temporary local server.
    # To keep simple and robust cross-platform, use the manual paste method here:
    print("After authorizing, Spotify will redirect to the redirect URI.")
    print("Copy the full redirect URL from the browser address bar and paste it here.")
    redirect_response = input("Paste redirect URL: ").strip()
    code = oauth.parse_response_code(redirect_response)
    if not code:
        # try to parse query param 'code'
        import urllib.parse as urlparse
        parsed = urlparse.urlparse(redirect_response)
        qs = urlparse.parse_qs(parsed.query)
        code = qs.get("code", [None])[0]
    token_info = oauth.get_access_token(code)
    # Save to disk
    _write_cache(CACHE_PATH, token_info)
    return token_info

def ensure_spotify_client():
    """
    Ensure we have a valid spotipy client and token_info.
    - Attempt to use CACHE_PATH silently.
    - If present and refreshable, refresh access token without browser.
    - If absent or refresh fails, run interactive auth (first time).
    Returns (sp, oauth, token_info).
    """
    oauth = _build_oauth()
    token_info = _read_cache(CACHE_PATH)

    if token_info:
        # check expiry
        expires_at = token_info.get("expires_at", 0)
        now = int(time.time())
        if expires_at - now < 60:
            # token near expiry -> try refresh
            refresh_token = token_info.get("refresh_token")
            if refresh_token:
                try:
                    new_token = oauth.refresh_access_token(refresh_token)
                    token_info = new_token
                    _write_cache(CACHE_PATH, token_info)
                except Exception as e:
                    print("Refresh failed:", e)
                    token_info = None
            else:
                token_info = None

    if not token_info:
        # interactive auth (first-run). This will ask user to authorize in browser.
        token_info = run_interactive_auth()

    sp = spotipy.Spotify(auth=token_info["access_token"])
    return sp, oauth, token_info

def get_active_device_id(sp):
    try:
        devices = sp.devices().get("devices", [])
        if not devices:
            return None
        # prefer a device named "Spotify" or the first active device
        for d in devices:
            if d.get("is_active"):
                return d.get("id")
        return devices[0].get("id")
    except Exception as e:
        print("devices() error:", e)
        return None

def start_playback(sp, oauth, token_info, playlist_uri):
    """
    Try API playback. On failure, open playlist in Spotify app / web as fallback.
    Returns True if API playback succeeded; False otherwise (fallback used).
    """
    try:
        # refresh token if needed
        if oauth and oauth.is_token_expired(token_info):
            token_info = oauth.refresh_access_token(token_info["refresh_token"])
            _write_cache(CACHE_PATH, token_info)
            sp = spotipy.Spotify(auth=token_info["access_token"])

        dev_id = get_active_device_id(sp)
        if not dev_id:
            raise RuntimeError("No active Spotify device found")

        sp.start_playback(device_id=dev_id, context_uri=playlist_uri)
        return True

    except Exception as e:
        print("API playback failed:", e)
        # fallback: try to open Spotify app with URI (Windows) or web fallback
        try:
            if playlist_uri.startswith("spotify:playlist:"):
                # try OS-level handler
                try:
                    os.startfile(playlist_uri)  # Windows
                except Exception:
                    # fallback to cmd start
                    try:
                        subprocess.run(["cmd", "/c", "start", "", playlist_uri], check=False)
                    except Exception:
                        pid = playlist_uri.split(":")[-1]
                        webbrowser.open(f"https://open.spotify.com/playlist/{pid}", new=1)
            else:
                webbrowser.open(playlist_uri, new=1)
        except Exception as e2:
            print("Fallback error:", e2)
        return False

def force_reauth():
    """Delete cache and re-run interactive auth on next ensure_spotify_client call."""
    try:
        if os.path.exists(CACHE_PATH):
            os.remove(CACHE_PATH)
            print("Deleted cache:", CACHE_PATH)
    except Exception as e:
        print("Failed to delete cache:", e)
