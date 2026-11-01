"""Draw the app icon: a jade seal with 粵 on cream paper.

    uv run --with pillow python tools/make_icon.py <out dir>

Writes into <out dir>:
  windowIcon.icns / .ico / .jpg   macOS window and app icon (rounded, with shadow)
  ios-icon-1024.png               iOS AppIcon: full-bleed 1024x1024, no transparency;
                                  iOS rounds the corners itself

Needs the macOS fonts STHeiti and the iconutil command. Copy the files you want
into assets/ (macOS) or the Xcode asset catalog (iOS).
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFilter, ImageFont

HEI = '/System/Library/Fonts/STHeiti Medium.ttc'   # face index 1 = Heiti SC Medium
PAPER = (244, 240, 230)
JADE = (31, 111, 84)
INK = (248, 245, 236)

S = 2048                      # working size, downscaled 2x for clean edges
BODY = int(S * 824 / 1024)    # macOS icon grid: 824px body on a 1024 canvas
OFF = (S - BODY) // 2
RADIUS = int(BODY * 0.225)


def centered_text(draw, text, fnt, cx, cy, fill):
    l, t, r, b = draw.textbbox((0, 0), text, font=fnt)
    draw.text((cx - (l + r) / 2, cy - (t + b) / 2), text, font=fnt, fill=fill)


def seal(size):
    """The seal artwork on a size x size paper square."""
    body = Image.new('RGBA', (size, size), PAPER + (255,))
    d = ImageDraw.Draw(body)
    m = int(size * 0.2)
    d.rounded_rectangle([m, m, size - m, size - m], int(size * 0.07), fill=JADE)
    inset = int(size * 0.035)
    d.rounded_rectangle([m + inset, m + inset, size - m - inset, size - m - inset], int(size * 0.05),
                        outline=PAPER, width=max(2, size // 165))
    centered_text(d, '粵', ImageFont.truetype(HEI, int(size * 0.364), index=1), size / 2, size / 2, INK)
    return body


def mac_icon():
    """Rounded body with a soft shadow on a transparent canvas, like system icons."""
    canvas = Image.new('RGBA', (S, S), (0, 0, 0, 0))

    shadow = Image.new('RGBA', (S, S), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle([OFF, OFF + 24, OFF + BODY, OFF + BODY + 24], RADIUS, fill=(0, 0, 0, 90))
    canvas.alpha_composite(shadow.filter(ImageFilter.GaussianBlur(36)))

    mask = Image.new('L', (BODY, BODY), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, BODY - 1, BODY - 1], RADIUS, fill=255)
    canvas.paste(seal(BODY), (OFF, OFF), mask)
    return canvas.resize((1024, 1024), Image.LANCZOS)


def write_icns(icon, path):
    with tempfile.TemporaryDirectory() as tmp:
        iconset = os.path.join(tmp, 'icon.iconset')
        os.mkdir(iconset)
        for s in (16, 32, 128, 256, 512):
            icon.resize((s, s), Image.LANCZOS).save(f'{iconset}/icon_{s}x{s}.png')
            icon.resize((s * 2, s * 2), Image.LANCZOS).save(f'{iconset}/icon_{s}x{s}@2x.png')
        subprocess.run(['iconutil', '-c', 'icns', iconset, '-o', path], check=True)


def main(out):
    os.makedirs(out, exist_ok=True)

    icon = mac_icon()
    write_icns(icon, f'{out}/windowIcon.icns')
    icon.save(f'{out}/windowIcon.ico', sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
    flat = Image.new('RGB', icon.size, (255, 255, 255))
    flat.paste(icon, mask=icon.split()[3])
    flat.resize((400, 400), Image.LANCZOS).save(f'{out}/windowIcon.jpg', quality=92)

    # iOS: the whole square is the icon, no alpha channel
    seal(S).convert('RGB').resize((1024, 1024), Image.LANCZOS).save(f'{out}/ios-icon-1024.png')
    print('written to', out)


if __name__ == '__main__':
    main(sys.argv[1] if len(sys.argv) > 1 else 'assets')
