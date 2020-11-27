from numpy.core.fromnumeric import mean
import pyaudio
import struct
import sys
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.pyplot import figure, draw, pause
from _tkinter import TclError

from kaleidoscope import kaleidoscope


mic = pyaudio.PyAudio()

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 2000
CHUNK = int(RATE / 10)

stream = mic.open(
    format=FORMAT,
    channels=CHANNELS,
    rate=RATE,
    input=True,
    output=True,
    frames_per_buffer=CHUNK,
)

# turn navigation toolbar off
plt.rcParams["toolbar"] = "None"
fg = figure()
fg.canvas.set_window_title("Kaleidoscope")
# fg.canvas.manager.window.overrideredirect(1)
ax = fg.gca()
# turn axes off
ax.axis("off")
data = 300
new_img = kaleidoscope(data, "assets/1.jpg")
h = ax.imshow(new_img, aspect="auto")

while True:
    try:
        data = stream.read(CHUNK, exception_on_overflow=False)
        data = np.array(struct.unpack(str(2 * CHUNK) + "B", data), dtype="b")[::2]
        mean_data = np.max(data)
        vis_size = np.interp(mean_data, [1, 200], [100, 500])
        # print(vis_size)
        new_img = kaleidoscope(int(vis_size), "assets/1.jpg")
        h.set_data(new_img)
        draw()
        pause(0.05)
    except (KeyboardInterrupt, TclError):
        sys.exit(0)

stream.stop_stream()
stream.close()
mic.terminate()
