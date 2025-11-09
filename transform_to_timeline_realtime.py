#!/usr/bin/env python3
"""
Transform the transcript into a vertical timeline with 15-minute intervals
using real clock times (PDT) instead of processed audio timestamps.
"""

import re
import json
from html import escape
from datetime import datetime, timedelta

def parse_timestamp(href):
    """Extract part number and timestamp from href"""
    match = re.search(r'part(\d+)\.mp3#t=([\d.]+)', href)
    if match:
        part = int(match.group(1))
        timestamp = float(match.group(2))
        # Calculate absolute time: (part - 1) * 600 seconds + timestamp
        absolute_time = (part - 1) * 600 + timestamp
        return absolute_time
    return None

# Load timestamp mapping
with open('timestamp_mapping.json', 'r') as f:
    mapping = json.load(f)

compression_ratio = mapping['processed']['compression_ratio']
start_time = datetime.fromisoformat(mapping['recording_window']['start_utc'])
PDT_OFFSET = timedelta(hours=-7)

def map_processed_to_real_time(processed_seconds):
    """Map a timestamp in the processed audio to real UTC time"""
    real_seconds = processed_seconds / compression_ratio
    real_time = start_time + timedelta(seconds=real_seconds)
    return real_time

def utc_to_pdt(utc_dt):
    """Convert UTC datetime to PDT datetime"""
    return utc_dt + PDT_OFFSET

def format_time_pdt(utc_dt, show_seconds=False):
    """Format as PDT time string"""
    pdt_dt = utc_to_pdt(utc_dt)
    if show_seconds:
        return pdt_dt.strftime("%I:%M:%S %p").lstrip('0')
    else:
        return pdt_dt.strftime("%I:%M %p").lstrip('0')

# Read the original HTML
with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Extract all segments
segment_pattern = r'<div class="segment">\s*<a href="([^"]+)">([^<]+)</a>\s*</div>'
segments = re.findall(segment_pattern, content)

print(f"Found {len(segments)} segments")

# Parse segments with timestamps
timeline_segments = []
for href, text in segments:
    timestamp = parse_timestamp(href)
    if timestamp is not None:
        real_time = map_processed_to_real_time(timestamp)
        timeline_segments.append({
            'processed_time': timestamp,
            'real_time': real_time,
            'href': href,
            'text': text
        })

print(f"Parsed {len(timeline_segments)} segments with timestamps")

# Determine the time range
min_time = timeline_segments[0]['real_time']
max_time = timeline_segments[-1]['real_time']
print(f"Time range: {format_time_pdt(min_time)} to {format_time_pdt(max_time)} PDT")

