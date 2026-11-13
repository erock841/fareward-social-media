import os, subprocess, sys
from PIL import Image, ImageDraw
_src=open("/workspace/fareward-holiday/make.py").read().split("SETS={")[0]
exec(_src)
OUTROOT="/workspace/fareward-next5/drafts"
AIR1="American · Alaska · Delta · Hawaiian";AIR2="JetBlue · Southwest · United"
def cta(head="HOW TO START"):
    def f(d,y):
        d.text((80,y),head,font=mono(32),fill=BLUE)
        y+=65
        for n,t in [("1","Book your flight like normal"),("2","Forward your confirmation to"),("3","We watch until takeoff")]:
            d.ellipse([80,y,150,y+70],fill=NAVY);fn=font(42);d.text((115-d.textlength(n,font=fn)/2,y+8),n,font=fn,fill=WHITE)
            d.text((180,y+8),t,font=font(44),fill=NAVY)
            if n=="2": d.text((180,y+68),"trips (at) fareward.com",font=font(50),fill=BLUE); y+=70
            y+=100
        y+=10
        for a in ["Free to watch","Fareward keeps 20% of the savings."]:
            check(d,80,y);d.text((160,y+2),a,font=font(40),fill=NAVY);y+=80
        d.text((80,y+5),AIR1,font=font(36,500),fill=GREY)
        d.text((80,y+52),AIR2,font=font(36,500),fill=GREY)
        y+=125
        d.rounded_rectangle([80,y,520,y+100],radius=50,fill=NAVY)
        fn=font(42);d.text((300-d.textlength("Link in bio",font=fn)/2,y+26),"Link in bio",font=fn,fill=WHITE)
    return f
def big(tag,ls,sub=None,gap=120,sz=100):
    def f(d,y):
        d.text((80,y),tag,font=mono(32),fill=BLUE)
        y=L(d,y+70,ls,sz,gap)
        if sub: d.text((80,y+40),sub,font=fit(d,sub,46,500),fill=GREY)
    return f
def checklist(n_show=3,head=True):
    items=[("Pick your seat.",NAVY),("Add the trip to",NAVY),("your calendar.",NAVY),("Watch the price.",None)]
    def f(d,y):
        d.text((80,y),"JUST BOOKED?",font=mono(32),fill=BLUE)
        y=L(d,y+70,[("Do these",NAVY),("3 things.",NAVY)],100,120)+40
        rows=[("1",["Pick your seat."]),("2",["Add the trip to","your calendar."]),("3",["Watch the price."])]
        for i,(n,ts) in enumerate(rows):
            if i>=n_show: break
            d.ellipse([80,y,170,y+90],fill=(GREEN if n=="3" else NAVY));fn=font(54)
            d.text((125-d.textlength(n,font=fn)/2,y+12),n,font=fn,fill=WHITE)
            for j,t in enumerate(ts): d.text((200,y+10+j*78),t,font=font(66),fill=(GREEN if n=="3" else NAVY))
            y+=80*len(ts)+70
    return f
def why3():
    def f(d,y):
        d.text((80,y),"WHY NUMBER 3?",font=mono(32),fill=BLUE)
        y=L(d,y+70,[("Fares can drop",NAVY),("after you buy.",NAVY)],96,114)
        y=box(d,y+30,[("Many airlines give you",WHITE),("the difference",WHITE),("in airline credits.",LB)])
        d.text((80,y+45),"We do number 3 for you.",font=fit(d,"We do number 3 for you.",50),fill=BLUE)
    return f
