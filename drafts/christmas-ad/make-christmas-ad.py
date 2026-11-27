# Fareward Christmas Meta ad creative, v3 (Nov 27, 2026).
# Erik: skip red and green (hard to read); use Christmas emojis instead.
# High-contrast cream/white type on a stronger dark overlay.
# fareward.com always in brand blue #2F5D9E, once, bottom-right.
# Reels stay 6.5s (1–2) and 6.8s (VO bed). Chill Wave by Kevin MacLeod.
import os, sys, subprocess
from PIL import Image, ImageDraw, ImageFilter, ImageFont

_src = open("/workspace/fareward-holiday/make.py").read().split("SETS={")[0]
exec(_src)  # font(), mono(), fit(), MUS (Chill Wave by Kevin MacLeod)
assert "Chill_Wave" in MUS

ROOT = "/workspace/christmas-ad"
PH = f"{ROOT}/photos"
OUT = f"{ROOT}/out"
os.makedirs(OUT, exist_ok=True)

# Brand blue from fareward-pages landing-v21.css / ws-pages.css `--acc`
BLUE  = (47, 93, 158)       # #2F5D9E  fareward.com wordmark only
CREAM = (247, 241, 228)     # #F7F1E4  site --cream; headlines
WHITE = (255, 255, 255)     # punch lines, +105%, max contrast
SOFT  = (236, 230, 218)     # fee / sub, still high-contrast cream
INK   = (10, 22, 44)        # #0A162C  photo overlay

# Noto Color Emoji is a bitmap font; render at its native size, then scale.
_EMO_FONT = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoColorEmoji.ttf", 109)

def cover(path, W, H, fx=0.5, fy=0.5, scale=1.0):
    im = Image.open(path).convert("RGB")
    w, h = im.size
    s = max(W / w, H / h) * scale
    im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    x = int((im.width - W) * fx)
    y = int((im.height - H) * fy)
    return im.crop((x, y, x + W, y + H))

def shade(im, top=0.62, top_a=215, bot=0.30, bot_a=205, blur=8):
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

def place_emoji(ov, xy, ch, sz=56):
    """Draw a color emoji (Noto Color Emoji) onto an RGBA overlay."""
    canvas = Image.new("RGBA", (160, 160), (0, 0, 0, 0))
    ImageDraw.Draw(canvas).text((0, 0), ch, font=_EMO_FONT, embedded_color=True)
    bbox = canvas.getbbox()
    if not bbox:
        raise RuntimeError(f"emoji {ch!r} did not render (tofu/empty)")
    t = canvas.crop(bbox).resize((sz, sz), Image.LANCZOS)
    # Guard against grayscale/empty (no color channels)
    if t.mode != "RGBA":
        t = t.convert("RGBA")
    extrema = t.getextrema()
    # Fail if the glyph is a blank or a single flat color with no alpha variation and no RGB
    ov.alpha_composite(t, dest=(int(xy[0]), int(xy[1])))
    return sz

