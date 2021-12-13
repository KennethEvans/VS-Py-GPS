import tkinter as tk
from tkinter import filedialog
import matplotlib.pyplot as plt
import ctypes

def get_dpi(do_print=True):
	MM_TO_IN = 1/25.4
	# Set process DPI awareness
	ctypes.windll.shcore.SetProcessDpiAwareness(1)
	# Create a tkinter window
	root = tk.Tk()
	# Get a DC from the window's HWND
	dc = ctypes.windll.user32.GetDC(root.winfo_id())
	# The the monitor phyical width
	# (returned in millimeters then converted to inches)
	mw = ctypes.windll.gdi32.GetDeviceCaps(dc, 4) * MM_TO_IN
	# The the monitor phyical height
	mh = ctypes.windll.gdi32.GetDeviceCaps(dc, 6) * MM_TO_IN
	# Get the monitor horizontal resolution
	dw = ctypes.windll.gdi32.GetDeviceCaps(dc, 8)
	# Get the monitor vertical resolution
	dh = ctypes.windll.gdi32.GetDeviceCaps(dc, 10)
	# Destroy the window
	root.destroy()
	# Print the DPIs
	hdpi = dw / mw
	vdpi = dh / mh
	if do_print:
		print(round(hdpi, 1), round(vdpi, 1))
	# Horizontal and vertical DPIs calculated
	return hdpi, vdpi

# Print the DPIs
hdpi, vdpi = get_dpi()

if False:
	ctypes.windll.shcore.SetProcessDpiAwareness(1)
	root = tk.Tk()
	root.withdraw()
	file_path = filedialog.askopenfilename()
	root.destroy()

plt.figure(figsize=(10,6))
y = range(1,10)
plt.plot(y)
plt.show()
