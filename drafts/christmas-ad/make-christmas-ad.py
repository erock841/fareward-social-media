# Fareward Christmas Meta ad creative. Reuses the drafts/make-next5.py pipeline
# (fonts, Chill Wave track, ffmpeg settings) and adds full-bleed photo layouts.
import os, sys, subprocess, json
from PIL import Image, ImageDraw, ImageFilter
_src=open("/workspace/fareward-holiday/make.py").read().split("SETS={")[0]
exec(_src)   # font(), mono(), fit(), MUS (Chill Wave by Kevin MacLeod)
assert "Chill_Wave" in MUS
ROOT="/workspace/christmas-ad"; PH=f"{ROOT}/photos"; OUT=f"{ROOT}/out"
os.makedirs(OUT,exist_ok=True)
WHITE=(255,255,255); SOFT=(225,232,245); GOLD=(244,201,120); MINT=(140,226,170); INK=(10,22,44)

def cover(path,W,H,fx=0.5,fy=0.5,scale=1.0):
    im=Image.open(path).convert("RGB"); w,h=im.size
    s=max(W/w,H/h)*scale; im=im.resize((round(w*s),round(h*s)),Image.LANCZOS)
    x=int((im.width-W)*fx); y=int((im.height-H)*fy)
    return im.crop((x,y,x+W,y+H))

def shade(im,top=0.62,top_a=215,bot=0.30,bot_a=205,blur=7):
    W,H=im.size
    if blur:  # soft focus behind the text zone so copy stays readable on busy photos
        m=Image.new("L",(W,H),0); md=ImageDraw.Draw(m); bh=int(H*top*0.95)
        for y in range(bh): md.line([(0,y),(W,y)],fill=int(255*min(1,(1-y/bh)*1.6)))
        im=Image.composite(im.filter(ImageFilter.GaussianBlur(blur)),im,m)
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); px=ImageDraw.Draw(ov)
    tH=int(H*top)
    for y in range(tH):
        a=int(top_a*(1-y/tH)**1.15); px.line([(0,y),(W,y)],fill=(*INK,a))
    bH=int(H*bot)
    for y in range(bH):
        a=int(bot_a*(y/bH)**1.4); px.line([(0,H-bH+y),(W,H-bH+y)],fill=(*INK,a))
    return Image.alpha_composite(im.convert("RGBA"),ov)

def T(d,xy,t,f,c):  # text with soft shadow for legibility on photos
    x,y=xy; d.text((x+2,y+3),t,font=f,fill=(0,0,0,110)); d.text((x,y),t,font=f,fill=c)

