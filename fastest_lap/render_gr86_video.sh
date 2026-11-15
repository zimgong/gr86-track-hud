#!/bin/zsh
set -euo pipefail
cd "$(dirname "$0")/.."
PYTHON="${PYTHON:-python3}"
"$PYTHON" fastest_lap/work/render_gr86.py
ffmpeg -hide_banner -filter_complex_threads 2 -threads 4 -hwaccel videotoolbox -noautorotate -display_rotation 0 -ss 748.876 -i DJI_20261024120038_0061_D.MP4 -i fastest_lap/work/gr86_overlay.mov \
  -filter_complex '[0:v:0]scale=1920:1080:flags=lanczos,hflip,vflip,setsar=1[v];[v][1:v:0]overlay=0:0:format=auto,format=yuv420p[out]' \
  -map '[out]' -map 0:a:0 -t 95.874 -c:v h264_videotoolbox -b:v 20M -profile:v high \
  -r 60000/1001 -c:a aac -b:a 256k -movflags +faststart \
  -metadata title='GR86 Track Mode | Thunderhill West 1:29.874 | Zim Gong' \
  -y fastest_lap/Thunderhill_West_GR86_Track_Mode_1m29.874_refined_1080p60.mp4
