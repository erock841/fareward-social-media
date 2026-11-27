# Fareward Christmas Meta ad creative, v4 (Nov 27, 2026).
# Erik: drop the price-increase ad; lock typography; lead with savings.
# No red/green. Cream/white on a dark overlay. fareward.com in #2F5D9E.
# Reels 6.5s (1–2) and 6.8s (VO bed). Chill Wave by Kevin MacLeod.
import os, sys, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

_src = open("/workspace/fareward-holiday/make.py").read().split("SETS={")[0]
exec(_src)  # font(), MUS (Chill Wave by Kevin MacLeod)
assert "Chill_Wave" in MUS

ROOT = "/workspace/christmas-ad"
PH = f"{ROOT}/photos"
OUT = f"{ROOT}/out"
os.makedirs(OUT, exist_ok=True)

# Brand blue from fareward-pages landing-v21.css / ws-pages.css `--acc`
BLUE  = (47, 93, 158)     # #2F5D9E  fareward.com wordmark only
CREAM = (247, 241, 228)   # #F7F1E4  headlines and body
WHITE = (255, 255, 255)   # last headline line (savings punch)
INK   = (10, 22, 44)      # #0A162C  overlay + chip text

# --- Locked type system. Same sizes on every frame (feed, story, and reels).
# 1080-wide canvas, so type does not change between feed and story.
# Headlines are written to fit; we never shrink a font to make a line fit.
X = 72
MAX_W = 1080 - 2 * X
HEAD = 96
HEAD_W = 700
HEAD_GAP = 108
HEAD_SLOTS = 4          # reserved lines; unused slots stay empty, later rows don't move
SUPPORT = 44
SUPPORT_W = 500
CHIP = 36
CHIP_W = 700
CHIP_LINE = 48
CHIP_PAD_Y = 18
CHIP_PAD_X = 28
FEE = 26
FEE_W = 500
BRAND = 38
EMOJI_SZ = 80
# Vertical grids (story starts lower for IG safe area; sizes stay the same)
FEED_Y = dict(emoji=88, head=196, support=196 + HEAD_GAP * HEAD_SLOTS + 20, chip=196 + HEAD_GAP * HEAD_SLOTS + 20 + 70, fee_from_bottom=112)
STORY_Y = dict(emoji=268, head=376, support=376 + HEAD_GAP * HEAD_SLOTS + 28, chip=376 + HEAD_GAP * HEAD_SLOTS + 28 + 78, fee_from_bottom=400)

_EMO_FONT = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)

def cover(path, W, H, fx=0.5, fy=0.5, scale=1.0):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    s = max(W / w, H / h) * scale
    im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    x = int((im.width - W) * fx)
    y = int((im.height - H) * fy)
    return im.crop((x, y, x + W, y + H))

def shade(im, top=0.72, top_a=248, bot=0.30, bot_a=205, blur=8):
    W, H = im.size
    if blur:
        m = Image.new("L", (W, H), 0)
        md = ImageDraw.Draw(m)
        bh = int(H * top * 0.95)
        for y in range(bh):
            md.line([(0, y), (W, y)], fill=int(255 * min(1, (1 - y / bh) * 1.6)))
        im = Image.composite(im.filter(ImageFilter.GaussianBlur(blur)), im, m)
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = ImageDraw.Draw(ov)
    tH = int(H * top)
    for y in range(tH):
        a = int(top_a * (1 - y / tH) ** 1.05)
        px.line([(0, y), (W, y)], fill=(*INK, a))
    bH = int(H * bot)
    for y in range(bH):
        a = int(bot_a * (y / bH) ** 1.4)
        px.line([(0, H - bH + y), (W, H - bH + y)], fill=(*INK, a))
    return Image.alpha_composite(im.convert("RGBA"), ov)

def T(d, xy, t, f, c):
    x, y = xy
    d.text((x + 2, y + 3), t, font=f, fill=(0, 0, 0, 130))
    d.text((x, y), t, font=f, fill=c)

def measure(t, size, weight):
    dummy = ImageDraw.Draw(Image.new("RGB", (8, 8)))
    return dummy.textlength(t, font=font(size, weight))

def require_fit(label, t, size, weight, maxw=MAX_W):
    w = measure(t, size, weight)
    if w > maxw:
        raise SystemExit(f"TYPE LOCK BROKEN: {label!r} {t!r} is {w:.1f}px at {size}pt, max {maxw}")
    return w

