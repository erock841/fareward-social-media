# Build the voiced Christmas reel: ad B visuals, locked v4 type, AI VO, Jingle Bells bed.
import os, sys, json, subprocess, asyncio
from pathlib import Path
from PIL import Image

# Load the v4 generator (fonts, layout primitives, ADS, shade, cover, etc.)
import importlib.util
_spec = importlib.util.spec_from_file_location("xmas", "/workspace/christmas-ad/make-christmas-ad.py")
xmas = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(xmas)

ROOT = Path("/workspace/christmas-ad")
OUT = ROOT / "out"
VO_DIR = ROOT / "vo"
VO_DIR.mkdir(exist_ok=True)
JINGLE = ROOT / "music" / "Jingle_Bells-Kevin_MacLeod.mp3"
EDGE = str(ROOT / ".venv/bin/python")

# 21 words, ~7s at a warm conversational pace. Uses "airline credits" (never promises a credit).
SCRIPT = (
    "Need gift money this Christmas? "
    "If your fare drops after you book, many airlines give airline credits. "
    "Fareward watches for you."
)
VOICE = "en-US-AndrewNeural"  # Microsoft Edge neural; tagged Warm, Confident, Authentic, Honest
RATE = "+8%"

# On-screen captions, locked v4 headline size, written to fit. One phrase per beat.
PHRASES = [
    {
        "cue": "Need",
        "lines": ["Need gift money", "this Christmas?"],
    },
    {
        "cue": "If",
        "lines": ["If your fare drops", "after you book,", "many airlines give", "airline credits."],
    },
    {
        "cue": "Fareward",
        "lines": ["Fareward watches", "for you."],
        "fee": True,
    },
]

