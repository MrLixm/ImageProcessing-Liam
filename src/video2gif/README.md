# video2gif (v2gif)

Convert a video to gif using ffmpeg.

Offer a simple API to define settings. 

# Use

*These are the way I use it on Windows, instruction might change for your context*

Heads to [video_to_gif.py](video_to_gif.py).

- At the top of the file modify the `FFMPEG` variable with the path to your
ffmpeg executable
- In the `run()` top function, modify the settings according to your needs.

Heads to [video_to_gif.bat](video_to_gif.bat).

- Modify the `_python` variable with the path to your python interpreter. (recommended python > 3.6)
- Run the `.bat`

# Notes

The `settings` defined in the `run()` function are an instance of `Settings`
which is itself a subclass of a `dictionary`. This mean you could easily
export them to json or whatever format for reuse.