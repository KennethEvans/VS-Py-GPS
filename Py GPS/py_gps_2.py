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
            print(f'    Number of track points: {n_trkpt}')
    return file_name, gpx

def get_data(gpx):
        # Use DataFrame
        print('Creating DataFrame')
        data = gpx.tracks[0].segments[0].points
        df = pd.DataFrame(columns=['lon', 'lat', 'ele', 'time'])
        for point in data:
            df = df.append({'lon': point.longitude, 'lat' : point.latitude,
                'ele' : point.elevation, 'time' : point.time}, ignore_index=True)
        return df

def plot_track(df, title='GPX Track'):
    print('Plotting track')
    plt.figure(figsize=(10,6))
    # Is necessary to not have scientific notation and offset
    #plt.ticklabel_format(useOffset=False, style='plain')
    plt.ticklabel_format(useOffset=False)
    plt.plot(df['lon'], df['lat'])
    plt.title(title)
    plt.xlabel('longitude, deg')
    plt.ylabel('latitude, deg')
    plt.show()

def plot_speed(speed, time, title='Speed vs Time'):
    print('Plotting speed')
    plt.figure(figsize=(10,6))
    # Is necessary to not have scientific notation and offset
    #plt.ticklabel_format(useOffset=False, style='plain')
    plt.ticklabel_format(useOffset=False)
    plt.plot_date(time, speed)
    plt.title(title)
    plt.xlabel('time')
    plt.ylabel('speed, mph')
    plt.show()

def get_speed(data, df):
    KM_PER_M = .001
    MI_PER_M = 0.000621371
    print('Getting speed')
    time_dif = [0]
    dist_hav_no_alt = [0]
    speed = [0]
    for index in range(len(data)):
        if index == 0:
            pass
        else:
            start = data[index - 1]
            stop = data[index]
            distance_hav_2d = haversine.haversine((start.latitude, start.longitude),
                (stop.latitude, stop.longitude)) / MI_PER_M
            dist_hav_no_alt.append(distance_hav_2d)
            time_delta = (stop.time - start.time).total_seconds()
            time_dif.append(time_delta)
            if time_delta == 0:
                cur_speed = 0
            else:
                cur_speed = distance_hav_2d / time_delta
            speed.append(cur_speed)
    df['dist_hav_2d'] = dist_hav_no_alt
    df['time_dif'] = time_dif
    df['speed'] = speed
    print('Haversine 2D : ', dist_hav_no_alt[-1])
    print('Total Time : ', floor(sum(time_dif) / 60),' min ', int(sum(time_dif) % 60),' sec ')

def plot_speed(df, title='Speed'):
        print('Plotting speed')
        plt.figure(figsize=(10,6))
        plt.title(title)
        plt.ylabel('Speed, mph')
        plt.plot(df['speed'])
        plt.show()

def main():
    file_name, gpx = get_gpx_data(prompt=False)
    data = gpx.tracks[0].segments[0].points
    df = get_data(gpx)
    #plot_track(df, title=file_name)
    speed = get_speed(data, df)
    plot_speed(df, title=file_name)
    #print(f'{len(speed)=} {len(time)=}')
    #for i in range(10):
    #    print(speed[i], time[i])
    #plot_speed(time, speed)
if __name__ == "__main__":
    main()


