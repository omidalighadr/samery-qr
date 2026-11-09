# Samery QR

A Python command-line tool that reads QR codes from images. It prints the decoded text locally, one result per line in text mode, without opening any links.

## Setup

Use Python 3.12 or newer. CI tests Python 3.12 and 3.13.

```sh
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install .
```

## Usage

```sh
samery-qr path/to/image.png
```

Run `python scan_qr.py` from the checkout if you prefer invoking the source directly.

PNG and JPEG work, including rotated images. Output goes to standard output; errors go to standard error. Exit codes are `0` for a decoded QR code, `1` when no readable QR is found, and `2` when the image or arguments cannot be read.

### JSON output

Use `--json` to get an array of decoded strings, which preserves line breaks and separates multiple codes:

```sh
samery-qr --json path/to/image.png
```

```json
["https://example.com/qr"]
```

Errors still use standard error and the same exit codes.

### Save the decoded text

Quote paths that contain spaces. Use shell redirection to save the decoded text to a file:

```sh
samery-qr "photos/QR code.jpg" > decoded.txt
```

If no code is found, try the original image or crop around the QR code while keeping its white border.

Uses Pillow for image loading and ZXing-C++ for QR decoding. The small CLI workflow was inspired by [unqr](https://github.com/xeptore/unqr).


## Development checks

```sh
python -m unittest discover -s tests -v
```
