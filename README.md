# 🎭🎵 Emotion-Based Music Player

> Real-time facial emotion detection with YOLOv11 that plays mood-matched Spotify playlists

![Python](https://img.shields.io/badge/python-3.8+-blue.svg)
![YOLOv11](https://img.shields.io/badge/YOLOv11-Ultralytics-00FFFF.svg)
![Spotify](https://img.shields.io/badge/Spotify-1ED760?logo=spotify&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-5C3EE8?logo=opencv&logoColor=white)

## 📖 Overview

This project combines computer vision and music streaming to create an intelligent emotion-aware music player. Using a custom-trained YOLOv11 model, it detects facial expressions in real-time through your webcam and automatically plays Spotify playlists that match your current mood.

### ✨ Features

- 🎯 **Real-time Emotion Detection**: Detects 8 different emotions using YOLOv11
- 🎵 **Automatic Playlist Selection**: Maps emotions to curated Spotify playlists
- 📹 **Live Webcam Feed**: Visual feedback with bounding boxes and confidence scores
- 🔐 **Spotify Integration**: Seamless OAuth authentication with token caching
- ⚡ **Quick Controls**: Simple keyboard shortcuts for capture and playback

### 🎭 Supported Emotions

| Emotion | Playlist Theme |
|---------|---------------|
| 😠 Anger | Rock Hard |
| 😌 Content | Chill Vibes |
| 🤢 Disgust | Intense Beats |
| 😨 Fear | Calm Down |
| 😊 Happy | Happy Hits |
| 😐 Neutral | Acoustic Chill |
| 😢 Sad | Sad Songs |
| 😲 Surprise | Top Hits |

## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- Webcam/camera access
- Spotify Premium account (required for playback control)
- Spotify Developer App credentials

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/YOLOv11-emotion-music-player.git
   cd YOLOv11-emotion-music-player
   ```

2. **Create and activate virtual environment**
   ```powershell
   # Windows PowerShell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```
   
   ```bash
   # Linux/macOS
   python -m venv .venv
   source .venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Download/Place YOLOv11 Model**
   - Place your trained `best.pt` model file in the project root
   - Or update `MODEL_PATH` in `config.py` to point to your model location

5. **Configure Spotify API**
   - Create a Spotify Developer App at [Spotify Dashboard](https://developer.spotify.com/dashboard)
   - Note your `Client ID` and `Client Secret`
   - Add `http://127.0.0.1:8080/callback` to Redirect URIs in app settings
   - Update `spotify_config.py` with your credentials:
     ```python
     CLIENT_ID = "your_client_id_here"
     CLIENT_SECRET = "your_client_secret_here"
     REDIRECT_URI = "http://127.0.0.1:8080/callback"
     ```

## 🎮 Usage

### Running the Application

```bash
python main.py
```

### Controls

| Key | Action |
|-----|--------|
| `q` | Capture current emotion and play matched playlist |
| `r` | Force re-authentication (clears Spotify cache) |
| `ESC` | Exit application |

### First Run

1. Launch the application - your webcam feed will appear
2. On first run, you'll be redirected to Spotify for authorization
3. Grant the requested permissions
4. You'll be redirected back automatically (token is cached for future use)
5. Press `q` when your face is visible to detect emotion and start playback

## 📁 Project Structure

```
YOLOv11/
│
├── main.py                 # Main application entry point
├── config.py              # Model and emotion configuration
├── spotify_config.py      # Spotify API credentials (⚠️ DO NOT COMMIT)
├── requirements.txt       # Python dependencies
├── best.pt               # Trained YOLOv11 model (⚠️ DO NOT COMMIT if large)
│
├── utils/
│   ├── camera.py         # Camera handling and YOLO detection
│   ├── emotion_to_song.py # Emotion-to-playlist mapping
│   └── spotify_client.py  # Spotify API integration
│
└── models/               # Additional model files (if needed)
```

## ⚙️ Configuration

### `config.py`
```python
MODEL_PATH = "best.pt"           # Path to your YOLOv11 model
CONFIDENCE = 0.45                # Detection confidence threshold
EMOTION_NAMES = [...]           # Emotion class labels
```

### `utils/emotion_to_song.py`
Customize playlist URIs for each emotion:
```python
PLAYLISTS = {
    "happy": "spotify:playlist:YOUR_PLAYLIST_ID",
    # ... other emotions
}
```

## 🛠️ Technologies Used

- **[YOLOv11](https://github.com/ultralytics/ultralytics)**: State-of-the-art object detection
- **[OpenCV](https://opencv.org/)**: Computer vision and webcam handling
- **[Spotipy](https://spotipy.readthedocs.io/)**: Spotify Web API Python library
- **[NumPy](https://numpy.org/)**: Numerical computing

## 🔒 Security Notes

- **Never commit** `spotify_config.py` with real credentials
- **Never commit** `.cache-spotify` (Spotify token cache)
- Add sensitive files to `.gitignore`
- Consider using environment variables for production deployments

## 🐛 Troubleshooting

### Webcam Not Opening
- Ensure no other application is using the camera
- Grant camera permissions to your terminal/Python
- Try changing camera index in `cv2.VideoCapture(0)` to `1` or `2`

### Spotify Authentication Fails
- Verify `REDIRECT_URI` matches your Spotify App settings exactly
- Check that your Spotify App has the correct permissions
- Try deleting `.cache-spotify` and re-authenticating with `r` key

### Model Not Found
- Ensure `best.pt` exists in the project root
- Update `MODEL_PATH` in `config.py` if stored elsewhere

### Low Detection Accuracy
- Adjust `CONFIDENCE` threshold in `config.py`
- Ensure good lighting conditions
- Face the camera directly

## 📝 TODO / Future Enhancements

- [ ] Add multi-face detection support
- [ ] Implement emotion history tracking
- [ ] Create custom playlist generation based on mood patterns
- [ ] Add GUI with Tkinter/PyQt
- [ ] Support for local music playback (non-Spotify)
- [ ] Docker containerization
- [ ] Deploy as web application

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the project
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Ultralytics YOLOv11](https://github.com/ultralytics/ultralytics) for the amazing detection framework
- [Spotify for Developers](https://developer.spotify.com/) for the comprehensive API
- OpenCV community for computer vision tools

## 📧 Contact

Your Name - [@yourtwitter](https://twitter.com/yourtwitter) - your.email@example.com

Project Link: [https://github.com/yourusername/YOLOv11-emotion-music-player](https://github.com/yourusername/YOLOv11-emotion-music-player)

---

⭐ **Star this repo if you found it helpful!** ⭐
