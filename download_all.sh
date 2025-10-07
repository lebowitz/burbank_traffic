#!/bin/bash

# Read each line from f.txt and convert wget commands to curl with headers
while IFS= read -r line; do
    # Remove carriage returns and extract URL from wget command
    url=$(echo "$line" | tr -d '\r' | sed 's/wget //')

    # Extract filename from URL
    filename=$(basename "$url")

    echo "Downloading $filename..."

    curl "$url" \
      -H 'accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7' \
      -H 'accept-language: en-US,en;q=0.9,es;q=0.8,ms;q=0.7' \
      -H 'cache-control: no-cache' \
      -H 'pragma: no-cache' \
      -H 'priority: u=0, i' \
      -H 'referer: https://www.liveatc.net/' \
      -H 'sec-ch-ua: "Chromium";v="140", "Not=A?Brand";v="24", "Google Chrome";v="140"' \
      -H 'sec-ch-ua-mobile: ?0' \
      -H 'sec-ch-ua-platform: "Windows"' \
      -H 'sec-fetch-dest: document' \
      -H 'sec-fetch-mode: navigate' \
      -H 'sec-fetch-site: same-site' \
      -H 'sec-fetch-user: ?1' \
      -H 'upgrade-insecure-requests: 1' \
      -H 'user-agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/140.0.0.0 Safari/537.36' \
      --output "$filename"

    if [ $? -eq 0 ]; then
        echo "✓ Successfully downloaded $filename"
    else
        echo "✗ Failed to download $filename"
    fi
    echo ""

done < f.txt

echo "Download complete!"
