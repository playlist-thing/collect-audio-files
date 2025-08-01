# collect-audio-files

Python script that searches for audio files linked in a
[playlist-thing](https://playlist-thing.com) playlist and collects
them all in MP3 format in the correct order

The only requriement is the `ffmpeg` CLI in your PATH.

```bash
# collect audio files from Music and Downloads
python collect_audio_files.py playlist.json ~/Music ~/Downloads
```
