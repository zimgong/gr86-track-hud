import numpy as np
from pathlib import Path
r=np.loadtxt(next(Path('.').glob('*_CSV'))/'RPM.csv',delimiter=',',skiprows=2);z=np.load('fastest_lap/work/spectrum.npz'); ts=z['times'];s=z['spec']
for start,end in [(300,500),(700,900),(1000,1200),(751,842)]:
 sel=(ts>start)&(ts<end);t=ts[sel];a=s[sel];idx=np.arange(len(t)); scores=[];offs=np.arange(52.2,52.61,.005)
 for off in offs:
  rpm=np.interp(t+off,r[:,0],r[:,1]);score=0
  for fac in [2/60,4/60]:
   b=rpm*fac*2048/8000;l=b.astype(int);f=b-l;score+=(a[idx,l]*(1-f)+a[idx,l+1]*f).mean()
  scores.append(score)
 print(start,end,round(offs[np.argmax(scores)],3),round(max(scores),3))
