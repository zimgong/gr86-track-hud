import render as r
from PIL import Image,ImageDraw,ImageFont
import numpy as np, math, subprocess
ROOT=r.ROOT;OUT=r.OUT;DATA=r.DATA
r.channels['SteerAngle']=np.loadtxt(DATA/'SteerAngle.csv',delimiter=',',skiprows=2)
WHITE=(244,245,247,255);GRAY=(157,162,168,255);DARK=(46,49,54,255);RED=(244,47,58,255)
F={}
def text(d,xy,s,size=20,color=WHITE,anchor=None,italic=False):
 key=(size,italic)
 if key not in F:F[key]=ImageFont.truetype('/System/Library/Fonts/Supplemental/'+('Arial Narrow Bold Italic.ttf' if italic else 'Arial.ttf'),size)
 d.text(xy,s,font=F[key],fill=color,anchor=anchor)
DIGIT_FONTS={}
def digits(im,xy,value,size,color=WHITE,width_scale=0.78):
 if size not in DIGIT_FONTS:DIGIT_FONTS[size]=ImageFont.truetype(str(OUT/'work/Michroma-Regular.ttf'),size)
 f=DIGIT_FONTS[size];box=f.getbbox(value,stroke_width=0)
 tile=Image.new('RGBA',(box[2]-box[0]+8,box[3]-box[1]+8))
 ImageDraw.Draw(tile).text((4-box[0],4-box[1]),value,font=f,fill=color,stroke_width=1 if size>=40 else 0)
 tile=tile.resize((round(tile.width*width_scale),tile.height),Image.Resampling.LANCZOS)
 im.alpha_composite(tile,(round(xy[0]-tile.width/2),round(xy[1])))

def panel(d,b):d.rounded_rectangle(b,9,fill=(3,5,8,210),outline=(132,137,144,150),width=1)
def arc(d,c,rad,start,end,fill,width=9):
 d.arc((c[0]-rad,c[1]-rad,c[0]+rad,c[1]+rad),start,end,fill=fill,width=width)
base=Image.new('RGBA',(1920,1080));d=ImageDraw.Draw(base)
panel(d,(30,28,591,112))
logo=Image.open(OUT/'work/gr_boxed_vector.png').convert('RGBA').crop((0,0,293,149)).resize((82,42),Image.Resampling.LANCZOS)
base.alpha_composite(logo,(48,40))
text(d,(142,39),'THUNDERHILL WEST',27,italic=True);text(d,(50,83),'Zim Gong  /  GR86  /  24 OCT 2026',17,GRAY)
panel(d,(1605,28,1890,311));text(d,(1625,44),'TRACK MAP',18,GRAY);d.line(r.track+[r.track[0]],fill=(184,189,196,255),width=4,joint='curve');sx,sy=r.track[0];d.ellipse((sx-4,sy-4,sx+4,sy+4),fill=WHITE);text(d,(1625,282),'LAP 06',16,GRAY)

# Factory-inspired G monitor: four directional numbers, four input arcs.
C=(235,914);R=78
for radius in [39,78]:arc(d,C,radius,0,360,(115,120,126,230),2)
d.line((C[0]-R,C[1],C[0]+R,C[1]),fill=(135,140,146,230),width=1);d.line((C[0],C[1]-R,C[0],C[1]+R),fill=(135,140,146,230),width=1)
for aa,bb in [(198,258),(282,342),(18,78),(102,162)]:arc(d,C,113,aa,bb,DARK,13)
text(d,(145,794),'LEFT',16,GRAY);text(d,(290,794),'RIGHT',16,GRAY)
text(d,(113,996),'BRAKE',16,GRAY,anchor='ma');text(d,(360,996),'ACCELERATOR',16,GRAY,anchor='ma')
d.rectangle((299,1024,363,1045),outline=GRAY);text(d,(331,1024),'2.0 G',16,anchor='ma')
# Central Track-mode cluster silhouette, with sloping linear rev scale.
# Lines connect an upper and lower rail to the center circle, like the factory TFT.
arc(d,(969,917),129,210,330,(175,180,188,255),4)
arc(d,(969,917),129,30,150,(175,180,188,255),4)
d.line([(693,816),(888,816)],fill=(175,180,188,255),width=4);d.line([(1050,816),(1245,816)],fill=(175,180,188,255),width=4)
d.line([(693,992),(860,992)],fill=(175,180,188,255),width=4);d.line([(1078,992),(1245,992)],fill=(175,180,188,255),width=4)
# Nonlinear low-rev compression mirrors the 0 / 2 / 4 / 5 ... Track scale.
def xpos(rpm):return float(np.interp(rpm,[0,4000,9000],[741,811,1197]))
def topy(x):return 925-(x-760)*.16
SEGMENTS=[]
for left in np.arange(741,1197,7):
 right=min(left+4.5,1197)
 SEGMENTS.append((left,right))
 d.polygon([(left,topy(left)),(right,topy(right)),(right,957),(left,957)],fill=(83,22,28,255) if left>=xpos(7500) else (56,61,68,255))
