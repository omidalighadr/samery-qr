"""Read QR text locally without following any embedded links."""
import argparse
import sys

from PIL import Image, ImageOps, UnidentifiedImageError
import zxingcpp


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', help='path to a PNG, JPEG or other supported image')
    args = parser.parse_args()
    try:
        with Image.open(args.image) as source:
            image = ImageOps.exif_transpose(source).convert('RGB')
        codes = zxingcpp.read_barcodes(image, formats=zxingcpp.BarcodeFormat.QRCode)
    except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as error:
        print(f'Could not read the image: {error}', file=sys.stderr)
        return 2
    if not codes:
        print('No readable QR code found.', file=sys.stderr)
        return 1
    for code in codes:
        print(code.text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
