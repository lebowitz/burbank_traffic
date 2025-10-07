#!/bin/bash

# Create output directory
mkdir -p processed

# Process each MP3 file
for file in *.mp3; do
    if [ -f "$file" ]; then
        echo "Processing $file..."

        output="processed/${file%.mp3}_no_silence.mp3"

        # Use ffmpeg silenceremove filter with 250ms padding
        # Parameters:
        # - stop_periods=-1: process all silence in the file
        # - stop_duration=0.5: silence must be at least 0.5s
        # - stop_threshold=-50dB: audio below this is considered silence
        # - detection=peak: use peak detection
        # We'll remove silence but leave 0.25s (250ms) padding by processing in segments

        ffmpeg -i "$file" \
            -af "silenceremove=start_periods=1:start_duration=0.5:start_threshold=-50dB:start_silence=0.25:stop_periods=-1:stop_duration=0.5:stop_threshold=-50dB:stop_silence=0.25:detection=peak" \
            -c:a libmp3lame -q:a 2 \
            "$output" -y 2>&1 | grep -E "Duration|size="

        if [ $? -eq 0 ]; then
            echo "✓ Created $output"
        else
            echo "✗ Failed to process $file"
        fi
        echo ""
    fi
done

echo "Silence removal complete! Files are in processed/"