def place_emoji(ov, xy, ch, sz=EMOJI_SZ):
    canvas = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(canvas).text((0, 0), ch, font=_EMO_FONT, embedded_color=True)
    bbox = canvas.getbbox()
    if not bbox:
        raise RuntimeError(f"emoji {ch!r} did not render")
    t = canvas.crop(bbox).resize((sz, sz), Image.LANCZOS).convert("RGBA")
    ov.alpha_composite(t, dest=(int(xy[0]), int(xy[1])))

def brand(d, W, yb):
    u = "fareward.com"
    f = font(BRAND, 600)
    uw = d.textlength(u, font=f)
    pad_x, pad_y = 22, 10
    x1 = W - X - uw - pad_x
    y1 = yb - pad_y + 4
    x2 = W - X + pad_x
    y2 = yb + 48
    d.rounded_rectangle([x1, y1, x2, y2], radius=18, fill=CREAM)
    d.text((W - X - uw, yb + 6), u, font=f, fill=BLUE)

FEE_LINE = "Free to watch. Fareward keeps 20% of the savings."
SUPPORT_LINE = "Many airlines give airline credits."
DISCLAIMER = "One real save, not a typical result"

# Messaging leads with savings. Real 41% numbers always carry the disclaimer.
# Headlines are 3–4 lines of similar length, written to fit HEAD without shrinking.
ADS = {
    "a-booked-board": dict(
        photo="px_1716825.jpg", fx=0.62, fy=0.5,
        emo="🎄",
        head=["Booked your", "Christmas flight?", "If the fare drops,", "get it back."],
        chip="One real trip: 41% back",
    ),
    "b-gifts-window": dict(
        photo="px_127441.jpg", fx=0.5, fy=0.45,
        emo="🎁",
        head=["Need gift money", "this Christmas?", "Your flight could", "pay you back."],
        chip="One real trip: 41% back",
    ),
    "c-savings-wing": dict(
        photo="px_20952602.jpg", fx=0.5, fy=0.6,
        emo="✈️",
        head=["Your fare dropped?", "Get it back.", "A real trip got", "41% back."],
        chip="One real trip: 41% back",
    ),
    "d-5days-window": dict(
        photo="px_3863778.jpg", fx=0.5, fy=0.5,
        emo="❄️",
        head=["Fares can still drop", "5 days before", "you fly.", "Get it back."],
        chip="One real trip: 41% back",
    ),
}

# Lock check at import time so a too-long line fails before any render.
require_fit("support", SUPPORT_LINE, SUPPORT, SUPPORT_W)
require_fit("fee", FEE_LINE, FEE, FEE_W, maxw=MAX_W - 300)
require_fit("disclaimer", DISCLAIMER, CHIP, CHIP_W)
for name, spec in ADS.items():
    assert 1 <= len(spec["head"]) <= HEAD_SLOTS, name
    for i, line in enumerate(spec["head"]):
        require_fit(f"{name} head[{i}]", line, HEAD, HEAD_W)
    require_fit(f"{name} chip", spec["chip"], CHIP, CHIP_W)
print("type lock ok")