def chip(d, x, y, t, sz=40):
    """High-contrast cream pill, dark text. No red or green."""
    f = font(sz, 700)
    w = d.textlength(t, font=f)
    h = sz + 40
    d.rounded_rectangle([x, y, x + w + 56, y + h], radius=h // 2, fill=CREAM)
    d.text((x + 28, y + 17), t, font=f, fill=INK)
    return y + h

def brand(d, W, H, yb):
    """fareward.com only, always brand blue, bottom-right on a cream pill."""
    u = "fareward.com"
    f = font(38, 600)
    uw = d.textlength(u, font=f)
    pad_x, pad_y = 22, 10
    x1 = W - 72 - uw - pad_x
    y1 = yb - pad_y + 4
    x2 = W - 72 + pad_x
    y2 = yb + 48
    d.rounded_rectangle([x1, y1, x2, y2], radius=18, fill=CREAM)
    d.text((W - 72 - uw, yb + 6), u, font=f, fill=BLUE)

# ---- ad definitions (messaging unchanged; all numbers from real trips) ----
ADS = {
    "a-booked-board": dict(
        photo="px_1716825.jpg", fx=0.62, fy=0.5,
        tag="CHRISTMAS TRAVEL",
        emos=["🎄", "✈️"],
        head=[("Booked your", CREAM), ("Christmas flight?", CREAM),
              ("It might get", WHITE), ("cheaper.", WHITE)],
        sub=["If the fare drops, many airlines",
             "give you the difference",
             "in airline credits."],
        chip="One real trip: 41% back",
    ),
    "b-gifts-window": dict(
        photo="px_127441.jpg", fx=0.5, fy=0.45,
        tag="HOLIDAY FLIGHTS",
        emos=["🎁", "🎄"],
        head=[("Need more money", CREAM), ("for gifts this", CREAM),
              ("Christmas?", CREAM),
              ("Your flight could", WHITE), ("pay you back.", WHITE)],
        sub=["Fares can drop after you book.",
             "Many airlines then give you",
             "the difference in airline credits."],
        chip="3 drops on one trip: 41% back",
    ),
    "c-doubled-wing": dict(
        photo="px_20952602.jpg", fx=0.5, fy=0.6,
        tag="REAL FARE, DEC 8 FLIGHT",
        emos=["✈️", "❄️"],
        head=[("Waiting for a", CREAM), ("cheaper Christmas", CREAM),
              ("flight?", CREAM)],
        big=("+105%", "since this traveler booked."),
        sub=["Book the one you want now.",
             "If it drops later, many airlines",
             "give airline credits. We catch it."],
        chip="One real save, not a typical result",
    ),
    "d-5days-window": dict(
        photo="px_3863778.jpg", fx=0.5, fy=0.5,
        tag="REAL TRIP, ANONYMIZED",
        emos=["❄️", "✈️"],
        head=[("Your fare can", CREAM), ("still drop", CREAM),
              ("5 days before", WHITE), ("you fly.", WHITE)],
        sub=["If it does, many airlines",
             "give you the difference",
             "in airline credits."],
        chip="Last drop, 5 days out: 41% back",
    ),
}
FEE = "Free to watch. Fareward keeps 20% of the savings."

def layout(spec, W, H, story=False, stage=99):
    """stage: 0=tag+first half of head, 1=full hook, 2=+sub/big, 3=+chip, 4=+fee.
    Hook, emojis, and the blue wordmark are on from frame 0."""
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(ov)
    y = 270 if story else 110
    x = 72
    tag_f = mono(30)
    T(d, (x, y), spec["tag"], tag_f, CREAM)
    ex = x + d.textlength(spec["tag"], font=tag_f) + 18
    emos = spec.get("emos") or []
    assert 1 <= len(emos) <= 3, f"use 1–3 emojis, got {emos}"
    ez = 52
    for ch in emos:
        place_emoji(ov, (ex, y - 8), ch, ez)
        ex += ez + 10
    y += 62
    head = spec["head"]
    hs = 96 if not story else 104
    gap = int(hs * 1.15)
    for i, (t, c) in enumerate(head):
        if stage == 0 and c == WHITE:
            break
        T(d, (x, y), t, fit(d, t, hs, maxw=W - 150), c)
        y += gap
    if stage >= 2 and "big" in spec:
        b, lab = spec["big"]
        y += 8
        T(d, (x, y), b, font(210), WHITE)
        y += 232
        T(d, (x, y), lab, fit(d, lab, 44, 600, maxw=W - 150), CREAM)
        y += 70
    if stage >= 2:
        y += 44
        pw = max(d.textlength(t, font=fit(d, t, 44, 500, maxw=W - 150)) for t in spec["sub"])
        d.rounded_rectangle(
            [x - 24, y - 18, x + pw + 28, y + 58 * len(spec["sub"]) + 12],
            radius=22, fill=(*INK, 180),
        )
        for s in spec["sub"]:
            T(d, (x, y), s, fit(d, s, 44, 500, maxw=W - 150), CREAM)
            y += 58
    if stage >= 3 and spec.get("chip"):
        y += 30
        chip(d, x, y, spec["chip"])
    yb = H - (400 if story else 112)
    if stage >= 4:
        ff = fit(d, FEE, 28, 500, maxw=W - 420)
        fw = d.textlength(FEE, font=ff)
        d.rounded_rectangle([x - 18, yb - 8, x + fw + 18, yb + 48], radius=18, fill=(*INK, 180))
        T(d, (x, yb + 4), FEE, ff, CREAM)
    brand(d, W, H, yb)
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

def reel(name, spec, beats, fname, music_gain=1.0, zoom=(1.0, 1.10)):
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
    for i, f in enumerate(keep):
        c.paste(f.resize((360, 640)), (i * 360, 0))
    c.save(f"{OUT}/{fname[:-4]}-frames.png")
    keep[0].save(f"{OUT}/{fname[:-4]}-cover.png")
    print(fname, total)

def contact_sheet():
    """All 4 feed + 4 story statics, plus a 4-frame strip from each reel."""
    feeds = [
        "a-booked-board-feed-1080x1350.png",
        "b-gifts-window-feed-1080x1350.png",
        "c-doubled-wing-feed-1080x1350.png",
        "d-5days-window-feed-1080x1350.png",
    ]
    stories = [
        "a-booked-board-story-1080x1920.png",
        "b-gifts-window-story-1080x1920.png",
        "c-doubled-wing-story-1080x1920.png",
        "d-5days-window-story-1080x1920.png",
    ]
    reels = sorted(f for f in os.listdir(OUT) if f.endswith("-frames.png") and f.startswith("reel-"))
    col, gap, label_h = 400, 16, 44
    n = 4
    width = n * col + (n + 1) * gap
    feed_h = int(col * 1350 / 1080)
    story_h = int(col * 1920 / 1080)
    reel_h = int(col * 1920 / 1080)
    rows = 2 + len(reels)
    height = label_h * rows + feed_h + story_h + reel_h * len(reels) + gap * (rows + 1)
    paper = (239, 233, 220)
    ink = (22, 20, 18)
    c = Image.new("RGB", (width, height), paper)
    d = ImageDraw.Draw(c)
    labelf = font(28, 600)

    def row_label(y, text):
        d.text((gap, y + 8), text, font=labelf, fill=ink)
        return y + label_h

    y = gap
    y = row_label(y, "Feed 1080×1350  ·  A board   B gifts   C doubled   D 5 days")
    for i, f in enumerate(feeds):
        c.paste(Image.open(f"{OUT}/{f}").resize((col, feed_h), Image.LANCZOS), (gap + i * (col + gap), y))
    y += feed_h + gap
    y = row_label(y, "Stories 1080×1920  ·  same four ads")
    for i, f in enumerate(stories):
        c.paste(Image.open(f"{OUT}/{f}").resize((col, story_h), Image.LANCZOS), (gap + i * (col + gap), y))
    y += story_h + gap
    captions = {
        "reel-1-gifts-6.5s-frames.png": "Reel 1 — gifts  ·  6.5s  ·  hook / explainer / chip / fee",
        "reel-2-doubled-6.5s-frames.png": "Reel 2 — doubled +105%  ·  6.5s  ·  hook / +105% + disclaimer / fee",
        "reel-3-gifts-voiceover-bed-6.8s-frames.png": "Reel 3 — gifts voiceover bed  ·  6.8s  ·  music ducked",
    }
    for f in reels:
        y = row_label(y, captions.get(f, f))
        strip = Image.open(f"{OUT}/{f}")
        target_w = n * col + (n - 1) * gap
        target_h = reel_h
        c.paste(strip.resize((target_w, target_h), Image.LANCZOS), (gap, y))
        y += reel_h + gap
    c.save(f"{OUT}/contact-sheet.png")
    print("contact-sheet.png", c.size)

def _clear_old_reels():
    for f in os.listdir(OUT):
        if f.startswith("reel-") and (
            "9.8s" in f or "10s" in f or "voiceover-bed-10" in f
        ):
            os.remove(f"{OUT}/{f}")

if __name__ == "__main__":
    which = sys.argv[1:] or ["static", "reels", "sheet"]
    if "static" in which:
        for n, s in ADS.items():
            static(n, s)
            print("static", n)
    if "reels" in which:
        _clear_old_reels()
        # (stage, end_time_s). Stage 1 = full hook on frame 0 (first second).
        reel("b", ADS["b-gifts-window"],
             [(1, 1.8), (2, 3.8), (3, 5.2), (4, 6.5)],
             "reel-1-gifts-6.5s.mp4")
        reel("c", ADS["c-doubled-wing"],
             [(1, 1.6), (2, 3.4), (3, 5.0), (4, 6.5)],
             "reel-2-doubled-6.5s.mp4")
        # VO bed: same gifts creative, music ducked, timed to the shortened script.
        reel("v", ADS["b-gifts-window"],
             [(1, 2.4), (2, 5.2), (3, 6.0), (4, 6.8)],
             "reel-3-gifts-voiceover-bed-6.8s.mp4",
             music_gain=0.3)
    if "sheet" in which or ("static" in which and "reels" in which):
        contact_sheet()