# real trip (SFO-RDU United First) as % of booked fare: booked, -8%, -26%, -41% low, then back up 26% from the low
PV=[3448.81,3178.70,2552.30,2034.32,2570.00]
LB5=["Booked","Oct 18","Oct 29","Oct 30","Nov 3"]
def linechart(prog=1.0,title=None):
    def f(d,y):
        d.text((80,y),"REAL TRIP, ANONYMIZED",font=mono(32),fill=BLUE)
        L(d,y+70,title or [("The lowest fare",NAVY),("didn't last.",NAVY)],100,120)
        cy0,cy1=y+470,y+900
        d.rounded_rectangle([80,cy0-70,1000,cy1+110],radius=28,fill=WHITE)
        Y=lambda v:cy1-(v-1900)/(3550-1900)*(cy1-cy0)
        xs=[150,330,510,690,870]
        r=prog*(len(PV)-1)
        pts=[(xs[i],Y(v)) for i,v in enumerate(PV)]
        for i in range(len(PV)-1):
            fr=max(0,min(1,r-i))
            if fr<=0: break
            (x0,y0),(x1,y1)=pts[i],pts[i+1]
            col=RED_UP if i==3 else GREEN
            d.line([(x0,y0),(x0+(x1-x0)*fr,y0+(y1-y0)*fr)],fill=col,width=10)
        for i,(x,yy) in enumerate(pts):
            if i>r+1e-6: break
            d.ellipse([x-13,yy-13,x+13,yy+13],fill=(NAVY if i==0 else (RED_UP if i==4 else GREEN)))
            d.text((x-d.textlength(LB5[i],font=mono(24))/2,cy1+45),LB5[i],font=mono(24),fill=GREY)
        if r>=3-1e-6:
            x,yy=pts[3];t="Low: 41% off";fn=font(40);d.text((x-d.textlength(t,font=fn)/2,yy+26),t,font=fn,fill=GREEN)
        if r>=4-1e-6:
            x,yy=pts[4];t="+26%";fn=font(54);d.text((x-d.textlength(t,font=fn)/2,yy-80),t,font=fn,fill=RED_UP)
    return f
RED_UP=(196,30,58)
def counter(n):
    def f(d,y):
        d.text((80,y),"REAL TRIP, ANONYMIZED",font=mono(32),fill=BLUE)
        y=L(d,y+70,[("You don't have",NAVY),("time to check",NAVY),("your fare",NAVY)],100,120)
        d.text((80,y),f"{n}",font=font(260),fill=BLUE)
        d.text((80+d.textlength(f"{n}",font=font(260))+30,y+150),"times.",font=font(100),fill=NAVY)
    return f
def save29():
    def f(d,y):
        d.text((80,y),"REAL TRIP, ANONYMIZED",font=mono(32),fill=BLUE)
        y=L(d,y+70,[("to save",NAVY)],100,130)
        d.text((80,y),"29%",font=font(260),fill=GREEN)
        d.text((80,y+310),"We do.",font=font(120),fill=BLUE)
        d.text((80,y+470),"One real trip: SFO → SJD",font=fit(d,"One real trip: SFO → SJD",40,500),fill=GREY)
    return f
def mk(f,H=1920,y0=380):
    im,d=base(H,110);f(d,y0);return im.convert("RGB")
def render_reel(name,O,frames,plan):
    fd=f"/tmp/n5_{name}";os.makedirs(fd,exist_ok=True)
    for x in os.listdir(fd): os.remove(f"{fd}/{x}")
    k=0
    for p in plan:
        if p[0]=="A":
            for im in p[1]: im.save(f"{fd}/f_{k:04d}.png");k+=1
        elif p[0]=="x":
            n=int(p[3]*30)
            for i in range(n):
                a=(i+1)/(n+1);a=a*a*(3-2*a)
                Image.blend(frames[p[1]],frames[p[2]],a).save(f"{fd}/f_{k:04d}.png");k+=1
        else:
            for _ in range(int(round(p[1]*30))): frames[p[0]].save(f"{fd}/f_{k:04d}.png");k+=1
    T=k/30;assert T<=10.0,(name,T)
    subprocess.run(["ffmpeg","-y","-framerate","30","-i",f"{fd}/f_%04d.png","-i",MUS,"-filter_complex",
     f"[1:a]atrim=start=4,asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-1.5,afade=t=in:st=0:d=0.2,afade=t=out:st={T-1.2:.2f}:d=1.2[a]",
     "-map","0:v","-map","[a]","-t",f"{T:.3f}","-c:v","libx264","-pix_fmt","yuv420p","-crf","20","-preset","fast","-c:a","aac","-b:a","192k","-movflags","+faststart",f"{O}/{name}-reel.mp4"],check=True,capture_output=True)
    print(name,"dur",T)
    return T