def layout(spec, W, H, story=False, stage=99):
    """stage: 1=emoji+headline, 2=+support, 3=+chip, 4=+fee. Brand always on."""
    grid = STORY_Y if story else FEED_Y
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    place_emoji(ov, (X, grid["emoji"]), spec["emo"], EMOJI_SZ)
    hf = font(HEAD, HEAD_W)
    for i, line in enumerate(spec["head"]):
        # Last line is the savings punch, same size, white.
        color = WHITE if i == len(spec["head"]) - 1 else CREAM
        T(d, (X, grid["head"] + i * HEAD_GAP), line, hf, color)
    if stage >= 2:
        sf = font(SUPPORT, SUPPORT_W)
        sw = d.textlength(SUPPORT_LINE, font=sf)
        sy = grid["support"]
        d.rounded_rectangle([X - 16, sy - 12, X + sw + 16, sy + 56], radius=18, fill=(*INK, 180))
        T(d, (X, sy), SUPPORT_LINE, sf, CREAM)
    if stage >= 3:
        lines = [spec["chip"], DISCLAIMER]
        f = font(CHIP, CHIP_W)
        widths = [d.textlength(t, font=f) for t in lines]
        tw = max(widths)
        h = CHIP_PAD_Y * 2 + CHIP_LINE * len(lines)
        x0, y0 = X, grid["chip"]
        d.rounded_rectangle([x0, y0, x0 + tw + CHIP_PAD_X * 2, y0 + h], radius=h // 2, fill=CREAM)
        for i, t in enumerate(lines):
            d.text((x0 + CHIP_PAD_X, y0 + CHIP_PAD_Y + i * CHIP_LINE - 2), t, font=f, fill=INK)
    yb = H - grid["fee_from_bottom"]
    if stage >= 4:
        ff = font(FEE, FEE_W)
        fw = d.textlength(FEE_LINE, font=ff)
        d.rounded_rectangle([X - 16, yb - 8, X + fw + 16, yb + 44], radius=16, fill=(*INK, 180))
        T(d, (X, yb + 4), FEE_LINE, ff, CREAM)
    brand(d, W, yb)
    return ov

def static(name, spec):
    for tag, (W, H, story) in {
        "feed-1080x1350": (1080, 1350, False),
        "story-1080x1920": (1080, 1920, True),
    }.items():
        bg = shade(
            cover(f"{PH}/{spec['photo']}", W, H, spec["fx"], spec["fy"]),
            top=0.82 if not story else 0.72,
            top_a=248,
        )
        im = Image.alpha_composite(bg, layout(spec, W, H, story)).convert("RGB")
        im.save(f"{OUT}/{name}-{tag}.png")

def reel(spec, beats, fname, music_gain=1.0, zoom=(1.0, 1.10)):
    W, H = 1080, 1920
    FPS = 30
    total = beats[-1][1]
    assert 6.0 <= total <= 7.0, f"{fname} duration {total}s is outside 6–7s"
    big = cover(f"{PH}/{spec['photo']}", int(W * zoom[1]) + 2, int(H * zoom[1]) + 2, spec["fx"], spec["fy"])
    layers = [
        (s, e, layout(spec, W, H, True, stage))
        for stage, e, s in [
            (b[0], b[1], (beats[i - 1][1] if i else 0)) for i, b in enumerate(beats)
        ]
    ]
    p = subprocess.Popen(
        [
            "ffmpeg", "-y",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-i", MUS,
            "-filter_complex",
            f"[1:a]atrim=start=4,asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-1.5,volume={music_gain},"
            f"afade=t=in:st=0:d=0.2,afade=t=out:st={total - 1.0:.2f}:d=1.0[a]",
            "-map", "0:v", "-map", "[a]",
            "-t", f"{total:.3f}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "fast",
            "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart",
            f"{OUT}/{fname}",
        ],
        stdin=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    n = int(round(total * FPS))
    keep = []
    for k in range(n):
        t = k / FPS
        z = zoom[0] + (zoom[1] - zoom[0]) * (t / total)
        cw, ch = W * z, H * z
        cx, cy = big.width / 2, big.height / 2
        fr = big.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.BICUBIC)
        fr = shade(fr, top=0.72, top_a=248)
        i = [j for j, (s, e, L) in enumerate(layers) if s <= t < e]
        i = i[0] if i else len(layers) - 1
        s = layers[i][0]
        if i > 0 and t - s < 0.25:
            a = (t - s) / 0.25
            fr = Image.alpha_composite(fr, Image.blend(layers[i - 1][2], layers[i][2], a))
        else:
            fr = Image.alpha_composite(fr, layers[i][2])
        fr = fr.convert("RGB")
        p.stdin.write(fr.tobytes())
        if k in (0, int(n * 0.35), int(n * 0.65), n - 1):
            keep.append(fr)
    p.stdin.close()
    p.wait()
    assert p.returncode == 0, f"ffmpeg failed on {fname}"
    c = Image.new("RGB", (360 * len(keep), 640))
    for i, fimg in enumerate(keep):
        c.paste(fimg.resize((360, 640)), (i * 360, 0))
    c.save(f"{OUT}/{fname[:-4]}-frames.png")
    keep[0].save(f"{OUT}/{fname[:-4]}-cover.png")
    print(fname, total)

def contact_sheet():
    feeds = [
        "a-booked-board-feed-1080x1350.png",
        "b-gifts-window-feed-1080x1350.png",
        "c-savings-wing-feed-1080x1350.png",
        "d-5days-window-feed-1080x1350.png",
    ]
    stories = [
        "a-booked-board-story-1080x1920.png",
        "b-gifts-window-story-1080x1920.png",
        "c-savings-wing-story-1080x1920.png",
        "d-5days-window-story-1080x1920.png",
    ]
    reels = [
        "reel-1-gifts-6.5s-frames.png",
        "reel-2-savings-6.5s-frames.png",
        "reel-3-gifts-voiceover-bed-6.8s-frames.png",
    ]
    # Voiced reel (name includes its measured duration)
    reels += sorted(f for f in os.listdir(OUT) if f.startswith("reel-vo-gifts-") and f.endswith("-frames.png"))
    reels = [f for f in reels if os.path.exists(f"{OUT}/{f}")]
    col, gap, label_h = 400, 16, 44
    n = 4
    width = n * col + (n + 1) * gap
    feed_h = int(col * 1350 / 1080)
    story_h = int(col * 1920 / 1080)
    reel_h = int(col * 1920 / 1080)
    rows = 2 + len(reels)
    height = label_h * rows + feed_h + story_h + reel_h * len(reels) + gap * (rows + 1)
    paper, ink = (239, 233, 220), (22, 20, 18)
    c = Image.new("RGB", (width, height), paper)
    d = ImageDraw.Draw(c)
    labelf = font(26, 600)

    def row_label(y, text):
        d.text((gap, y + 8), text, font=labelf, fill=ink)
        return y + label_h

    y = gap
    y = row_label(y, "Feed 1080×1350  ·  A booked   B gifts   C savings 41%   D 5 days")
    for i, f in enumerate(feeds):
        c.paste(Image.open(f"{OUT}/{f}").resize((col, feed_h), Image.LANCZOS), (gap + i * (col + gap), y))
    y += feed_h + gap
    y = row_label(y, "Stories 1080×1920  ·  same four ads, same type sizes")
    for i, f in enumerate(stories):
        c.paste(Image.open(f"{OUT}/{f}").resize((col, story_h), Image.LANCZOS), (gap + i * (col + gap), y))
    y += story_h + gap
    captions = {
        "reel-1-gifts-6.5s-frames.png": "Reel 1 — gifts  ·  6.5s  ·  hook / support / chip / fee",
        "reel-2-savings-6.5s-frames.png": "Reel 2 — savings 41%  ·  6.5s  ·  hook / support / chip / fee",
        "reel-3-gifts-voiceover-bed-6.8s-frames.png": "Reel 3 — gifts voiceover bed  ·  6.8s  ·  music ducked",
        "reel-vo-gifts-": "Reel VO — gifts, spoken captions, Jingle Bells under AI voice",
    }
    for f in reels:
        label = captions.get(f, f)
        if f.startswith("reel-vo-gifts-"):
            label = "Reel VO — gifts + spoken captions + Jingle Bells  ·  " + f.replace("-frames.png","").replace("reel-vo-gifts-","")
        y = row_label(y, label)
        strip = Image.open(f"{OUT}/{f}")
        target_w = n * col + (n - 1) * gap
        c.paste(strip.resize((target_w, reel_h), Image.LANCZOS), (gap, y))
        y += reel_h + gap
    c.save(f"{OUT}/contact-sheet.png")
    print("contact-sheet.png", c.size)

def _clear_retired():
    for f in os.listdir(OUT):
        if "doubled" in f or "9.8s" in f or "voiceover-bed-10" in f or f.startswith("c-doubled"):
            os.remove(f"{OUT}/{f}")
            print("removed", f)

if __name__ == "__main__":
    which = sys.argv[1:] or ["static", "reels", "sheet"]
    _clear_retired()
    if "static" in which:
        for n, s in ADS.items():
            static(n, s)
            print("static", n)
    if "reels" in which:
        # Hook (headline) on frame 0. Same beats on reels 1 and 2.
        beats = [(1, 1.8), (2, 3.6), (3, 5.1), (4, 6.5)]
        reel(ADS["b-gifts-window"], beats, "reel-1-gifts-6.5s.mp4")
        reel(ADS["c-savings-wing"], beats, "reel-2-savings-6.5s.mp4")
        reel(ADS["b-gifts-window"], [(1, 2.4), (2, 5.2), (3, 6.0), (4, 6.8)],
             "reel-3-gifts-voiceover-bed-6.8s.mp4", music_gain=0.3)
    if "sheet" in which or ("static" in which and "reels" in which):
        contact_sheet()
