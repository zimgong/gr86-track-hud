from pathlib import Path
import numpy as np, math, subprocess, json
from PIL import Image,ImageDraw,ImageFont
ROOT=Path(__file__).resolve().parents[2]; OUT=ROOT/'fastest_lap'; DATA=next(ROOT.glob('*_CSV'))
START=804.251; LAP=89.874; OFFSET=52.375; PRE=3.; POST=3.; DUR=PRE+LAP+POST; FPS=30000/1001
names=['SpeedV','RPM','Gear','Throttle Positio','BrakePress','Clutch','IMU LongG','IMU Lateral G']
channels={n:np.loadtxt(DATA/(n+'.csv'),delimiter=',',skiprows=2) for n in names}
gps=np.loadtxt(DATA/'_GPS.csv',delimiter=',',skiprows=1); gp=gps[(gps[:,0]>=START)&(gps[:,0]<=START+LAP)]
x=(gp[:,3]-gp[:,3].mean())*math.cos(math.radians(gp[:,2].mean()));y=-(gp[:,2]-gp[:,2].mean());scale=min(224/np.ptp(x),198/np.ptp(y)); pts=np.column_stack((x*scale+1750,y*scale+174)); track=[tuple(a) for a in pts]

def fmt(t):return f'{int(t)//60}:{t%60:06.3f}'
