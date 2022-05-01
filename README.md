# ImageProcessing-Liam

Personal resources for image processing.

# What's inside

- [`imageGridCombine`](./src/imageGridCombine) 
      
    Convert an ordered group of images to a single "grid" combined image.
  
- [`video2gif`](./src/video2gif) 
      
    Convert a video to gif using ffmpeg.

- [`WebcamLiveProcessing`](./src/video2gif) 
      
    Perform color transformation on a live camera feed that can be used in
    any application.


# How to use

## Environment

I'm using [Poetry](https://python-poetry.org/). 
You can simply install dependency using  [pyproject.toml](pyproject.toml)

## Packages

Each project (a package) can be found in [./src](./src).
Be careful as some of these packages are using themselves between each others,
so they need to be added to your env path.

In PyCharm I simply mark the package directory as `Sources Root` (RMB > Mark Directory As).