''' GPX routines.
Based on https://towardsdatascience.com/how-tracking-apps-analyse-your-gps-data-a-hands-on-tutorial-in-python-756d4db6715d
'''

import numpy as np
import matplotlib.pyplot as plt
import gpxpy

import datetime
from zoneinfo import ZoneInfo
from timezonefinder import TimezoneFinder

import xml.etree.ElementTree as ET

#from geopy import distance
#from math import sqrt, floor
import os

import pandas as pd

import speed as s

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

def get_gpx(file_name, reparse=True):
    '''Parses the file and returns a gpx object. GpxPy doesn't handle the case
where the default namespace is not GPX/1/1. This is overcome by parsing the file
with xml.etree.ElementTree and specifying the default namespace to be GPX/1/1,
then passing the xml str to gpxpy.parse(). This step is not taken and the file
is read directly if reparse=False.
    
        Parameters
        ----------
        file_name : str
            Full path to the GPX file.
            default: None
        reparse : boolean
            reparse : Whether to reparse the file to set the default namespace
                      or not.
            default : True
    
        Returns
        ------
        return : gpxpy.gpx.GPX()
            The GpxPy gpx object
    '''
    if reparse:
        # Ensure GPX/1/1 is the default namespace
        ET.register_namespace('', "http://www.topografix.com/GPX/1/1")
        tree = ET.parse(file_name)
        root = tree.getroot();
        xml = ET.tostring(root, encoding='unicode');
        # Parse the xml string
        gpx = gpxpy.parse(xml)
    else:
        gpx_file = open(file_name, 'r')
        gpx = gpxpy.parse(gpx_file)
        gpx_file.close();
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

def get_gpx_data(gpx):
    '''Currently Only does the first track and first segment'''
    tzf = TimezoneFinder()
    # Use lists for the data not a DataFrame
    lat = []
    lon = []
    ele = []
    hr = []
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
                # Get HR
                hr_val = 0
                extensions = point.extensions
                found = False
                for extension in extensions:
                    if not found:
                        # Find all children
                        elems = extension.findall('.//')
                        for elem in elems:
                            if elem.tag.endswith('}hr'):
                                hr_val = int(elem.text)
                                found = True
                                break
                    else:
                        break
                hr.append(hr_val)
                # Get time
                try:
                    new_time = point.time.astimezone(ZoneInfo(tz_name))
                except:
                    new_time = point.time.astimezone(ZoneInfo('UTC'))
                time.append(new_time)
    return lat, lon, ele, hr, time

def get_track_info(lat, lon, ele, time):
    start = (lat[0], lon[0])
    end = (lat[-1], lon[-1])
    start_time = time[0]
    end_time = time[-1]
    speed, total_dist, total_time, avg_speed = s.get_speed(lat, lon, time)
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

def plot_speed_hr(time, speed, hr, avg_speed=None, max_speed=5.0, title='Speed and Heart Rate vs Time'):
    '''Plots speed and HR. Also plots avg_speed if given.'''
    if(avg_speed):
        avg_speed_array = []
        lenSpeed = len(speed)
        for i in range(lenSpeed):
            avg_speed_array.append(avg_speed)
    fig = plt.figure(figsize=(10,6))
    plt.ticklabel_format(useOffset=False)
    plt.plot(time, speed, 'dodgerblue', label='speed')
    if avg_speed:
        plt.plot(time, avg_speed_array, 'mediumblue', label=f'avg speed ({avg_speed:.1f} mph)')
    plt.title(title)
    plt.xlabel('Time (dd hh:mm)')
    plt.ylabel('Speed, mph')
    plt.ylim(0, max_speed)
    # HR
    max_hr = max(hr)
    if max_hr != 0:
        ax2 = plt.gca().twinx()
        ax2.plot(time, hr, 'red', label='hr')
        ax2.set_ylabel('HR, bpm');
        ax2.set_ylim(0, round(max_hr + 10))
    # Manually set figure legend (owing to two axes)
    ax = plt.gca()
    fig.legend(loc='lower left', framealpha=0.6, bbox_to_anchor=(0,0),
              bbox_transform=ax.transAxes)
    plt.tight_layout()
    plt.show()

def plot_speed_hr_1(time, speed, hr, avg_speed=None, max_speed=5.0, title='Speed vs Time'):
    '''Plots speed and HR. Calculates moving averages for speed.
    Also plots avg_speed if given.'''
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

    fig = plt.figure(figsize=(10,6))
    plt.ticklabel_format(useOffset=False)
    plt.plot(time, speed, 'lightskyblue', label='speed')
    plt.plot(time, moving_avg, 'dodgerblue', label=f'moving_average({window_size})')
    #plt.plot(time, moving_avg2, 'yellow', label=f'moving_average({window_size2})')
    if avg_speed:
        plt.plot(time, avg_speed_array, 'mediumblue', label=f'avg speed ({avg_speed:.1f} mph)')
    plt.title(title)
    plt.xlabel('Time (dd hh:mm)')
    plt.ylabel('Speed, mph')
    plt.ylim(0, max_speed)
    # HR
    max_hr = max(hr)
    if max_hr != 0:
        ax2 = plt.gca().twinx()
        ax2.plot(time, hr, 'red', label='hr')
        ax2.set_ylabel('HR, bpm');
        ax2.set_ylim(0, round(max_hr + 10))
    # Manually set figure legend (owing to two axes)
    ax = plt.gca()
    fig.legend(loc='lower left', framealpha=0.6, bbox_to_anchor=(0,0),
              bbox_transform=ax.transAxes)
    plt.tight_layout()
    plt.show()

def main():
    # Set prompt to use default filename or prompt with a FileDialog
    prompt = True
    file_names = get_files(prompt=prompt)
    nFiles = len(file_names)
    for file_name in file_names:
        short_name = os.path.basename(file_name)
        print(f'{file_name=}')
        gpx = get_gpx(file_name)
        # Print gpx info
        gpx_info = get_gpx_info(gpx);
        print(f'GPX Information\n{gpx_info}')
        lat, lon, ele, hr, time = get_gpx_data(gpx)
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
        speed, total_dist, total_time, avg_speed = s.get_speed(lat, lon, time)
        speed_proc = s.process_speed(time, speed)
        if False:
            s.plot_speed(time, speed, speed_proc, avg_speed,
                title=f'Speed\n{file_name}')
        plot_speed_hr(time, speed_proc, hr, avg_speed,
                title=f'Speed and Heart Rate\n{file_name}')

if __name__ == "__main__":
    main()

