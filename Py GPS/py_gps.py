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

def prompt_for_file_name():
    # Prompt for the file name
    import tkinter as tk
    from tkinter import filedialog
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    root = tk.Tk()
    root.withdraw()    
    # Prompt to open a GPX file
    filetypes = (('GPX files', '*.gpx'),
        ('All files', '*.*'))
    file_name = filedialog.askopenfilename(title='Open a GPX file', multiple=False,
        filetypes=filetypes)
    root.destroy()
    return file_name


def get_gpx_data(prompt=True):
    file_name = 'C:/Users/evans/Documents/GPSLink/Polar/Kenneth_Evans_2021-12-04_12-01-33_Walking_Kensington.gpx'
    if prompt:
        file_name = prompt_for_file_name()

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
            n_trkpt = len(gpx.tracks[trk].segments[seg].points)
            print(f'    Number of points: {n_trkpt}')
    return file_name, gpx

def get_data(gpx, use_data_frame=False):
    if use_data_frame:
           # Use DataFrame
            print('Creating DataFrame')
            data = gpx.tracks[0].segments[0].points
            df = pd.DataFrame(columns=['lon', 'lat', 'ele', 'time'])
            for point in data:
                df = df.append({'lon': point.longitude, 'lat' : point.latitude,
                    'ele' : point.elevation, 'time' : point.time}, ignore_index=True)
            lon = df['lon']
            lat = df['lat']
    else:
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
    return lat, lon, ele, time

def plot_track(lat, lon, title='GPX Track'):
    print('Plotting track')
    plt.figure(figsize=(10,6))
    # Is necessary to not have scientific notation and offset
    #plt.ticklabel_format(useOffset=False, style='plain')
    plt.ticklabel_format(useOffset=False)
    plt.plot(lon, lat)
    plt.title(title)
    plt.xlabel('longitude, deg')
    plt.ylabel('latitude, deg')
    plt.show()

def plot_speed(time, speed, avg_speed=None, title='Speed vs Time'):
    print('Plotting speed')
    if(avg_speed):
        avg_speed_array = []
        lenSpeed = len(speed)
        for i in range(lenSpeed):
            avg_speed_array.append(avg_speed)
    # Moving average 1
    moving_avg = []
    window_size = 5
    for i in range(lenSpeed):
        if i == 0:
             window_average = 0
        elif i == 1:
            window_average = speed[0]
        elif i < window_size:
            this_window = speed[0 : i]
            window_average = sum(this_window) / (i + 1)
        else:
            this_window = speed[i - window_size: i]
            window_average = sum(this_window) / window_size
        moving_avg.append(window_average)

    # Moving average 2
    moving_avg2 = []
    window_size2 = 60
    for i in range(lenSpeed):
        if i == 0:
             window_average = 0
        elif i == 1:
            window_average = speed[0]
        elif i < window_size2:
            this_window = speed[0 : i]
            window_average = sum(this_window) / (i + 1)
        else:
            this_window = speed[i - window_size2: i]
            window_average = sum(this_window) / window_size2
        moving_avg2.append(window_average)

    plt.figure(figsize=(10,6))
    # Is necessary to not have scientific notation and offset
    #plt.ticklabel_format(useOffset=False, style='plain')
    plt.ticklabel_format(useOffset=False)
    plt.plot(speed, 'dodgerblue', label='speed')
    plt.plot(moving_avg, 'orangered', label=f'moving_average({window_size})')
    #plt.plot(moving_avg2, 'yellow', label=f'moving_average({window_size2})')
    if avg_speed:
        plt.plot(avg_speed_array, 'orange', label='avg speed')
    plt.title(title)
    plt.xlabel('Trackpoint Index')
    plt.ylabel('Speed, mph')
    plt.legend(loc='upper right', framealpha=0.6)
    plt.tight_layout()
    plt.show()

def get_speed(lat, lon, time):
    MI_PER_M = 0.000621371
    SEC_PER_HR = 3600
    SEC_PER_MIN = 60
    lenData = len(lat)
    dist = []
    speed = []
    total_dist = 0
    total_time = 0
    for i in range(lenData):
        if i == 0:
            speed.append(0)
            continue
        dist_hav = haversine.haversine((lat[i], lon[i]), (lat[i - 1], lon[i - 1]), unit='mi')
        dist.append(dist_hav)
        total_dist = total_dist + dist_hav
        time_delta = (time[i] - time[i - 1]).total_seconds()
        total_time = total_time + time_delta / SEC_PER_MIN
        if time_delta == 0:
            speed.append(0.)
        else:
            speed.append(dist_hav / time_delta * SEC_PER_HR)
        #if i < 100:
        #    print(f'{i=} {time_delta=} {speed[i]=} {time[i]=}')
    return speed, total_dist, total_time

def moving_average2(x, winsize):
    '''Calculates a moving average.
    Uses numpy.mean.

    Parameters
    ----------
    x: array of x values
    winsize: The size of the moving window.
    '''
    n = winsize if len(x) > winsize else len(x)
    val = np.mean(x[-n:])
    return val


def main():
    file_name, gpx = get_gpx_data(prompt=False)
    lat, lon, ele, time = get_data(gpx)
    #plot_track(lat, lon, title=file_name)
    speed, total_dist, total_time = get_speed(lat, lon, time)
    avg_speed = total_dist / total_time * 60
    print(f'{total_dist=:.2f} mi, {total_time=:.1f} min, avg_speed={avg_speed:.2f} mph')
    plot_speed(time, speed, avg_speed, title=f'Speed vs. Trackpoint Index\n{file_name}')

if __name__ == "__main__":
    main()

