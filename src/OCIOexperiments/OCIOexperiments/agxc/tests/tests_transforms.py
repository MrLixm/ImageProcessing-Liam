"""

"""
from pathlib import Path

import colour

import OCIOexperiments as ocex


def test_native_inout_look_1():

    input_path = ocex.c.DATA_DIR / "webcam" / "webcam-c922-A.0001.tif"
    output_path = Path(__file__).parent / "_outputs" / "webcam-c922-A.v2.tif"

    img = colour.read_image(str(input_path), bit_depth="float32")

    outimg = ocex.agxc.transforms.transform_native_inout_look_1(img)

    colour.write_image(outimg, path=str(output_path), bit_depth="float32")
    print(f"[test_native_inout_look_1] Image written to {output_path}")
    return


if __name__ == "__main__":

    test_native_inout_look_1()
