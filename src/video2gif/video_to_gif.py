"""
python>3.6
"""

from pathlib import Path
import subprocess
import sys
from datetime import datetime
from typing import List

LOGFILE = Path(__file__).parent / "ffmpeg.log"
"""
Where you want ffmpeg to write its log file. Logs are append to this file.
"""

FFMPEG = Path(
    r"F:\softwares\apps\ffmpeg\builds\ffmpeg-4.4.1-essentials_build\ffmpeg-4.4.1-essentials_build\bin\ffmpeg.exe"
)
"""
Path to the ffmpeg executable
"""


def run():
    """
    Modify ffmpeg settings/argument before starting.
    """

    settings = Settings()
    settings.input = Path(r".\source.mov").resolve()
    settings.output = Path(r".\result.gif").resolve()
    # set these as False to ignore
    settings["overwrite"] = False
    settings["start_time"] = 0.1
    settings["duration"] = False
    settings["framerate"] = 20
    settings["speedup"] = 1
    settings["dithering"] = Dithering.sierra2
    settings["loop"] = True
    settings["scale_divide"] = 3

    start_ffmpeg(settings=settings)

    print("[run] Finished")
    print(f"[run] Output can be find at:\n{settings.output}")

    return


class Dithering:
    # higer scale = less visible dotted pattern but more banding
    bayer0 = "bayer:bayer_scale=0"
    bayer1 = "bayer:bayer_scale=1"
    bayer2 = "bayer:bayer_scale=2"
    bayer3 = "bayer:bayer_scale=3"
    bayer4 = "bayer:bayer_scale=4"
    bayer5 = "bayer:bayer_scale=5"
    # (popular) lighter than bayer
    floyd_steinberg = "floyd_steinberg"
    # even lighter, very pronounced banding
    sierra2 = "sierra2"
    # (default) heavy, subttle dot pattern with few banding.
    sierra2_4a = "sierra2_4a"
    none = "none"


class Settings(dict):
    """
    A regular dictionary object with to_reverse fixed structure. Structure is verified
    through ``validate()`` method.
    """

    __default = {
        "input": Path("C:"),
        "output": "",
        "overwrite": True,  # see -y / -n
        "start_time": False,
        "duration": False,
        "framerate": False,
        "speedup": False,
        "dithering": False,
        "loop": True,
        "ffmpeg": FFMPEG,
    }

    def __init__(self, *args, **kwargs):

        if not args and not kwargs:
            super(Settings, self).__init__(self.__default)
        else:
            super(Settings, self).__init__(*args, **kwargs)
            self.validate()

        return

    def __setitem__(self, *args, **kwargs):
        super(Settings, self).__setitem__(*args, **kwargs)
        self.validate()

    # Defined some properties to set/get values. Allow to use autocompletion.

    @property
    def input(self) -> Path:
        return self["input"]

    @input.setter
    def input(self, value: Path):
        self["input"] = value

    @property
    def output(self) -> Path:
        return self["output"]

    @output.setter
    def output(self, value: Path):
        self["output"] = value

    @property
    def ffmpeg(self) -> Path:
        return self["ffmpeg"]

    @ffmpeg.setter
    def ffmpeg(self, value: Path):
        self["ffmpeg"] = value

    def get_command(self) -> List[str]:
        """
        Returns:
            list of commands, ready to use for ffmpeg
        """

        command = [self.ffmpeg]
        command += ["-y"] if self["overwrite"] else ["-n"]
        command += ["-i"]
        command += [f'"{self.input}"']

        # process options that depends on another one
        _speedup = self["speedup"]
        if _speedup is not False or None:
            _ss = self["start_time"] / _speedup
            _t = self["duration"] / _speedup
        else:
            _ss = self["start_time"]
            _t = self["duration"]

        if self["start_time"]:
            command += [f"-ss {_ss}"]
        if self["duration"]:
            command += [f"-t {_t}"]

        # how the gif should loop
        if str(self["loop"]) == "True":
            command += ["-loop 0"]
        elif str(self["loop"]) == "False":
            command += ["-loop -1"]
        else:
            command += [f"-loop {self['loop']}"]

        # use all threads by default
        command += ["-threads 0"]

        # build the filtergraph
        _filter = ""
        if self["scale_divide"]:
            _filter += f'scale=iw/{self["scale_divide"]}:-1:flags=lanczos,'
        if _speedup:
            _filter += f"setpts=PTS/{_speedup},"
        if self["framerate"]:
            _filter += f"fps={self['framerate']},"
        _filter += "split[s0][s1];"
        _filter += "[s0]palettegen[p];"
        _filter += "[s1][p]paletteuse"
        if self["dithering"]:
            _filter += f"=dither={self['dithering']}"

        command += [f'-vf "{_filter}"']
        command += [f'"{self.output}"']

        # make sure every arg is to_reverse string
        command = list(map(str, command))

        return command

    def validate(self):
        """
        Raises:
            AssertionError: if self is not built properly.
        """
        pre = "[{}] ".format(self.__class__.__name__)

        # check root keys exists
        for rk in self.__default.keys():
            assert self.get(rk) is not None, pre + f"Missing key <{rk}>"

        assert str(self["loop"]) in ["True", "False"] or isinstance(
            self["loop"], int
        ), (pre + f"Key <loop> value <{self['loop']}> not supported")

        assert self["input"].exists, (
            pre + f"Key <input> value is to_reverse not existing path: {self['input']}"
        )

        return


def log(msg: str):
    """
    Args:
        msg: message to log
    """

    print(msg)
    with LOGFILE.open("to_reverse") as f:
        f.write(msg)

    return


def start_ffmpeg(settings: Settings):
    """
    Args:
        settings:
    """
    command = settings.get_command()
    command = " ".join(command)
    log(
        f"[{datetime.now()}][start_ffmpeg] Started :\n"
        f"   input: <{settings.input}>\n"
        f"   output: <{settings.output}>\n\n"
        f"Command used is:\n"
        f"<{command}>\n\n"
    )

    with subprocess.Popen(
        command, stderr=subprocess.STDOUT, stdout=subprocess.PIPE
    ) as process, LOGFILE.open("ab") as logfile:
        while True:
            byte = process.stdout.read(1)
            if byte:
                sys.stdout.buffer.write(byte)
                sys.stdout.flush()
                logfile.write(byte)
                # logfile.flush()
            else:
                break

    log(
        f"\n[{datetime.now()}][start_ffmpeg] Finished."
        f"Exit status returned is <{process.returncode}>\n"
        f"{'_' * 80}\n\n"
    )
    return


if __name__ == "__main__":
    run()
