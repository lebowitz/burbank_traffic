#!/usr/bin/env python3
import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Transcribe the combined file
audio_file_path = "processed/KBUR3-Twr-Combined.mp3"

print(f"Transcribing {audio_file_path}...")

with open(audio_file_path, "rb") as audio_file:
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=audio_file,
        response_format="verbose_json",
        timestamp_granularities=["segment"]
    )

# Save full JSON transcript
import json
output_json = audio_file_path.replace('.mp3', '_transcript.json')
with open(output_json, 'w') as f:
    json.dump(transcript.model_dump(), f, indent=2)

# Also save a readable text version with timestamps
output_txt = audio_file_path.replace('.mp3', '_transcript_timestamps.txt')
with open(output_txt, 'w') as f:
    for segment in transcript.segments:
        start = segment.start
        end = segment.end
        text = segment.text
        f.write(f"[{start:.2f}s - {end:.2f}s] {text}\n")

print(f"\n✓ JSON transcript saved to: {output_json}")
print(f"✓ Timestamped text saved to: {output_txt}")
print(f"\nPreview (first 3 segments):")
for i, segment in enumerate(transcript.segments[:3]):
    print(f"[{segment.start:.2f}s - {segment.end:.2f}s] {segment.text}")
