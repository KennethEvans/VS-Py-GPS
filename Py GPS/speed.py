import numpy as np
import matplotlib.pyplot as plt
from scipy.fft import fft, fftfreq
from scipy.signal import butter, lfilter, freqz
import haversine

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def filter_butter_lowpass(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = lfilter(b, a, data)
    return y

def plot_fft(data, fs, title = 'FFT', filename=None):
    '''Plots the FFT of the given data.'''
    if filename:
      title = f"{title}\n{filename}"
    n = len(data)
    t = 1 / fs
    yf = fft(data)
    xf = fftfreq(n, t)[:n // 2]
    plt.figure(figsize=(10,6))
    plt.plot(xf, 2.0 / n * np.abs(yf[0:n // 2]))
    plt.grid()
    plt.title(title)
    plt.xlabel('frequency')
    plt.ylabel('fft')
    plt.show()

def get_speed(lat, lon, time):
    '''Gets the speed, total distance, and total time from the lat, lon, and time.'''
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
        avg_speed = total_dist / total_time * 60
    return speed, total_dist, total_time, avg_speed

def write_speed_file(speed, file):
    with open(file, 'w') as f:
        for val in speed:
            f.write(f'{float(val):.6}')
            f.write('\n')

def process_speed(time, speed):
    lenSpeed = len(speed)
    if False:
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
    if True:
        # Butterworth
        order = 6
        fs = 1  
        cutoff = .04
        b, a = butter_lowpass(cutoff, fs, order)
        val = filter_butter_lowpass(speed, cutoff, fs, order)
    return val

def plot_speed(time, speed, processed_speed, avg_speed=None, max_speed=5.0, title='Speed vs Time'):
    lenSpeed = len(speed)
    plt.figure(figsize=(10,6))
    plt.plot(time, speed, 'lightskyblue', label='Original')
    plt.plot(time, processed_speed, 'dodgerblue', linewidth=2, label='Filtered')
    if avg_speed:
        avg_speed_array = []
        for i in range(lenSpeed):
            avg_speed_array.append(avg_speed)
        plt.plot(time, avg_speed_array, 'mediumblue', label=f'avg speed ({avg_speed:.1f} mph)')
    plt.xlabel('Time (dd hh:mm)')
    plt.ylabel('Speed, mph')
    plt.title(title)
    plt.legend()
    plt.tight_layout()
    plt.show()



