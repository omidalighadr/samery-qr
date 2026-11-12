import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from PIL import Image
import zxingcpp


SCRIPT = Path(__file__).resolve().parents[1] / 'scan_qr.py'
PAYLOAD = 'سلام سامری | https://example.com/qr'


class ScanQRTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.directory = Path(directory.name)
        image = self.qr_image(PAYLOAD)
        self.png = self.directory / 'QR code.png'
        self.jpeg = self.directory / 'rotated.jpg'
        self.blank = self.directory / 'blank.png'
        image.save(self.png)
        image.rotate(90, expand=True).save(self.jpeg, quality=95)
        Image.new('L', (300, 300), 255).save(self.blank)

    @staticmethod
    def qr_image(payload):
        barcode = zxingcpp.create_barcode(payload, zxingcpp.BarcodeFormat.QRCode)
        pixels = memoryview(zxingcpp.write_barcode_to_image(barcode, scale=8))
        height, width = pixels.shape
        return Image.frombytes('L', (width, height), pixels.tobytes())

    def run_cli(self, *args):
        return subprocess.run(
            [sys.executable, '-B', str(SCRIPT), *map(str, args)],
            capture_output=True, encoding='utf-8', timeout=15,
        )

    def test_png_text_output(self):
        result = self.run_cli(self.png)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, PAYLOAD + '\n')

    def test_rotated_jpeg_json_output(self):
        result = self.run_cli('--json', self.jpeg)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), [PAYLOAD])

    def test_image_from_pipe(self):
        result = subprocess.run(
            [sys.executable, '-B', str(SCRIPT), '--json', '-'],
            input=self.png.read_bytes(), capture_output=True, timeout=15,
        )
        self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8'))
        self.assertEqual(json.loads(result.stdout), [PAYLOAD])

    def test_json_preserves_multiple_codes_and_embedded_line_breaks(self):
        payloads = ('first line\nsecond line', PAYLOAD)
        left, right = (self.qr_image(payload) for payload in payloads)
        gap = 64
        image = Image.new('L', (left.width + gap + right.width, max(left.height, right.height)), 255)
        image.paste(left, (0, 0))
        image.paste(right, (left.width + gap, 0))
        path = self.directory / 'multiple codes.png'
        image.save(path)

        result = self.run_cli('--json', path)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, '')
        self.assertCountEqual(json.loads(result.stdout), payloads)

    def test_invalid_image_from_pipe_uses_stderr(self):
        result = subprocess.run(
            [sys.executable, '-B', str(SCRIPT), '--json', '-'],
            input=b'not an image', capture_output=True, timeout=15,
        )
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, b'')
        self.assertIn(b'Could not read the image', result.stderr)

    def test_image_without_qr(self):
        result = self.run_cli('--json', self.blank)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, '')
        self.assertIn('No readable QR code', result.stderr)

    def test_missing_file(self):
        result = self.run_cli(self.directory / 'missing.png')
        self.assertEqual(result.returncode, 2)
        self.assertEqual(result.stdout, '')
        self.assertIn('Could not read the image', result.stderr)


if __name__ == '__main__':
    unittest.main()
