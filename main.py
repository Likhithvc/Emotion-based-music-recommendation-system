# main.py
"""
Main entrypoint for Emotion -> Spotify player.

Controls:
 - 'q' = capture current emotion and attempt to play mapped Spotify playlist
 - 'r' = force re-auth (delete cache) and then capture/play
 - ESC = exit

"""

import sys
import time
from pathlib import Path

import cv2

from config import MODEL_PATH, CONFIDENCE
from utils.camera import load_model, detect_and_draw
from utils.emotion_to_song import get_playlist_for_emotion
from utils.spotify_client import ensure_spotify_client, start_playback, force_reauth

def main():
    # ensure model exists
    model_path = Path(MODEL_PATH)
    if not model_path.exists():
        print(f"Model not found at {MODEL_PATH}. Place your .pt there or update config.py.")
        sys.exit(1)

    # load model
    print("Loading model:", MODEL_PATH)
    model = load_model(MODEL_PATH)

    # prepare face detector
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

    # open webcam
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open webcam. Close other camera apps / grant permissions and retry.")
        sys.exit(1)

    print("Webcam started. Press 'q' to capture emotion and play playlist.")
    print("Press 'r' to force re-auth (delete token cache and re-authorize).")
    print("Press ESC to exit.")

    current_emotion = None
    current_conf = 0.0

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Failed to read frame from webcam.")
                break

            # annotate frame with detections (face cascade + YOLO)
            annotated, dom_emotion, dom_conf = detect_and_draw(frame, model, face_cascade, imgsz=640, conf=CONFIDENCE, iou=0.45)

            # keep track of current dominant emotion
            if dom_emotion:
                current_emotion = dom_emotion
                current_conf = dom_conf

            # draw status
            status = f"Current: {current_emotion or 'None'} (conf {current_conf:.2f})"
            cv2.putText(annotated, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255,255,255), 2)

            cv2.imshow("Emotion Recommender - press q to capture", annotated)

            key = cv2.waitKey(1) & 0xFF
            if key == 27:  # ESC
                print("Exit requested. Goodbye.")
                break

            if key == ord('r'):
                # force reauthentication on next attempt
                print("Forcing re-auth: deleting cached token and will re-authorize on next play.")
                try:
                    force_reauth()
                except Exception as e:
                    print("Error forcing reauth:", e)
                continue

            if key == ord('q'):
                if current_emotion is None:
                    print("No emotion detected yet. Keep your face in frame and try again.")
                    continue

                print(f"Captured emotion: {current_emotion} (conf {current_conf:.2f})")
                playlist_uri = get_playlist_for_emotion(current_emotion)
                if not playlist_uri:
                    print("No playlist mapped for emotion:", current_emotion)
                    continue

                # Ensure spotify client (uses cache if present; will open browser on first run)
                try:
                    sp, oauth, token_info = ensure_spotify_client()
                except Exception as e:
                    print("Spotify authorization failed:", e)
                    print("If you want to re-auth manually, press 'r' and try again.")
                    continue

                # Attempt playback (start_playback will fallback to opening app/web)
                try:
                    ok = start_playback(sp, oauth, token_info, playlist_uri)
                    if ok:
                        print("Playback started via Spotify API.")
                    else:
                        print("Playback fallback used (opened app/web).")
                except Exception as e:
                    print("Playback process raised an exception:", e)
                # after attempt, break or continue depending on your preference — we'll exit after playing
                print("Done. Exiting program.")
                break

    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
