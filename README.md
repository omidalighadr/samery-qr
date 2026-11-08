# Samery QR

A Python command-line tool that reads QR codes from images. It prints the decoded text locally, one result at a time, without opening any links.

## Setup

With Python 3.12:

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Usage

```sh
python scan_qr.py path/to/image.png
```

PNG and JPEG work, including rotated images. Output goes to standard output; errors go to standard error. Exit codes are `0` for a decoded QR code, `1` when no readable QR is found, and `2` when the image or arguments cannot be read.

Uses Pillow for image loading and ZXing-C++ for QR decoding. The small CLI workflow was inspired by [unqr](https://github.com/xeptore/unqr).
