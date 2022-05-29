# pixelDataTesting

Unifying image resources used for testing.
The package is auto-generated from the images found.

# Use

```python
from pathlib import Path

import pixelDataTesting as pxdt

# just get the first image in asset
test_image: Path = pxdt.colorCheckerXrite2014.first.path

# get a specific image
test_image: Path = pxdt.colorCheckerXrite2014.get(colorspace="ACES").path
```

# Add a new image

> Follow conventions specified in [pixelDataTesting/data/README.md](pixelDataTesting/data/README.md) !

In the [pixelDataTesting/data](pixelDataTesting/data) directory, create a new
directory. Name will be used to generate a pthon variable so make sure it
doesn't use any character outside this regex: `[a-zA-Z\d_-]`

You can then add your first image into the newly created asset directory. The first 
image MUST have the `0001` id and the `base` variant.

You will then need to run [pixelDataTesting/autoGenerate.py](pixelDataTesting/autoGenerate.py)
to update the package. To do so you can simpy add [pixelDataTesting](pixelDataTesting)
to your Python path then just run the file.

# Update a current asset folder with a new image

In the existing directory, add your new image following the conventions.

You don't need to run an update.

# Update a current asset folder with a new name

- Rename the asset directory
- Rename all the file `assetID` property inside
- Run `autoGenerate.py`

> ⚠ This is a destructive operation. All the places where you used the asset
>will not work and will need to be updated to.
