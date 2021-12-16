''' GPX routines.
Based on https://towardsdatascience.com/how-tracking-apps-analyse-your-gps-data-a-hands-on-tutorial-in-python-756d4db6715d
'''

import numpy as np
import matplotlib.pyplot as plt
import gpxpy

import datetime
from zoneinfo import ZoneInfo
from timezonefinder import TimezoneFinder

#from geopy import distance
#from math import sqrt, floor
import os

import pandas as pd
import haversine

def prompt_for_file_names():
    # Prompt for the file name
    import tkinter as tk
    from tkinter import filedialog
    import ctypes
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
    root = tk.Tk()
    root.withdraw() 
    file_names = []
    # Prompt to open a GPX file
    filetypes = (('GPX files', '*.gpx'),
        ('All files', '*.*'))
    file_names_ret = filedialog.askopenfilenames(title='Open a GPX file', multiple=True,
        filetypes=filetypes)
    for file_name in file_names_ret:
        file_names.append(file_name)
    root.destroy()
    return file_names

def get_files(prompt=True):
    default_file_name = 'C:/Users/evans/Documents/GPSLink/Polar/Kenneth_Evans_2021-12-04_12-01-33_Walking_Kensington.gpx'
    if prompt:
        file_names = prompt_for_file_names()
    else:
        # Use the default
        file_names = []
        file_names.append(default_file_name);
    return file_names

def get_gpx_data(file_name, prompt=True):
    gpx_file = open(file_name, 'r')
    gpx = gpxpy.parse(gpx_file)
    return gpx

def get_gpx_info(gpx):
    n_trk = len(gpx.tracks)
    info = ""
    info += f'Creator: {gpx.creator}\n'
    info += f'Author Name: {gpx.author_name}\n'
    info += f'Number of tracks: {n_trk}\n'
    info += f'Schema Locations:\n'
    schema_locations = gpx.schema_locations
    if schema_locations:
        for loc in schema_locations:
            info += f'    {loc}\n'
    info += f'Namespaces:\n'
    nsmap = gpx.nsmap
    if nsmap:
        for key in nsmap:
            info += f'    {key}: {nsmap[key]}\n'
    for trk in range(n_trk):
        info += f'Track {trk}:\n'
        n_seg = len(gpx.tracks[trk].segments)
        info += f'  Number of segments: {n_seg}\n'
        for seg in range(n_seg):
            info += f'  Segment {seg}:\n'
            n_trkpt = len(gpx.tracks[trk].segments[seg].points)
            info += f'    Number of points: {n_trkpt}\n'
    # remove last \n
    lenInfo = len(info)
    if info[-1] == '\n':
       info = info[0: -2]
    return info

def get_data(gpx):
    '''Currently Only does the first track and first segment'''
    tzf = TimezoneFinder()
    # Use lists for the data not a DataFrame
    lat = []
    lon = []
    ele = []
    time = []
    n_trk = len(gpx.tracks)
    for trk in range(n_trk):
        n_seg = len(gpx.tracks[trk].segments)
        first = True  # Flag to get the timezone for this track
        for seg in range(n_seg):
            points = gpx.tracks[trk].segments[seg].points
            for point in points:
                if(first):
                    # Get the time zone from the first point in first segment
                    tz_name = tzf.timezone_at(lng=point.longitude, lat=point.latitude)
                    first = False
                lat.append(point.latitude)
                lon.append(point.longitude)
                ele.append(point.elevation)
                try:
                    new_time = point.time.astimezone(ZoneInfo(tz_name))
                except:
                    new_time = point.time.astimezone(ZoneInfo('UTC'))
                time.append(new_time)
    return lat, lon, ele, time

def get_track_info(lat, lon, ele, time):
    start = (lat[0], lon[0])
    end = (lat[-1], lon[-1])
    start_time = time[0]
    end_time = time[-1]
    speed, total_dist, total_time = get_speed(lat, lon, time)
    avg_speed = total_dist / total_time * 60
    info = ""
    info += f'start: lat={start[0]} lon={start[1]} time={start_time}\n'
    info += f'end  : lat={end[0]} lon={end[1]} time={end_time}\n'
    info += f'{total_dist=:.2f} mi, {total_time=:.1f} min, avg_speed={avg_speed:.2f} mph'
    return info

def plot_track(lat, lon, title='GPX Track'):
    #print('Plotting track')
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
    #print('Plotting speed')
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
    plt.plot(time, speed, 'dodgerblue', label='speed')
    plt.plot(time, moving_avg, 'orangered', label=f'moving_average({window_size})')
    #plt.plot(time, moving_avg2, 'yellow', label=f'moving_average({window_size2})')
    if avg_speed:
        plt.plot(time, avg_speed_array, 'orange', label='avg speed')
    plt.title(title)
    plt.xlabel('Time (dd hh:mm)')
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

def main():
    # Set prompt to use default filename or prompt with a FileDialog
    prompt = True
    file_names = get_files(prompt=prompt)
    nFiles = len(file_names)
    for file_name in file_names:
        short_name = os.path.basename(file_name)
        print(f'{file_name=}')
        gpx = get_gpx_data(file_name, prompt=prompt)
        # Print gpx info
        gpx_info = get_gpx_info(gpx);
        print(f'GPX Information\n{gpx_info}')
        lat, lon, ele, time = get_data(gpx)
        if len(lat) == 0:
            print('No trackpoints found\n')
            continue
        # Print track info
        track_info = get_track_info(lat, lon, ele, time)
        print(f'Track Information\n{track_info}')
        print()
        #for i in range(10):
        #    print(f'{i} {time[i]=} tz={time[i].tzinfo}')
        #plot_track(lat, lon, title=file_name)
        speed, total_dist, total_time = get_speed(lat, lon, time)
        avg_speed = total_dist / total_time * 60
        plot_speed(time, speed, avg_speed, title=f'Speed vs. Trackpoint Index\n{file_name}')

if __name__ == "__main__":
    main()

