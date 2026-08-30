# -*- coding: utf-8 -*-
"""Key the charter icon to transparency, decontaminated, in vanilla's shape.

Target, measured across all 40 files in
main_menu/gfx/interface/icons/disasters: 128x128, 8 mips, DXT5, 22000 bytes.

The first attempt left a visible pink rim, plainly worse than any vanilla icon
next to it. Three things fix it:

1. **Key on min(R,B) - G**, not the green channel: the seal is deep red and the
   smoke is orange, and both have a low blue, so both score low and survive. A
   green test would have eaten them.

2. **Decontaminate the partial pixels.** The smoke has genuinely translucent
   edges, so in the source those pixels ARE a blend of smoke and magenta:
   c = a*fg + (1-a)*magenta. Keying them semi-transparent keeps the magenta in
   RGB and the rim goes pink. Solving that back out - fg = (c - (1-a)*magenta)/a
   - is what removes it. This is the step the first version skipped.

3. **Premultiplied downscale**, so the mip chain cannot re-introduce a fringe.

Also crops to the artwork's own bounding box first: vanilla's subjects fill
their frame, and the raw render leaves a wide magenta margin that would
otherwise shrink ours next to them.
"""
import os
import struct
import sys

from PIL import Image, ImageChops

SRC = r"C:\Users\svnzr\Downloads\bohemya disaster icon yeni.png"
OUT = (r"C:\Users\svnzr\OneDrive\Belgeler\Paradox Interactive"
       r"\Europa Universalis V\mod\The Prussian Destiny"
       r"\main_menu\gfx\interface\icons\disasters"
       r"\PD_bohemian_estates_crisis.dds")
PREVIEW = r"C:\Users\svnzr\Downloads\bohemya_disaster_ICON_PREVIEW.png"

LO, HI = 5, 110           # score <= LO fully opaque, >= HI fully out
MARGIN = 0.03             # of the cropped side, kept clear at the edges

im = Image.open(SRC).convert("RGB")
w, h = im.size
px = im.load()

alpha = Image.new("L", (w, h), 255)
ap = alpha.load()
keyed = 0
for y in range(h):
    for x in range(w):
        r, g, b = px[x, y]
        s = min(r, b) - g
        if s >= HI:
            ap[x, y] = 0
            keyed += 1
        elif s > LO:
            ap[x, y] = int(255 * (HI - s) / float(HI - LO))
if keyed == 0:
    print("FAIL - no magenta found")
    sys.exit(1)
print("keyed %.1f%% fully transparent" % (100.0 * keyed / (w * h)))

# --- decontaminate: undo the blend against magenta on every partial pixel
clean = Image.new("RGB", (w, h))
cp = clean.load()
fixed = 0
for y in range(h):
    for x in range(w):
        a = ap[x, y]
        if a == 255:
            cp[x, y] = px[x, y]
        elif a == 0:
            cp[x, y] = (0, 0, 0)
        else:
            f = a / 255.0
            r, g, b = px[x, y]
            cp[x, y] = (max(0, min(255, int((r - (1 - f) * 255) / f))),
                        max(0, min(255, int(g / f))),
                        max(0, min(255, int((b - (1 - f) * 255) / f))))
            fixed += 1
print("decontaminated %d edge pixels" % fixed)

# A partial pixel whose DECONTAMINATED colour is still magenta-ish was never
# smoke - it was almost pure key, and the division just amplified the noise.
# Those are the speckles that survived the first pass; drop them outright.
dropped = 0
for y in range(h):
    for x in range(w):
        a = ap[x, y]
        if 0 < a < 255:
            r, g, b = cp[x, y]
            if min(r, b) - g > 60:
                ap[x, y] = 0
                cp[x, y] = (0, 0, 0)
                dropped += 1
print("dropped %d residual key pixels" % dropped)

# DESPILL. The pink rim survived two earlier passes because it is not in the
# semi-transparent pixels at all - the generated art fades its smoke into the
# key over many FULLY OPAQUE pixels, which read as "not magenta enough" to key
# but are visibly pink. So pull the magenta cast out of every pixel that still
# has one: where min(R,B) exceeds G, that excess is key bleed, not paint.
spilled = 0
for y in range(h):
    for x in range(w):
        if ap[x, y] == 0:
            continue
        r, g, b = cp[x, y]
        excess = min(r, b) - g
        if excess > 0:
            cp[x, y] = (max(0, r - excess), g, max(0, b - excess))
            spilled += 1
print("despilled %d pixels" % spilled)

