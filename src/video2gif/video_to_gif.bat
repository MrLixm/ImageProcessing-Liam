@echo off

set "_python=C:\Users\lcoll\AppData\Local\Programs\Python\Python39\python.exe"

start "" /B %_python% "%~dp0/video_to_gif.py"

echo Script started. Once finished press any key to exit.
echo:
echo:
pause > nul