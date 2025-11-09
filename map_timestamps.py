#!/usr/bin/env python3
"""
Map processed audio timestamps to real clock times based on original LiveATC files.

The workflow is:
1. Original files downloaded from LiveATC (30-min segments with known start times)
2. Silence removed from combined audio
3. Combined audio split into 10-minute parts for deep linking
4. This script maps the processed timestamps back to real UTC/PDT times
"""

from datetime import datetime, timedelta, timezone
import json

# Original file list from f.txt with their UTC start times
ORIGINAL_FILES = [
    ("KBUR3-Twr-Oct-06-2025-2300Z.mp3", "2025-10-06T23:00:00Z"),
    ("KBUR3-Twr-Oct-06-2025-2330Z.mp3", "2025-10-06T23:30:00Z"),
    ("KBUR3-Twr-Oct-07-2025-0000Z.mp3", "2025-10-07T00:00:00Z"),
    ("KBUR3-Twr-Oct-07-2025-0030Z.mp3", "2025-10-07T00:30:00Z"),
    ("KBUR3-Twr-Oct-07-2025-0100Z.mp3", "2025-10-07T01:00:00Z"),
    ("KBUR3-Twr-Oct-07-2025-0130Z.mp3", "2025-10-07T01:30:00Z"),
    ("KBUR3-Twr-Oct-07-2025-0200Z.mp3", "2025-10-07T02:00:00Z"),
    ("KBUR3-Twr-Oct-07-2025-0230Z.mp3", "2025-10-07T02:30:00Z"),
    ("KBUR3-Twr-Oct-07-2025-0300Z.mp3", "2025-10-07T03:00:00Z"),
    ("KBUR3-Twr-Oct-07-2025-0330Z.mp3", "2025-10-07T03:30:00Z"),
    ("KBUR3-Twr-Oct-07-2025-0400Z.mp3", "2025-10-07T04:00:00Z"),
    ("KBUR3-Twr-Oct-07-2025-0430Z.mp3", "2025-10-07T04:30:00Z"),
]

# Parse the start times
file_metadata = []
for filename, time_str in ORIGINAL_FILES:
    dt = datetime.fromisoformat(time_str.replace('Z', '+00:00'))
    file_metadata.append({
        'filename': filename,
        'start_utc': dt,
        'duration_seconds': 1800  # 30 minutes
    })

# Burbank is UTC-7 (PDT) during October
PDT_OFFSET = timedelta(hours=-7)

def utc_to_pdt(utc_dt):
    """Convert UTC datetime to PDT datetime"""
    return utc_dt + PDT_OFFSET

def format_time_pdt(utc_dt):
    """Format as PDT time string"""
    pdt_dt = utc_to_pdt(utc_dt)
    return pdt_dt.strftime("%I:%M %p")  # e.g., "04:15 PM"

def format_time_utc(utc_dt):
    """Format as UTC time string"""
    return utc_dt.strftime("%H:%MZ")  # e.g., "23:15Z"

# Calculate the recording window
first_start = file_metadata[0]['start_utc']
last_start = file_metadata[-1]['start_utc']
last_duration = file_metadata[-1]['duration_seconds']
recording_end = last_start + timedelta(seconds=last_duration)

print("Recording Window:")
print(f"  Start: {format_time_utc(first_start)} ({format_time_pdt(first_start)} PDT)")
print(f"  End:   {format_time_utc(recording_end)} ({format_time_pdt(recording_end)} PDT)")
print(f"  Original Duration: {(recording_end - first_start).total_seconds() / 60:.0f} minutes")
print()

# Load the transcript to see processed duration
with open('processed/KBUR3-Twr-Combined_transcript.json', 'r') as f:
    transcript = json.load(f)

# Find the last segment timestamp
if transcript['segments']:
    last_segment = transcript['segments'][-1]
    processed_duration = last_segment['end']
    print(f"Processed Duration (after silence removal): {processed_duration / 60:.1f} minutes")
    print(f"Silence removed: {(360 - processed_duration / 60):.1f} minutes")
    print()

# Create a simple linear mapping
# Assumption: silence is distributed relatively evenly across the recording
# More accurate would require per-file silence analysis, but this is a good start
compression_ratio = processed_duration / (recording_end - first_start).total_seconds()

print(f"Compression ratio: {compression_ratio:.3f}")
print(f"For every 1 second of processed audio ≈ {1/compression_ratio:.2f} seconds of real time")
print()

def map_processed_to_real_time(processed_seconds):
    """
    Map a timestamp in the processed audio to estimated real UTC time.

    This uses a simple linear interpolation based on the overall compression ratio.
    """
    real_seconds = processed_seconds / compression_ratio
    real_time = first_start + timedelta(seconds=real_seconds)
    return real_time

# Test with a few examples
print("Sample timestamp mappings:")
test_times = [0, 300, 900, 1800, 2700, 3600]  # 0, 5, 15, 30, 45, 60 minutes
for t in test_times:
    if t <= processed_duration:
        real_time = map_processed_to_real_time(t)
        print(f"  {t//60:2d}:{t%60:02d} processed → {format_time_pdt(real_time)} PDT ({format_time_utc(real_time)})")

# Save the mapping metadata
mapping_data = {
    'original_files': [
        {
            'filename': f['filename'],
            'start_utc': f['start_utc'].isoformat(),
            'start_pdt': format_time_pdt(f['start_utc']),
            'duration_seconds': f['duration_seconds']
        }
        for f in file_metadata
    ],
    'recording_window': {
        'start_utc': first_start.isoformat(),
        'end_utc': recording_end.isoformat(),
        'start_pdt': format_time_pdt(first_start),
        'end_pdt': format_time_pdt(recording_end),
        'original_duration_seconds': (recording_end - first_start).total_seconds(),
    },
    'processed': {
        'duration_seconds': processed_duration,
        'compression_ratio': compression_ratio,
    },
    'timezone_info': {
        'airport': 'KBUR',
        'timezone': 'PDT (UTC-7)',
        'note': 'Burbank Airport observes Pacific Daylight Time in October'
    }
}

with open('timestamp_mapping.json', 'w') as f:
    json.dump(mapping_data, f, indent=2)

print(f"\n✓ Saved mapping metadata to timestamp_mapping.json")