def carousel(O,slides):
    for i,(nm,f) in enumerate(slides):
        im,d=base(1350,70);f(d,150);im.save(f"{O}/slide-{i+1:02d}-{nm}.png")
    cols=2 if len(slides)<=4 else 3;rows=(len(slides)+cols-1)//cols
    c=Image.new("RGB",(1080*cols,1350*rows),"white")
    for i,(nm,_) in enumerate(slides): c.paste(Image.open(f"{O}/slide-{i+1:02d}-{nm}.png"),((i%cols)*1080,(i//cols)*1350))
    c.resize((540*cols,675*rows)).save(f"{O}/contact-carousel.png")
def contact_reel(O,frames):
    c=Image.new("RGB",(1080*len(frames),1920));[c.paste(x,(i*1080,0)) for i,x in enumerate(frames)];c.resize((360*len(frames),640)).save(f"{O}/contact-reel-frames.png")
_B,_G=BLUE,GREEN
def setcol(christmas=False):
    global BLUE,GREEN
    BLUE,GREEN=((RED,XG) if christmas else (_B,_G))
EXPL=lambda note="Most people never catch it.":explain([("Price drops",NAVY),("after you buy?",NAVY)],note)
P41=lambda:proof("41%","3 drops on one trip:","United First · SFO → RDU","Last drop: 5 days before the flight")

which=sys.argv[1:] or ["family-flights","after-you-book","christmas-gifts","cheap-fare-didnt-last","164-checks"]
for name in which:
    O=f"{OUTROOT}/{name}";os.makedirs(O,exist_ok=True)
    setcol(name=="christmas-gifts")
    if name=="family-flights":
        A=hook("HOLIDAY TRAVEL",[("Send this to",NAVY),("whoever books",NAVY),("the family flights.",BLUE)],None,(0,["✈️"]))
        fr=[mk(A),mk(EXPL()),mk(P41()),mk(cta())]
        plan=[(0,2.0),("x",0,1,0.4),(1,2.3),("x",1,2,0.4),(2,2.0),("x",2,3,0.4),(3,2.4)]
        sl=[("hook",A),("explainer",EXPL()),("proof",P41()),("cta",cta("SEND THIS TO THEM"))]
    elif name=="after-you-book":
        A=big("JUST BOOKED?",[("Just booked",NAVY),("a flight?",NAVY),("Do these",BLUE),("3 things.",BLUE)])
        c1,c2,c3=mk(checklist(1)),mk(checklist(2)),mk(checklist(3))
        fr=[mk(A),c1,c2,c3,mk(why3()),mk(cta("WE DO NUMBER 3"))]
        plan=[(0,1.5),("x",0,1,0.3),(1,0.9),(2,0.9),(3,1.4),("x",3,4,0.3),(4,2.2),("x",4,5,0.3),(5,2.1)]
        sl=[("hook",A),("checklist",checklist(3)),("why-3",why3()),("cta",cta("WE DO NUMBER 3"))]
    elif name=="christmas-gifts":
        A=hook("CHRISTMAS TRAVEL",[("Need more money",NAVY),("for gifts this",NAVY),("Christmas?",NAVY),("Your flight could",BLUE),("pay you back.",BLUE)],"In airline credits, if your fare drops.",(2,"🎅🎁"))
        E=explain([("Fares can drop",NAVY),("after you buy.",NAVY)],"Most people never catch it.")
        fr=[mk(A),mk(E),mk(P41()),mk(cta())]
        plan=[(0,2.2),("x",0,1,0.4),(1,2.2),("x",1,2,0.4),(2,1.9),("x",2,3,0.4),(3,2.4)]
        sl=[("hook",A),("explainer",E),("proof",P41()),("cta",cta())]
    elif name=="cheap-fare-didnt-last":
        anim=[mk(linechart((i+1)/45)) for i in range(45)]
        E=explain([("Fare drops",NAVY),("after you book?",NAVY)],"We caught this one: 41% back.")
        fr=[mk(linechart(0.0)),anim[-1],mk(E),mk(cta())]
        plan=[(0,0.6),("A",anim),(1,1.4),("x",1,2,0.4),(2,2.4),("x",2,3,0.4),(3,2.3)]
        sl=[("hook",big("REAL TRIP, ANONYMIZED",[("The lowest fare",NAVY),("on this flight",NAVY),("didn't last.",BLUE)],"Miss it and it's gone.")),("chart",linechart(1.0,[("Down 41%.",GREEN),("Then up 26%.",RED_UP)])),("explainer",E),("cta",cta())]
    elif name=="164-checks":
        nums=[int(round(1+163*((i+1)/36)**1.6)) for i in range(36)]
        anim=[mk(counter(n)) for n in nums]
        B=save29()
        fr=[anim[-1],mk(B),mk(EXPL("We watch it, so you don't have to.")),mk(cta())]
        plan=[("A",anim),(0,0.8),("x",0,1,0.3),(1,1.8),("x",1,2,0.3),(2,2.1),("x",2,3,0.3),(3,2.0)]
        sl=[("hook",counter(164)),("proof",B),("explainer",EXPL("We watch it, so you don't have to.")),("cta",cta())]
    fr[0].save(f"{O}/reel-cover.png")
    render_reel(name,O,fr,plan)
    contact_reel(O,fr)
    carousel(O,sl)
