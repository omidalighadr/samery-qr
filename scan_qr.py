"""Read QR text locally without following any embedded links."""
import argparse
import json
import sys

from PIL import Image, ImageOps, UnidentifiedImageError
import zxingcpp


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('image', help='image path, or - to read image bytes from standard input')
    parser.add_argument('--json', action='store_true', help='print a JSON array of decoded strings')
    args = parser.parse_args()
    try:
        image_input = sys.stdin.buffer if args.image == '-' else args.image
        with Image.open(image_input) as source:
            image = ImageOps.exif_transpose(source).convert('RGB')
        codes = zxingcpp.read_barcodes(image, formats=zxingcpp.BarcodeFormat.QRCode)
    except (OSError, UnidentifiedImageError, Image.DecompressionBombError) as error:
        print(f'Could not read the image: {error}', file=sys.stderr)
        return 2
    if not codes:
        print('No readable QR code found.', file=sys.stderr)
        return 1
    payloads = [code.text for code in codes]
    if args.json:
        print(json.dumps(payloads, ensure_ascii=False))
    else:
        print("\n".join(payloads))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
