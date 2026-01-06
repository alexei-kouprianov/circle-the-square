# Description

``circle-the-square`` is a free, open-source command-line tool designed for the pre-processing of microphotographs intended for stacking with ChimpStack. It auto-detects the circular field of view on a dark background, calculates the median centre and radius of the circle for a stack of images, bleaches the area outside the circle, and creates a fade on the circle border to prevent ChimpStack from being misguided by the sharp black field-of-view border. This is vitally important for microphotographs taken through one of the eyepieces of the binocular head of a dissection microscope (as the object unavoidably shifts sideways in sequential images).

## Installation (CLI)

### Linux / macOS
```bash
pipx install git+https://github.com/alexei-kouprianov/circle-the-square
```

## Usage

usage: ``circle-the-square [-h] [-f FADE] [-r REDUCE_RADIUS] images [images ...]``

positional arguments:

* ``images`` :: Input image files (globs expanded by the shell)

options:

* ``-h``, ``--help`` :: show this help message and exit

* ``-f`` FADE, ``--fade`` FADE :: Fade width ratio relative to circle radius (default: 0.06; typical: 0.03 sharp, 0.05–0.07 natural)

* ``-r`` REDUCE_RADIUS, ``--reduce-radius`` REDUCE_RADIUS :: Radius reduction in pixels applied after median radius detection (default: 100)

Example command line call:

```bash
circle-the-square -f .06 -r 110 *.JPG
```
