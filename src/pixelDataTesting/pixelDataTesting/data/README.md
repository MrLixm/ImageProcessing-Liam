# data

# Conventions

>One folder = similar scene representations in different formats, encoding,
colorspaces, ...

This folder is called an `asset`

Name of this folder = `assetID`

## Nomenclature

Every file in an asset folder must be named as :

```
{assetID}.{id}.{variant}.{colorspace}.{dimensions}.{frame}.{extension}
```

Like :

```
dragonScene.0001.base.aces.half.1001.exr
```

The dot is used as a separator so do not use it for anything else than splitting
a new property.

Where each property :

- `id` is an increment starting at 1, different for each file, no matter the other
properties. MUST be 4 digit long.
- `variant` can be any but `base` MUST be present
- `colorspace` is an RGB Colorspace name from `colour` library.
> TODO actually not true yet as colour ColorSpaces name are not sanitized for
> file names. Use them as a guideline for now.

<details>
  <summary>list(colour.RGB_COLOURSPACES.keys())</summary>

```python
['ACES2065-1',
 'ACEScc',
 'ACEScct',
 'ACEScg',
 'ACESproxy',
 'ALEXA Wide Gamut',
 'Adobe RGB (1998)',
 'Adobe Wide Gamut RGB',
 'Apple RGB',
 'Best RGB',
 'Beta RGB',
 'Blackmagic Wide Gamut',
 'CIE RGB',
 'Cinema Gamut',
 'ColorMatch RGB',
 'DCDM XYZ',
 'DCI-P3',
 'DCI-P3+',
 'DJI D-Gamut',
 'DRAGONcolor',
 'DRAGONcolor2',
 'DaVinci Wide Gamut',
 'Display P3',
 'Don RGB 4',
 'ECI RGB v2',
 'ERIMM RGB',
 'Ekta Space PS 5',
 'F-Gamut',
 'FilmLight E-Gamut',
 'ITU-R BT.2020',
 'ITU-R BT.470 - 525',
 'ITU-R BT.470 - 625',
 'ITU-R BT.709',
 'Max RGB',
 'N-Gamut',
 'NTSC (1953)',
 'NTSC (1987)',
 'P3-D65',
 'Pal/Secam',
 'ProPhoto RGB',
 'Protune Native',
 'REDWideGamutRGB',
 'REDcolor',
 'REDcolor2',
 'REDcolor3',
 'REDcolor4',
 'RIMM RGB',
 'ROMM RGB',
 'Russell RGB',
 'S-Gamut',
 'S-Gamut3',
 'S-Gamut3.Cine',
 'SMPTE 240M',
 'SMPTE C',
 'Sharp RGB',
 'V-Gamut',
 'Venice S-Gamut3',
 'Venice S-Gamut3.Cine',
 'Xtreme RGB',
 'sRGB',
 'aces',
 'adobe1998',
 'prophoto']
```

</details>

- `dimensions` MUST be specified in word like `half` `full`, ... OR number as
`{width}x{height}` like `1920x1080`.
- `frame` SHOULD starts at 1001.
