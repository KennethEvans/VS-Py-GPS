''' GPX routines.
Based on https://towardsdatascience.com/how-tracking-apps-analyse-your-gps-data-a-hands-on-tutorial-in-python-756d4db6715d
'''

import numpy as np
import matplotlib.pyplot as plt
import gpxpy
from geopy import distance

import datetime
from math import sqrt, floor

import pandas as pd
import haversine

file_name = 'C:/Users/evans/Documents/GPSLink/Polar/Kenneth_Evans_2021-12-04_12-01-33_Walking_Kensington.gpx'
if True:
    # Prompt for the file name
    import tkinter as tk
    from tkinter import filedialog
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    root = tk.Tk()
    root.withdraw()    
    # Prompt to open a GPX file
    filetypes = (
        ('GPX files', '*.gpx'),
        ('All files', '*.*')
    )
    file_name = filedialog.askopenfilename(title='Open a GPX file', multiple=False,
        filetypes=filetypes)
    root.destroy()

print(f'Opening {file_name=}')
gpx_file = open(file_name, 'r')
gpx = gpxpy.parse(gpx_file)
n_trk = len(gpx.tracks)
print(f'Number of tracks: {n_trk}')
for trk in range(n_trk):
    print(f'Track {trk}:')
    n_seg = len(gpx.tracks[trk].segments)
    print(f'  Number of segments: {n_seg}')
    for seg in range(n_seg):
        print(f'  Segment {seg}:')
        n_wpt = len(gpx.tracks[trk].segments[seg].points)
        print(f'    Number of points: {n_wpt}')

if True:
    # Use lists
    print('Make a dataset for the first track, first segment')
    lat = []
    lon = []
    ele = []
    time = []
    # Just do first track, first segment
    n_trk = 1
    n_seg = 1
    for trk in range(n_trk):
        n_seg = len(gpx.tracks[trk].segments)
        for seg in range(n_seg):
            points = gpx.tracks[trk].segments[seg].points
            for point in points:
                lat.append(point.latitude)
                lon.append(point.longitude)
                ele.append(point.elevation)
                time.append(point.time)
else:
    # Use DataFrame
    print('Creating DataFrame')
    data = gpx.tracks[0].segments[0].points
    df = pd.DataFrame(columns=['lon', 'lat', 'ele', 'time'])
    for point in data:
        df = df.append({'lon': point.longitude, 'lat' : point.latitude,
            'ele' : point.elevation, 'time' : point.time}, ignore_index=True)
    lon = df['lon']
    lat = df['lat']

print('Plotting')
plt.figure(figsize=(10,6))
# Is necessary to not have scientific notation and offset
#plt.ticklabel_format(useOffset=False, style='plain')
plt.ticklabel_format(useOffset=False)
plt.plot(lon, lat)
plt.title(file_name)
plt.xlabel('longitude, deg')
plt.ylabel('latitude, deg')
plt.show()