# --- crop to the artwork, so it fills the frame like vanilla's do
bbox = alpha.point(lambda v: 255 if v > 8 else 0).getbbox()
cx0, cy0, cx1, cy1 = bbox
side = max(cx1 - cx0, cy1 - cy0)
side = int(side * (1 + 2 * MARGIN))
mx, my = (cx0 + cx1) // 2, (cy0 + cy1) // 2
x0, y0 = mx - side // 2, my - side // 2
box = (max(0, x0), max(0, y0), min(w, x0 + side), min(h, y0 + side))
clean, alpha = clean.crop(box), alpha.crop(box)
print("cropped to artwork bbox %s -> %dx%d" % (bbox, clean.width, clean.height))

# --- premultiplied downscale
r, g, b = clean.split()
pm = Image.merge("RGB", (ImageChops.multiply(r, alpha),
                         ImageChops.multiply(g, alpha),
                         ImageChops.multiply(b, alpha)))
pm_s = pm.resize((128, 128), Image.LANCZOS)
a_s = alpha.resize((128, 128), Image.LANCZOS)

out = Image.new("RGBA", (128, 128))
op, sp, apx = out.load(), pm_s.load(), a_s.load()
for y in range(128):
    for x in range(128):
        a = apx[x, y]
        # Un-premultiplying divides by alpha, so at a=1..3 it multiplies the
        # rounding error by ~100 and clamps out to junk - measured: pixels that
        # came out (255,0,255) at alpha 1. Every one of the 102 pink pixels in
        # the compressed file traced back to this, all of them in 4x4 blocks
        # that also held a transparent pixel, so DXT spread the junk across the
        # block. Below the visibility floor, drop the pixel and let the bleed
        # below fill it with a real neighbouring colour.
        if a < 12:
            op[x, y] = (0, 0, 0, 0)
        else:
            pr, pg, pb = sp[x, y]
            op[x, y] = (min(255, pr * 255 // a), min(255, pg * 255 // a),
                        min(255, pb * 255 // a), a)
def bleed(img, passes=6):
    """Push opaque colour outwards into the transparent pixels.

    DXT block compression knows nothing about alpha: it compresses the RGB of
    fully transparent pixels along with everything else, in 4x4 blocks. Leaving
    those pixels black gives the encoder wild colour endpoints on every block
    that straddles an edge - measured here as 129 pink pixels in the DDS from a
    PNG that had zero. Filling them with the nearest real colour first removes
    the artefact at the source.
    """
    w, h = img.size
    p = img.load()
    for _ in range(passes):
        todo = []
        for y in range(h):
            for x in range(w):
                if p[x, y][3] != 0:
                    continue
                acc, n = [0, 0, 0], 0
                for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
                    nx, ny = x+dx, y+dy
                    if 0 <= nx < w and 0 <= ny < h:
                        r2, g2, b2, a2 = p[nx, ny]
                        if a2 != 0 or (r2 or g2 or b2):
                            acc[0]+=r2; acc[1]+=g2; acc[2]+=b2; n+=1
                if n:
                    todo.append((x, y, (acc[0]//n, acc[1]//n, acc[2]//n, 0)))
        if not todo:
            break
        for x, y, v in todo:
            p[x, y] = v
    return img


out = bleed(out)
out.save(PREVIEW)
print("preview:", PREVIEW)

chain, cur = [], out
while True:
    chain.append(cur)
    if cur.width == 1:
        break
    cur = cur.resize((cur.width // 2, cur.height // 2), Image.LANCZOS)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
blobs = []
for m in chain:
    tmp = OUT + ".lvl"
    m.save(tmp, format="DDS", pixel_format="DXT5")
    blobs.append(open(tmp, "rb").read()[128:])
    os.remove(tmp)
out.save(OUT + ".head", format="DDS", pixel_format="DXT5")
head = bytearray(open(OUT + ".head", "rb").read()[:128])
os.remove(OUT + ".head")
struct.pack_into("<I", head, 8, struct.unpack_from("<I", head, 8)[0] | 0x20000)
struct.pack_into("<I", head, 28, len(chain))
struct.pack_into("<I", head, 108,
                 struct.unpack_from("<I", head, 108)[0] | 0x8 | 0x400000)
open(OUT, "wb").write(bytes(head) + b"".join(blobs))

d = open(OUT, "rb").read()
_, _, hh, ww, _, _, mm = struct.unpack_from("<7I", d, 4)
print("icon: %dx%d mips=%d %s %d bytes"
      % (ww, hh, mm, d[84:88].decode("ascii", "replace"), len(d)))
if (ww, hh, mm, d[84:88], len(d)) != (128, 128, 8, b"DXT5", 22000):
    print("FAIL - does not match vanilla's disaster icon shape")
    sys.exit(1)
print("matches vanilla's disaster icon shape exactly (40 of 40)")