def chip(d,x,y,t,sz=40,bg=GOLD,fg=INK):
    f=font(sz,700); w=d.textlength(t,font=f)
    d.rounded_rectangle([x,y,x+w+56,y+sz+40],radius=(sz+40)//2,fill=bg); d.text((x+28,y+17),t,font=f,fill=fg)
    return y+sz+40

def brand(d,W,H,yb):
    u="fareward.com"; f=font(38,600); uw=d.textlength(u,font=f)
    d.rounded_rectangle([W-72-uw-18,yb-8,W-72+18,yb+56],radius=18,fill=(*INK,165)); T(d,(W-72-d.textlength(u,font=f),yb),u,f,WHITE)

# ---- ad definitions (all numbers are from real Fareward trips) ----
ADS={
 "a-booked-board":dict(photo="px_1716825.jpg",fx=0.62,fy=0.5,
   tag="CHRISTMAS TRAVEL",
   head=[("Booked your",WHITE),("Christmas flight?",WHITE),("It might get",GOLD),("cheaper.",GOLD)],
   sub=["If the fare drops, many airlines","give you the difference","in airline credits."],
   chip="One real trip: 41% back"),
 "b-gifts-window":dict(photo="px_127441.jpg",fx=0.5,fy=0.45,
   tag="HOLIDAY FLIGHTS",
   head=[("Need more money",WHITE),("for gifts this",WHITE),("Christmas?",WHITE),("Your flight could",GOLD),("pay you back.",GOLD)],
   sub=["Fares can drop after you book.","Many airlines then give you","the difference in airline credits."],
   chip="3 drops on one trip: 41% back"),
 "c-doubled-wing":dict(photo="px_20952602.jpg",fx=0.5,fy=0.6,
   tag="REAL FARE, DEC 8 FLIGHT",
   head=[("Waiting for a",WHITE),("cheaper Christmas",WHITE),("flight?",WHITE)],
   big=("+105%","since this traveler booked."),
   sub=["Book the one you want now.","If it drops later, many airlines","give airline credits. We catch it."],
   chip=None),
 "d-5days-window":dict(photo="px_3863778.jpg",fx=0.5,fy=0.5,
   tag="REAL TRIP, ANONYMIZED",
   head=[("Your fare can",WHITE),("still drop",WHITE),("5 days before",GOLD),("you fly.",GOLD)],
   sub=["If it does, many airlines","give you the difference","in airline credits."],
   chip="Last drop, 5 days out: 41% back"),
}
FEE="Free to watch. Fareward keeps 20% of the savings."

def layout(spec,W,H,story=False,stage=99):
    """stage limits what's drawn (for reel text beats). 0=tag+head(first half),1=head,2=+sub/big,3=+chip,4=+fee"""
    ov=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(ov)
    y=270 if story else 110; x=72
    T(d,(x,y),spec["tag"],mono(30),GOLD); y+=62
    head=spec["head"]; hs=96 if not story else 104; gap=int(hs*1.15)
    for i,(t,c) in enumerate(head):
        if stage==0 and c==GOLD: break
        T(d,(x,y),t,fit(d,t,hs,maxw=W-150),c); y+=gap
    if stage>=2 and "big" in spec:
        b,lab=spec["big"]; y+=8; T(d,(x,y),b,font(210),MINT); y+=232
        T(d,(x,y),lab,fit(d,lab,44,600,maxw=W-150),WHITE); y+=70
    if stage>=2:
        y+=44
        pw=max(d.textlength(t,font=fit(d,t,44,500,maxw=W-150)) for t in spec["sub"])
        d.rounded_rectangle([x-24,y-18,x+pw+28,y+58*len(spec["sub"])+12],radius=22,fill=(*INK,150))
        for s in spec["sub"]:
            T(d,(x,y),s,fit(d,s,44,500,maxw=W-150),SOFT); y+=58
    if stage>=3 and spec.get("chip"):
        y+=30; chip(d,x,y,spec["chip"])
    yb=H-(400 if story else 112)
    if stage>=4:
        ff=fit(d,FEE,28,500,maxw=W-420); fw=d.textlength(FEE,font=ff)
        d.rounded_rectangle([x-18,yb-8,x+fw+18,yb+48],radius=18,fill=(*INK,165))
        T(d,(x,yb+4),FEE,ff,SOFT)
    brand(d,W,H,yb)
    return ov

def static(name,spec):
    for tag,(W,H,story) in {"feed-1080x1350":(1080,1350,False),"story-1080x1920":(1080,1920,True)}.items():
        bg=shade(cover(f"{PH}/{spec['photo']}",W,H,spec["fx"],spec["fy"]),top=0.80 if not story else 0.66,top_a=238)
        im=Image.alpha_composite(bg,layout(spec,W,H,story)).convert("RGB")
        im.save(f"{OUT}/{name}-{tag}.png")

def reel(name,spec,beats,fname,music_gain=1.0,zoom=(1.0,1.10)):
    W,H=1080,1920; FPS=30; total=beats[-1][1]; assert total<=10.0
    big=cover(f"{PH}/{spec['photo']}",int(W*zoom[1])+2,int(H*zoom[1])+2,spec["fx"],spec["fy"])
    layers=[(s,e,layout(spec,W,H,True,stage)) for stage,e,s in [(b[0],b[1],(beats[i-1][1] if i else 0)) for i,b in enumerate(beats)]]
    p=subprocess.Popen(["ffmpeg","-y","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i",MUS,
      "-filter_complex",f"[1:a]atrim=start=4,asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-1.5,volume={music_gain},afade=t=in:st=0:d=0.2,afade=t=out:st={total-1.2:.2f}:d=1.2[a]",
      "-map","0:v","-map","[a]","-t",f"{total:.3f}","-c:v","libx264","-pix_fmt","yuv420p","-crf","19","-preset","fast","-c:a","aac","-b:a","192k","-movflags","+faststart",f"{OUT}/{fname}"],
      stdin=subprocess.PIPE,stderr=subprocess.DEVNULL)
    n=int(round(total*FPS)); keep=[]
    for k in range(n):
        t=k/FPS; z=zoom[0]+(zoom[1]-zoom[0])*(t/total)
        cw,ch=W*z,H*z; cx,cy=big.width/2,big.height/2
        fr=big.crop((int(cx-cw/2),int(cy-ch/2),int(cx+cw/2),int(cy+ch/2))).resize((W,H),Image.BICUBIC)
        fr=shade(fr,top=0.66,top_a=238)
        cur=[L for (s,e,L) in layers if s<=t<e] or [layers[-1][2]]
        # 0.25s crossfade into each new beat (first beat is on screen at frame 0: hook visible immediately)
        i=[j for j,(s,e,L) in enumerate(layers) if s<=t<e]; i=i[0] if i else len(layers)-1
        s=layers[i][0]
        if i>0 and t-s<0.25:
            a=(t-s)/0.25; prev=layers[i-1][2]
            fr=Image.alpha_composite(fr,Image.blend(prev,layers[i][2],a))
        else: fr=Image.alpha_composite(fr,layers[i][2])
        fr=fr.convert("RGB"); p.stdin.write(fr.tobytes())
        if k in (0,int(n*0.35),int(n*0.65),n-1): keep.append(fr)
    p.stdin.close(); p.wait(); assert p.returncode==0
    c=Image.new("RGB",(360*len(keep),640)); [c.paste(f.resize((360,640)),(i*360,0)) for i,f in enumerate(keep)]
    c.save(f"{OUT}/{fname[:-4]}-frames.png"); keep[0].save(f"{OUT}/{fname[:-4]}-cover.png")
    print(fname,total)

if __name__=="__main__":
    which=sys.argv[1:] or ["static","reels"]
    if "static" in which:
        for n,s in ADS.items(): static(n,s)
        fs=sorted(f for f in os.listdir(OUT) if f.endswith("feed-1080x1350.png"))
        ss=sorted(f for f in os.listdir(OUT) if f.endswith("story-1080x1920.png"))
        c=Image.new("RGB",(4*540,675+960+20),"white")
        for i,f in enumerate(fs): c.paste(Image.open(f"{OUT}/{f}").resize((540,675)),(i*540,0))
        for i,f in enumerate(ss): c.paste(Image.open(f"{OUT}/{f}").resize((540,960)),(i*540,695))
        c.save(f"{OUT}/contact-sheet.png")
    if "reels" in which:
        # (stage, end_time_s). Stage 1 = full hook on frame 0.
        reel("b",ADS["b-gifts-window"],[(1,2.6),(2,5.6),(3,7.8),(4,9.8)],"reel-1-gifts-9.8s.mp4")
        reel("c",ADS["c-doubled-wing"],[(1,2.4),(2,7.2),(4,9.8)],"reel-2-doubled-9.8s.mp4")
        # VO version: same beats retimed to the voiceover script; music ducked so Erik's voice sits on top
        reel("v",ADS["b-gifts-window"],[(1,3.0),(2,7.0),(3,8.4),(4,10.0)],"reel-3-gifts-voiceover-bed-10s.mp4",music_gain=0.3)
