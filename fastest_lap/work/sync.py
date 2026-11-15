from pathlib import Path
import wave,numpy as np,json
root=Path(__file__).resolve().parents[2]; p=next(root.glob('*_CSV'))
w=wave.open(str(root/'fastest_lap/work/audio.wav')); a=np.frombuffer(w.readframes(w.getnframes()),dtype='<i2').astype(float); sr=w.getframerate()
n=2048; hop=800; frames=np.lib.stride_tricks.sliding_window_view(a,n)[::hop]; spec=np.abs(np.fft.rfft(frames*np.hanning(n),axis=1)); times=(np.arange(len(spec))*hop+n/2)/sr
# Whiten each frequency and each time, reducing wind and broad spectral coloration.
spec=np.log1p(spec); spec-=np.mean(spec,axis=0); spec-=np.mean(spec,axis=1)[:,None];spec/=np.std(spec,axis=0)[None,:]+.01
np.savez(root/'fastest_lap/work/spectrum.npz',spec=spec,times=times)
r=np.loadtxt(p/'RPM.csv',delimiter=',',skiprows=2)
sel=(times>300)&(times<1100); ts=times[sel]; s=spec[sel]; idx=np.arange(len(s))
for factor in [1/60,2/60,4/60,6/60]:
 scores=[]
 for offset in np.arange(-200,301,.1):
  rpm=np.interp(ts+offset,r[:,0],r[:,1]); bins=rpm*factor*n/sr
  lo=bins.astype(int); frac=bins-lo; v=s[idx,lo]*(1-frac)+s[idx,lo+1]*frac
  scores.append(v.mean())
 top=np.argsort(scores)[-5:][::-1];print(factor,[(round(-200+i*.1,3),round(scores[i],4)) for i in top],flush=True)