# Create the new HTML structure
new_html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>BurbankTraffic - KBUR Tower Communications Oct 6-7, 2025</title>
    <style>
        :root {{
            --aviation-navy: #1a2332;
            --aviation-blue: #2c5aa0;
            --sky-blue: #5b9bd5;
            --light-sky: #e8f4fd;
            --runway-gray: #626570;
            --accent-orange: #ff6b35;
            --white: #ffffff;
            --light-gray: #f8f9fa;
            --timeline-gray: #d0d0d0;
        }}

        * {{
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Inter', 'Roboto', 'Helvetica Neue', sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 0;
            background: linear-gradient(to bottom, var(--light-sky) 0%, var(--white) 300px);
            background-attachment: fixed;
            color: var(--aviation-navy);
            line-height: 1.6;
        }}

        h1 {{
            color: var(--aviation-navy);
            font-weight: 600;
            font-size: 2.5rem;
            margin: 0 0 0.25rem 0;
            letter-spacing: -0.02em;
            padding: 40px 30px 0 30px;
        }}

        h1::before {{
            content: "✈";
            margin-right: 12px;
            color: var(--aviation-blue);
        }}

        body > p {{
            padding: 0 30px;
            margin: 0 0 30px 0;
        }}

        #audio-player {{
            width: 100%;
            margin: 0 0 30px 0;
            padding: 25px 30px;
            background: var(--white);
            border-top: 3px solid var(--aviation-blue);
            border-bottom: 1px solid #e0e0e0;
        }}

        audio {{
            width: 100%;
            height: 40px;
        }}

        #background {{
            background: var(--white);
            padding: 30px;
            margin: 0 0 30px 0;
            border-left: 4px solid var(--accent-orange);
            line-height: 1.7;
        }}

        #background h2 {{
            color: var(--aviation-navy);
            margin-top: 0;
            font-weight: 600;
            font-size: 1.75rem;
            letter-spacing: -0.01em;
        }}

        #background h3 {{
            color: var(--aviation-blue);
            margin-top: 1.5em;
            font-weight: 600;
            font-size: 1.25rem;
        }}

        #background ul {{
            margin: 15px 0;
            padding-left: 20px;
        }}

        #background li {{
            margin: 8px 0;
            padding-left: 8px;
        }}

        #background li strong {{
            color: var(--aviation-blue);
        }}

        .stats {{
            color: var(--runway-gray);
            font-style: italic;
            margin: 15px 0;
            padding: 15px;
            background: var(--light-gray);
            border-radius: 4px;
            border-left: 3px solid var(--sky-blue);
            font-size: 0.9rem;
        }}

        #background a {{
            color: var(--aviation-blue);
            text-decoration: none;
            border-bottom: 1px solid transparent;
            transition: border-color 0.2s ease;
        }}

        #background a:hover {{
            border-bottom-color: var(--aviation-blue);
        }}

        /* Timeline Styles */
        #transcript {{
            background: var(--white);
            padding: 30px 30px 30px 20px;
            margin: 0 0 30px 0;
            position: relative;
        }}

        .timeline-header {{
            padding-left: 100px;
            margin-bottom: 20px;
            color: var(--runway-gray);
            font-size: 0.9rem;
        }}

        .timeline-container {{
            position: relative;
            padding-left: 100px;
        }}

        /* Vertical timeline line */
        .timeline-container::before {{
            content: "";
            position: absolute;
            left: 95px;
            top: 0;
            bottom: 0;
            width: 1px;
            background: var(--timeline-gray);
        }}

        .timeline-segment {{
            position: relative;
            margin-bottom: 6px;
            padding: 8px 16px;
            border-left: 2px solid transparent;
            transition: all 0.2s ease;
        }}

        .timeline-segment:hover {{
            background-color: var(--light-sky);
            border-left-color: var(--aviation-blue);
            transform: translateX(2px);
        }}

        .time-marker {{
            position: absolute;
            left: -100px;
            width: 90px;
            text-align: right;
            font-size: 0.7rem;
            color: var(--runway-gray);
            font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
            font-weight: 400;
            padding-top: 2px;
        }}

        .segment-content a {{
            color: var(--aviation-navy);
            text-decoration: none;
            display: block;
            font-size: 0.92rem;
            line-height: 1.5;
        }}

        .segment-content a:hover {{
            color: var(--aviation-blue);
        }}

        /* 15-minute tick marks */
        .major-tick {{
            position: relative;
            margin: 25px 0;
            padding: 10px 16px;
            border-top: 2px solid var(--aviation-blue);
        }}

        .major-tick .time-marker {{
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--aviation-blue);
            padding-top: 0;
        }}

        /* Visual tick mark on the timeline */
        .major-tick::before {{
            content: "";
            position: absolute;
            left: -10px;
            top: -2px;
            width: 10px;
            height: 2px;
            background: var(--aviation-blue);
        }}

        @media (max-width: 768px) {{
            h1 {{
                font-size: 2rem;
                padding: 30px 20px 0 20px;
            }}

            body > p {{
                padding: 0 20px;
            }}

            #audio-player,
            #transcript,
            #background {{
                padding: 20px;
                margin: 0 0 20px 0;
            }}

            .timeline-container {{
                padding-left: 70px;
            }}

            .timeline-container::before {{
                left: 65px;
            }}

            .time-marker {{
                left: -70px;
                width: 65px;
                font-size: 0.65rem;
            }}

            .major-tick::before {{
                left: -10px;
            }}
        }}
    </style>
