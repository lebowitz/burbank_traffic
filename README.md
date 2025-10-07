# KBUR ATC Transcript

Automated transcription of Burbank Airport (KBUR) tower communications from October 6-7, 2025.

## Background

During the 2025 government shutdown, Burbank Airport experienced unusual operations when the control tower was unstaffed from 4:15 PM to 10:00 PM on October 6, 2025. Air traffic control was handled remotely by Southern California TRACON (Terminal Radar Approach Control) in San Diego instead of local tower controllers.

This situation created a unique opportunity to study how commercial pilots operate using CTAF (Common Traffic Advisory Frequency) procedures - typically used at uncontrolled airports - at a normally towered commercial airport.

### What Happened

- **Air traffic controller shortage** due to unpaid federal workers during the government shutdown
- **No local tower control** for nearly 6 hours at a commercial airport
- **Remote operations** from SoCal TRACON (normally handles approach/departure, not tower operations)
- **Delayed flights** continuing past the normal 10 PM voluntary curfew
- **Pilots self-announcing** positions and intentions on CTAF, similar to uncontrolled airport operations

This recording captures commercial airline operations under these unusual circumstances, providing insight into pilot communication and coordination when normal tower services are unavailable.

## Overview

This project downloads, processes, and transcribes air traffic control recordings from LiveATC.net, then generates an interactive HTML player with timestamped transcripts.

## Files

- `download_all.sh` - Downloads MP3 files from LiveATC archive
- `remove_silence.sh` - Removes silence from recordings (250ms padding)
- `transcribe.py` - Transcribes audio using OpenAI Whisper API
- `transcript_player.html` - Interactive HTML player with clickable timestamps
- `f.txt` - List of files to download

## Setup

1. Install dependencies:
```bash
python3 -m venv venv
source venv/bin/activate
pip install openai python-dotenv
```

2. Create `.env` file with your OpenAI API key:
```
OPENAI_API_KEY=your_key_here
```

## Usage

### Download recordings
```bash
./download_all.sh
```

### Remove silence
```bash
./remove_silence.sh
```

### Transcribe audio
```bash
source venv/bin/activate
python3 transcribe.py
```

### View transcript
Open `transcript_player.html` in your browser to see the timestamped transcript with audio playback.

## Features

- **Silence removal**: Uses ffmpeg to remove gaps >0.5s with 250ms padding
- **Whisper transcription**: OpenAI's Whisper API with segment-level timestamps
- **Combined audio**: All recordings merged into a single 92-minute file
- **Static HTML**: No JavaScript required, uses HTML5 media fragments

## Output

- Combined audio: `processed/KBUR3-Twr-Combined.mp3` (17 MB, 92:27 duration)
- Transcript: 1,020 segments with timestamps
- Interactive player with clickable timestamp links