for num in [0,2,4,5,6,7,8,9]:
 x=xpos(num*1000);digits(base,(x,topy(x)-25),str(num),24,RED if num>=8 else WHITE,width_scale=0.82)
d.line([(741,960),(1199,960)],fill=GRAY,width=1);text(d,(741,965),'x1000 r/min',14,GRAY)

text(d,(1430,803),'BEST LAP',17,GRAY);text(d,(1848,800),'1:29.874',28,WHITE,anchor='ra',italic=True)
text(d,(1430,849),'CURRENT LAP  06',18,GRAY)


# No branding in the bottom cluster.



MAX_SAMPLE_GAP = 0.5

def sample(name,t,step=False):
 a=r.channels[name]
 j=int(np.searchsorted(a[:,0],t,side='left'))
 if j<len(a) and abs(a[j,0]-t)<1e-7:return float(a[j,1])
 if j==0 or j==len(a):return float('nan')
 if a[j,0]-a[j-1,0]>MAX_SAMPLE_GAP:return float('nan')
 if step:return float(a[j-1,1])
 return float(np.interp(t,a[j-1:j+1,0],a[j-1:j+1,1]))

def speed_value(t):
 v=sample('SpeedV',t)
 if np.isfinite(v):return v/1.609344,False
 j=int(np.searchsorted(r.gps[:,0],t))
 if j==0 or j==len(r.gps) or r.gps[j,0]-r.gps[j-1,0]>MAX_SAMPLE_GAP:return float('nan'),True
 return float(np.interp(t,r.gps[:,0],r.gps[:,5])*2.2369362920544),True