</head>
<body>
    <h1>BurbankTraffic</h1>
    <p style="color: var(--runway-gray); font-size: 1.1rem; font-weight: 500;">KBUR Tower Communications - October 6-7, 2025</p>

    <div id="background">
        <h2>Background</h2>
        <p>During the 2025 government shutdown, Burbank Airport experienced unusual operations when the control tower was unstaffed from 4:15 PM to 10:00 PM on October 6, 2025. Air traffic control was handled remotely by Southern California TRACON (Terminal Radar Approach Control) in San Diego instead of local tower controllers.</p>

        <p>This situation created a unique opportunity to study how commercial pilots operate using CTAF (Common Traffic Advisory Frequency) procedures - typically used at uncontrolled airports - at a normally towered commercial airport.</p>

        <h3>What Happened</h3>
        <ul>
            <li><strong>Air traffic controller shortage</strong> due to unpaid federal workers during the government shutdown</li>
            <li><strong>No local tower control</strong> for nearly 6 hours at a commercial airport</li>
            <li><strong>Remote operations</strong> from SoCal TRACON (normally handles approach/departure, not tower operations)</li>
            <li><strong>Delayed flights</strong> continuing past the normal 10 PM voluntary curfew</li>
            <li><strong>Pilots self-announcing</strong> positions and intentions on CTAF, similar to uncontrolled airport operations</li>
        </ul>

        <p>This recording captures commercial airline operations under these unusual circumstances, providing insight into pilot communication and coordination when normal tower services are unavailable.</p>

        <p class="stats">Recording: 4:00 PM - 10:00 PM PDT (6 hours) | 92:27 after silence removal | 1,020 transcript segments | Transcribed using OpenAI Whisper</p>

        <p style="margin-top: 15px;">
            <a href="https://github.com/lebowitz/burbank_traffic" target="_blank">
                📁 View source code and scripts on GitHub
            </a>
        </p>
    </div>

    <div id="transcript">
        <div class="timeline-header">
            Times shown in Pacific Daylight Time (PDT). Recording spans 4:00 PM to 10:00 PM.
        </div>
        <div class="timeline-container">
'''

# Generate timeline segments with major ticks every 15 minutes
# Round down to nearest 15 minutes for the first tick
first_tick_minutes = (min_time.hour * 60 + min_time.minute) // 15 * 15
current_tick_time = min_time.replace(minute=0, second=0, microsecond=0) + timedelta(minutes=first_tick_minutes)

# Make sure we start at or before the first segment
while current_tick_time > min_time:
    current_tick_time -= timedelta(minutes=15)

seg_idx = 0
while seg_idx < len(timeline_segments):
    # Check if we need to insert a major tick
    if current_tick_time <= timeline_segments[seg_idx]['real_time']:
        if current_tick_time >= min_time - timedelta(minutes=15):  # Only show ticks within range
            tick_label = format_time_pdt(current_tick_time)
            new_html += f'''            <div class="major-tick">
                <div class="time-marker">{tick_label}</div>
            </div>
'''
        current_tick_time += timedelta(minutes=15)
    else:
        # Add the segment
        seg = timeline_segments[seg_idx]
        time_label = format_time_pdt(seg['real_time'], show_seconds=True)
        new_html += f'''            <div class="timeline-segment" data-processed-time="{seg['processed_time']}" data-real-time="{seg['real_time'].isoformat()}">
                <div class="time-marker">{time_label}</div>
                <div class="segment-content">
                    <a href="{escape(seg['href'])}">{escape(seg['text'])}</a>
                </div>
            </div>
'''
        seg_idx += 1

# Add any remaining ticks
while current_tick_time <= max_time + timedelta(minutes=15):
    tick_label = format_time_pdt(current_tick_time)
    new_html += f'''            <div class="major-tick">
                <div class="time-marker">{tick_label}</div>
            </div>
'''
    current_tick_time += timedelta(minutes=15)

new_html += '''        </div>
    </div>

</body>
</html>'''

# Write the new HTML
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print(f"\n✓ Updated index.html with real-time vertical timeline")
print(f"Total segments: {len(timeline_segments)}")
print(f"Time range: {format_time_pdt(min_time)} - {format_time_pdt(max_time)} PDT")
