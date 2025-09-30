Remove audio

ffmpeg.exe -i "d:\2025-08-16 15-00-32.mkv" -c copy -an genspeed2.mkv

Speed up 

ffmpeg.exe -i genspeed2.mkv -vf "setpts=0.01639*PTS" genspeed.mkv

Add the padding to be youtube friendly

ffmpeg -i genspeed.mkv -vf "scale=1080:-1,pad=1080:1920:(ow-iw)/2:(oh-ih)/2" -c:a copy genpad.mkv

Add music to youtube video

ffmpeg -i genpad.mkv -i "Downloads\Way back when - Patrick Patrikios.mp3" -c copy -map 0:v:0 -map 1:a:0 -shortest gencomplete.mkv

Combined ? might be wierd, let's try next time

ffmpeg -i "d:\2025-08-16 15-00-32.mkv" -i "Downloads\Way back when - Patrick Patrikios.mp3" -an -filter_complex "[0:v]setpts=0.01639*PTS,scale=1080:-1,pad=1080:1920:(ow-iw)/2:(oh-ih)/2[v];[1:a]apad[a]" -map "[v]" -map "[a]" -shortest -c:v libx264 -c:a aac -b:a 192k gencomplete.mkv