# WebcamLiveProcessing

Perform color transformation on a live camera feed that can be used in
any application.

> This is a test project. 
> I do not guarantee that you will make it work on your machine.

# Dependencies

See the dependency at the root of this repo or check [pyproject.toml](pyproject.toml)
next to this file.

- pyvirtualcam is used for producing a virtual camera feed
- opencv is used to create the original camera stream from a webcam
- ❕ OCIOexperiments project from this repo is also used, make sure it is added to your path
  (`src/OCIOexperiments`)

# Use

Add [WebcamLiveProcessing](WebcamLiveProcessing) to your path so you can :

```python
import WebcamLiveProcessing as wlp
```

You can then configure logging for the root logger named `wlp`. (see `WebcamLiveProcessing.c.ABR`)

Creating a camera is in 2 steps :
- Create the desired camera configuration
- Use it to create a Webcam instance

```python
config = wlp.sources.WebcamConfiguration(
    camera=0,
    name="c922pro",
    target_width=1280,
    target_height=720,
    target_fps=30,
)
cam_c922 = wlp.sources.Webcam(configuration=config)
```

`cam_c922` is a `cv2.VideoCapture` subclass instance and can then be used with
pyvirtualcam.

## Demo

### [tests/tests_agxc.py](tests/tests_agxc.py)

Apply AgX "image formation pipeline" from Troy.S on a live camera feed.

> AgX : https://github.com/sobotka/AgX/blob/main/config.ocio

Made use of the OCIO python library and the `OCIOexperiments` project to apply
it.

Unfortunately it currently runs at a poor framerate where a 1280x720@30fps 
source stream runs at ~6.8fps which is not usable.

I tried to make a python native implementation of AgX without using OCIO but
it ended up even slower (~3fps).