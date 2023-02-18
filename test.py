from scipy import signal
import sounddevice as sd
import matplotlib.pyplot as plt
import numpy as np

duration = 1
fs = 44100
recording = sd.rec(int(duration * fs), samplerate = fs, channels =1, dtype='float64')
sd.wait(duration)
print(recording)

N = recording.shape[0]
print(N , recording.shape)
L = N/fs
tuckey_window=signal.windows.tukey(N,0.01,True) #generate the Tuckey window, widely open, alpha=0.01
ysc=recording[:,0]*tuckey_window               #applying the Tuckey window
yk = np.fft.rfft(ysc)                   #real to complex DFT
k = np.arange(yk.shape[0])
freqs = k/L
fig, ax = plt.subplots()
ax.plot(freqs, np.abs(yk))
plt.show()