def frame(sec):
 t=r.START+sec-r.PRE;im=base.copy();d=ImageDraw.Draw(im);elapsed=sec-r.PRE
 val=lambda n:sample(n,t,n in ['Gear','Clutch'])
 rpm=val('RPM');gear=val('Gear');speed,gps_speed=speed_value(t);th=val('Throttle Positio');br=val('BrakePress');cl=val('Clutch');steer=val('SteerAngle');lat=val('IMU Lateral G');long=val('IMU LongG')
 for left,right in SEGMENTS:
  if not np.isfinite(rpm) or left>=xpos(rpm):continue
  d.polygon([(left,topy(left)),(right,topy(right)),(right,957),(left,957)],fill=RED if left>=xpos(7500) else (246,180,64,255) if left>=xpos(6000) else WHITE)
 digits(im,(969,792),('--' if not np.isfinite(gear) else str(int(gear)) if gear else 'N'),68,RED if rpm>=7400 else WHITE,width_scale=0.72)
 digits(im,(952,977),f'{speed:.0f}' if np.isfinite(speed) else '--',44,width_scale=0.78)
 text(d,(1004,991),'mph',16,GRAY)
 text(d,(1235,1010),f'{rpm:,.0f} RPM' if np.isfinite(rpm) else '-- RPM',18,GRAY,anchor='ra')
 text(d,(1848,886),r.fmt(min(r.LAP,max(0,elapsed))),48,RED if elapsed>=r.LAP else WHITE,anchor='ra',italic=True)
 if elapsed<0:text(d,(1430,936),'LEAD-IN',15,GRAY)
 elif elapsed>=r.LAP:text(d,(1430,936),'FASTEST LAP',15,RED)
 if gps_speed:
  text(d,(1430,975),'GPS SPEED',18,GRAY)
  text(d,(1430,1002),'VEHICLE DATA GAP',16,GRAY)



 # Input quadrants around the G monitor, filled from their lower center ends.
 if br>.05:arc(d,C,113,102,102+60*min(1,br/40),RED,13)
 if th>.05:arc(d,C,113,78-60*th/100,78,WHITE,13)
 # Steering angle channel is measured at steering wheel, +/-180 deg visual full scale.
 if steer>0:arc(d,C,113,282,282+60*min(1,steer/180),WHITE,13)
 elif steer<0:arc(d,C,113,258-60*min(1,-steer/180),258,WHITE,13)
 text(d,(97,1024),f'{br:.1f} bar' if np.isfinite(br) else '-- bar',16,RED,anchor='ma');text(d,(394,1024),f'{th:.0f}%' if np.isfinite(th) else '--%',16,anchor='ma')
 # Short red dotted trail and current white dot, like the OEM G monitor.
 trail=np.arange(t-1.2,t,.1)
 for i,tt in enumerate(trail):
  la=sample('IMU Lateral G',tt);lo=sample('IMU LongG',tt)
  if not (np.isfinite(la) and np.isfinite(lo)):continue
  norm=max(1,math.hypot(la,lo)/2);xx=C[0]+la/norm*R/2;yy=C[1]-lo/norm*R/2
  d.ellipse((xx-3,yy-3,xx+3,yy+3),fill=(int(90+i*12),30,38,255))
 if np.isfinite(lat) and np.isfinite(long):
  norm=max(1,math.hypot(lat,long)/2);xx=C[0]+lat/norm*R/2;yy=C[1]-long/norm*R/2;d.ellipse((xx-6,yy-6,xx+6,yy+6),fill=WHITE)
 for pos,v in [((C[0],818),long),((C[0],996),-long),((128,899),-lat),((342,899),lat)]:
  text(d,pos,f'{max(0,v):.2f}' if np.isfinite(v) else '--',23,anchor='ma')
 latgps=np.interp(t,r.gps[:,0],r.gps[:,2]);longps=np.interp(t,r.gps[:,0],r.gps[:,3])
 px=(longps-r.gp[:,3].mean())*math.cos(math.radians(r.gp[:,2].mean()))*r.scale+1750
 py=-(latgps-r.gp[:,2].mean())*r.scale+174
 d.ellipse((px-7,py-7,px+7,py+7),fill=RED,outline=WHITE,width=2)
 compact=Image.new('RGBA',(1920,1080))
 compact.paste(im.crop((0,0,1920,750)),(0,0))
 panel(ImageDraw.Draw(compact),(330,840,1590,1055))
 for box,size,pos in [((60,790,445,1048),(289,194),(350,850)),((690,780,1248,1048),(424,204),(748,844)),((1420,790,1860,1048),(330,194),(1220,850))]:
  tile=im.crop(box).resize(size,Image.Resampling.LANCZOS)
  compact.alpha_composite(tile,pos)
 return compact
if __name__=='__main__':
 for sec in [1,12,38,68,94]:frame(sec).save(OUT/'work'/f'gr86_overlay_{sec}.png')
 proc=subprocess.Popen(['ffmpeg','-v','error','-f','rawvideo','-pixel_format','rgba','-video_size','1920x1080','-framerate',str(r.FPS),'-i','pipe:0','-an','-c:v','qtrle','-pix_fmt','argb','-y',str(OUT/'work/gr86_overlay.mov')],stdin=subprocess.PIPE)
 for i in range(math.ceil(r.DUR*r.FPS)):
  proc.stdin.write(frame(i/r.FPS).tobytes())
  if i%600==0:print(f'GR86 overlay {i/r.FPS:.0f}/{r.DUR:.0f}s',flush=True)
 proc.stdin.close()
 if proc.wait():raise RuntimeError('Overlay encoding failed')
 print('GR86 overlay complete',flush=True)
