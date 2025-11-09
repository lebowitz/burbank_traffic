#!/usr/bin/env python3
"""
Transform the transcript into a vertical timeline with 15-minute intervals
"""

import re
from html import escape

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

def format_time(seconds):
    """Format seconds as HH:MM:SS or MM:SS"""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)

    if hours > 0:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes}:{secs:02d}"

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
        timeline_segments.append({
            'time': timestamp,
            'href': href,
            'text': text
        })

print(f"Parsed {len(timeline_segments)} segments with timestamps")

# Determine the range
max_time = max(seg['time'] for seg in timeline_segments)
print(f"Max time: {format_time(max_time)} ({max_time:.2f} seconds)")

# Generate timeline HTML
timeline_html = []

# Add segments to timeline
for seg in timeline_segments:
    time_label = format_time(seg['time'])
    timeline_html.append(f'''        <div class="timeline-segment" data-time="{seg['time']}">
            <div class="time-marker">{time_label}</div>
            <div class="segment-content">
                <a href="{escape(seg['href'])}">{escape(seg['text'])}</a>
            </div>
        </div>''')

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

        #airport-diagram {{
            background: var(--white);
            padding: 30px;
            margin: 0 0 30px 0;
            text-align: center;
            border-left: 4px solid var(--sky-blue);
        }}

        #airport-diagram h2 {{
            color: var(--aviation-navy);
            margin-top: 0;
            font-weight: 600;
            font-size: 1.75rem;
        }}

        #airport-diagram img {{
            max-width: 100%;
            height: auto;
            border: 2px solid var(--light-gray);
            border-radius: 4px;
            box-shadow: 0 4px 12px rgba(26, 35, 50, 0.08);
        }}

        /* Timeline Styles */
        #transcript {{
            background: var(--white);
            padding: 30px 30px 30px 20px;
            margin: 0 0 30px 0;
            position: relative;
        }}

        .timeline-container {{
            position: relative;
            padding-left: 80px;
        }}

        .timeline-segment {{
            position: relative;
            margin-bottom: 8px;
            padding: 10px 16px;
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
            left: -80px;
            width: 70px;
            text-align: right;
            font-size: 0.75rem;
            color: var(--runway-gray);
            font-family: 'SF Mono', 'Monaco', 'Courier New', monospace;
            font-weight: 500;
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
            margin: 20px 0;
            padding: 8px 16px;
            border-top: 1px solid var(--timeline-gray);
        }}

        .major-tick .time-marker {{
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--aviation-blue);
            padding-top: 0;
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
            #background,
            #airport-diagram {{
                padding: 20px;
                margin: 0 0 20px 0;
            }}

            .timeline-container {{
                padding-left: 60px;
            }}

            .time-marker {{
                left: -60px;
                width: 55px;
                font-size: 0.7rem;
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

        <p class="stats">Recording: 92:27 duration | 1,020 transcript segments | Transcribed using OpenAI Whisper</p>

        <p style="margin-top: 15px;">
            <a href="https://github.com/lebowitz/burbank_traffic" target="_blank">
                📁 View source code and scripts on GitHub
            </a>
        </p>
    </div>

    <div id="transcript">
        <div class="timeline-container">
'''

# Insert timeline segments with major ticks every 15 minutes
current_major = 0  # Track major tick marks (every 15 minutes = 900 seconds)
for seg in timeline_segments:
    # Check if we need to insert a major tick
    seg_major = int(seg['time'] // 900)
    while current_major <= seg_major:
        if current_major > 0:  # Don't add tick at 0:00
            tick_time = current_major * 900
            tick_label = format_time(tick_time)
            new_html += f'''            <div class="major-tick">
                <div class="time-marker">{tick_label}</div>
            </div>
'''
        current_major += 1

    # Add the segment
    time_label = format_time(seg['time'])
    new_html += f'''            <div class="timeline-segment" data-time="{seg['time']}">
                <div class="time-marker">{time_label}</div>
                <div class="segment-content">
                    <a href="{escape(seg['href'])}">{escape(seg['text'])}</a>
                </div>
            </div>
'''

new_html += '''        </div>
    </div>

    <div id="airport-diagram">
        <h2>Airport Diagram</h2>
        <img src="data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAwIiBoZWlnaHQ9IjQwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNjAwIiBoZWlnaHQ9IjQwMCIgZmlsbD0iI2Y1ZjVmNSIvPjx0ZXh0IHg9IjMwMCIgeT0iMjAwIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTgiIHRleHQtYW5jaG9yPSJtaWRkbGUiIGZpbGw9IiM2NjY2NjYiPkFpcnBvcnQgZGlhZ3JhbSBwbGFjZWhvbGRlcjwvdGV4dD48L3N2Zz4=" alt="KBUR Airport Diagram">
        <p style="margin-top: 15px; color: var(--runway-gray); font-size: 0.9rem;">
            Airport diagram placeholder - shows runway layout and taxiway configuration
        </p>
    </div>

</body>
</html>'''

# Write the new HTML
with open('index_timeline.html', 'w', encoding='utf-8') as f:
    f.write(new_html)

print("Generated index_timeline.html")
print(f"Total segments: {len(timeline_segments)}")
print(f"Duration: {format_time(max_time)}")