def _synth():
    """Record the script with word timings via edge-tts."""
    code = r'''
import asyncio, json, sys, edge_tts
text, voice, rate, out_mp3, out_json = sys.argv[1:]
async def main():
    c = edge_tts.Communicate(text, voice, rate=rate)
    audio = b""
    words = []
    async for chunk in c.stream():
        if chunk["type"] == "audio":
            audio += chunk["data"]
        elif chunk["type"] in ("WordBoundary", "SentenceBoundary"):
            words.append({
                "type": chunk["type"],
                "text": chunk["text"],
                "offset": chunk["offset"] / 10_000_000.0,
                "duration": chunk["duration"] / 10_000_000.0,
            })
    open(out_mp3, "wb").write(audio)
    json.dump({"voice": voice, "rate": rate, "text": text, "words": words}, open(out_json, "w"), indent=2)
asyncio.run(main())
'''
    mp3 = VO_DIR / "andrew-script.mp3"
    meta = VO_DIR / "andrew-script.json"
    r = subprocess.run(
        [EDGE, "-c", code, SCRIPT, VOICE, RATE, str(mp3), str(meta)],
        check=True,
    )
    wav = VO_DIR / "andrew-script.wav"
    subprocess.check_call([
        "ffmpeg", "-y", "-i", str(mp3),
        "-af", "loudnorm=I=-16:TP=-1.5:LRA=11",
        "-ar", "48000", "-ac", "1", str(wav),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    data = json.loads(meta.read_text())
    return wav, data

def _phrase_starts(words):
    """Map each caption phrase to the start of its spoken sentence (or cue word)."""
    sentences = [w for w in words if w.get("type") == "SentenceBoundary"] or words
    starts = []
    used = set()
    for phrase in PHRASES:
        cue = phrase["cue"].lower()
        hit = None
        for i, w in enumerate(sentences):
            if i in used:
                continue
            text = w["text"].strip().lower()
            token = text.strip(".,!?").split()[:1]
            if text.startswith(cue.lower()) or (token and token[0] == cue.lower()):
                hit = w["offset"]
                used.add(i)
                break
        if hit is None:
            raise SystemExit(f"cue {phrase['cue']!r} not found in {[w['text'] for w in sentences]}")
        starts.append(hit)
    return starts

def vo_layout(lines, fee=False):
    """Locked v4 type on the gifts visual. Captions only; no extra chip."""
    W, H = 1080, 1920
    spec = xmas.ADS["b-gifts-window"]
    grid = xmas.STORY_Y
    ov = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    from PIL import ImageDraw
    d = ImageDraw.Draw(ov)
    xmas.place_emoji(ov, (xmas.X, grid["emoji"]), spec["emo"], xmas.EMOJI_SZ)
    hf = xmas.font(xmas.HEAD, xmas.HEAD_W)
    assert len(lines) <= xmas.HEAD_SLOTS
    for i, line in enumerate(lines):
        xmas.require_fit(f"vo line {i}", line, xmas.HEAD, xmas.HEAD_W)
        color = xmas.WHITE if i == len(lines) - 1 else xmas.CREAM
        xmas.T(d, (xmas.X, grid["head"] + i * xmas.HEAD_GAP), line, hf, color)
    yb = H - grid["fee_from_bottom"]
    if fee:
        ff = xmas.font(xmas.FEE, xmas.FEE_W)
        fw = d.textlength(xmas.FEE_LINE, font=ff)
        d.rounded_rectangle([xmas.X - 16, yb - 8, xmas.X + fw + 16, yb + 44], radius=16, fill=(*xmas.INK, 180))
        xmas.T(d, (xmas.X, yb + 4), xmas.FEE_LINE, ff, xmas.CREAM)
    xmas.brand(d, W, yb)
    return ov

def render_video(starts, vo_end, total, silent_mp4):
    W, H, FPS = 1080, 1920, 30
    spec = xmas.ADS["b-gifts-window"]
    zoom = (1.0, 1.10)
    big = xmas.cover(f"{xmas.PH}/{spec['photo']}", int(W * zoom[1]) + 2, int(H * zoom[1]) + 2, spec["fx"], spec["fy"])
    # Caption layers: hook on frame 0 even if VO starts a beat later.
    layers = []
    for i, phrase in enumerate(PHRASES):
        s = 0.0 if i == 0 else starts[i]
        e = starts[i + 1] if i + 1 < len(starts) else total
        layers.append((s, e, vo_layout(phrase["lines"], fee=phrase.get("fee", False))))
    p = subprocess.Popen(
        [
            "ffmpeg", "-y",
            "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
            "-t", f"{total:.3f}",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", "-crf", "19", "-preset", "fast",
            "-an", "-movflags", "+faststart", str(silent_mp4),
        ],
        stdin=subprocess.PIPE, stderr=subprocess.DEVNULL,
    )
    n = int(round(total * FPS))
    keep = []
    for k in range(n):
        t = k / FPS
        z = zoom[0] + (zoom[1] - zoom[0]) * (t / total)
        cw, ch = W * z, H * z
        cx, cy = big.width / 2, big.height / 2
        fr = big.crop((int(cx - cw / 2), int(cy - ch / 2), int(cx + cw / 2), int(cy + ch / 2))).resize((W, H), Image.BICUBIC)
        fr = xmas.shade(fr, top=0.72, top_a=248)
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
    assert p.returncode == 0, "ffmpeg video failed"
    return keep

def mix_audio(vo_wav, total, mixed_wav):
    """Jingle Bells bed, ducked under the VO. Fade in/out. No clipping."""
    # Skip the file's leading silence; start on the first Jingle Bells phrase.
    jingle_start = 0.55
    # Voice is loudnormed to -16 LUFS / -1.5 dBTP. Bed is audible but ducked under speech.
    filtergraph = (
        f"[1:a]atrim=start={jingle_start},asetpts=PTS-STARTPTS,"
        f"aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,"
        f"volume=0.62,afade=t=in:st=0:d=0.20,afade=t=out:st={total-0.70:.2f}:d=0.70[m];"
        f"[0:a]aformat=sample_fmts=fltp:sample_rates=48000:channel_layouts=stereo,"
        f"adelay=80|80,apad=whole_dur={total:.3f}[voice];"
        f"[m][voice]sidechaincompress=threshold=0.06:ratio=4:attack=15:release=280:makeup=1:knee=6[md];"
        f"[voice][md]amix=inputs=2:duration=longest:dropout_transition=0:normalize=0[ax];"
        f"[ax]alimiter=limit=0.89:attack=5:release=50,atrim=duration={total:.3f},asetpts=PTS-STARTPTS[a]"
    )
    subprocess.check_call([
        "ffmpeg", "-y",
        "-i", str(vo_wav),
        "-i", str(JINGLE),
        "-filter_complex", filtergraph,
        "-map", "[a]", "-ar", "48000", "-ac", "2", str(mixed_wav),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def measure(path):
    """Print duration, true peak, and integrated loudness."""
    dur = subprocess.check_output([
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", str(path),
    ], text=True).strip()
    # ebur128 + volumedetect
    log = subprocess.run(
        ["ffmpeg", "-i", str(path), "-af", "loudnorm=I=-16:TP=-1.5:print_format=json,volumedetect", "-f", "null", "-"],
        capture_output=True, text=True,
    ).stderr
    # Extract the printed JSON block and max_volume
    lines = log.splitlines()
    max_vol = next((ln for ln in lines if "max_volume" in ln), "")
    mean_vol = next((ln for ln in lines if "mean_volume" in ln), "")
    # loudnorm JSON is at the end
    js = log[log.rfind("{") : log.rfind("}") + 1] if "{" in log else ""
    print("duration", dur)
    print(max_vol)
    print(mean_vol)
    print(js)
    return float(dur), js, max_vol

def main():
    assert JINGLE.exists(), JINGLE
    wav, data = _synth()
    words = data["words"]
    vo_end = words[-1]["offset"] + words[-1]["duration"]
    starts = _phrase_starts(words)
    # Short tail after the last word so the jingle can cadence; cap at 8.0s.
    total = min(8.0, round(vo_end + 0.70, 2))
    if total < vo_end + 0.15:
        raise SystemExit(f"VO end {vo_end:.2f}s does not fit in an 8s reel")
    print("VO end", round(vo_end, 3), "phrase starts", [round(s, 3) for s in starts], "total", total)
    (VO_DIR / "timing.json").write_text(json.dumps({
        "script": SCRIPT, "voice": VOICE, "rate": RATE,
        "vo_end": vo_end, "starts": starts, "total": total, "words": words,
    }, indent=2))

    silent = VO_DIR / "vo-silent.mp4"
    keep = render_video(starts, vo_end, total, silent)
    mixed = VO_DIR / "vo-mixed.wav"
    mix_audio(wav, total, mixed)
    print("---- mix levels ----")
    measure(mixed)

    dur_tag = f"{total:.1f}".rstrip("0").rstrip(".") if False else f"{total:.1f}"
    # Use one decimal if not .0, else keep one decimal for consistency with prior names
    fname = f"reel-vo-gifts-{total:.1f}s.mp4"
    out = OUT / fname
    subprocess.check_call([
        "ffmpeg", "-y",
        "-i", str(silent),
        "-i", str(mixed),
        "-map", "0:v", "-map", "1:a",
        "-c:v", "copy",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        "-shortest",
        str(out),
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("---- final ----")
    measure(out)
    # frame strip + cover
    c = Image.new("RGB", (360 * len(keep), 640))
    for i, fimg in enumerate(keep):
        c.paste(fimg.resize((360, 640)), (i * 360, 0))
    c.save(OUT / f"{out.stem}-frames.png")
    keep[0].save(OUT / f"{out.stem}-cover.png")
    print("wrote", out)
    # drop stale vo-gifts files with a different duration in the name
    for f in OUT.iterdir():
        if f.name.startswith("reel-vo-gifts-") and out.stem not in f.name:
            f.unlink()
            print("removed stale", f.name)

if __name__ == "__main__":
    main()
