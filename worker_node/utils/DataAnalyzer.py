import numpy as np
import matplotlib.pyplot as plt
from geopy.distance import distance as geodistance

class DataAnalyzer():
    def __init__(self):
        super().__init__()

    '''
    def cast_data_as_numeric(self, data_dict):
        for data_key in data_dict.keys():
            if data_key == 'time':
                continue
            else:
                try:
                    data_dict[data_key] = data_dict[data_key].astype(float)
                except ValueError:
                    continue

        return data_dict

    def clean_data(self, raw_data):
        # raw_data: [dict(<'data_feature': [values] >)]
        clean_data = []
        for segment_data in raw_data:
            clean_segment_data = {}
            valid_segment_indices = set()

            for data_key in segment_data.keys():
                values = np.array(segment_data[data_key])
                if len(valid_segment_indices) == 0:
                    valid_segment_indices = set(np.where(values != None)[0])
                else:
                    valid_segment_indices = valid_segment_indices.intersection(set(np.where(values != None)[0]))
            valid_segment_indices = sorted(list(valid_segment_indices))

            for data_key in segment_data.keys():
                clean_segment_data[data_key] = np.array(segment_data[data_key])[valid_segment_indices]

            clean_segment_data = self.cast_data_as_numeric(clean_segment_data)
            clean_data.append(clean_segment_data)

        return clean_data
    '''

    def get_valid_indices(self, x1, x2=None):
        x1 = np.array(x1)
        valid_indices = set(np.where(np.isfinite(x1))[0])

        if x2 is not None:
            x2 = np.array(x2)
            valid_indices = valid_indices.intersection(set(np.where(np.isfinite(x2))[0]))

        return sorted(list(valid_indices))


    def get_avg_power(self, power_data, time_data):
        valid_indices = self.get_valid_indices(power_data, time_data)

        if len(valid_indices) == 0:
            return 0

        power_data = power_data[valid_indices]
        time_data = time_data[valid_indices]

        accumulated_power = 0
        for i in range(len(time_data)-1):
            accumulated_power += (power_data[i] * (time_data[i+1] - time_data[i]))
        return accumulated_power / float(self.get_elapsed_time(time_data))


    def get_distance(self, coords):
        valid_indices = self.get_valid_indices(np.array(coords[:,0]).astype(float), np.array(coords[:,1]).astype(float))
        coords = coords[valid_indices]

        dist = 0
        for i in range(len(coords)-1):
            dist += geodistance(coords[i], coords[i+1]).km

        return dist


    def get_elapsed_time(self, time_data):
        valid_indices = self.get_valid_indices(time_data)

        if len(valid_indices) == 0:
            return 0

        time_data = time_data[valid_indices]

        # return elapsed time in seconds
        return time_data[-1] - time_data[0]

    def get_elevation_statistics(self, elevation_data):
        # return min elevation, max elevation, meters climbed, meters descended
        min_elev, max_elev, climb, descend = 0, 0, 0, 0

        valid_indices = self.get_valid_indices(elevation_data)

        if len(valid_indices) == 0:
            return min_elev, max_elev, climb, descend

        elevation_data = elevation_data[valid_indices]

        min_elev, max_elev = np.min(elevation_data), np.max(elevation_data)
        current_elev = elevation_data[0]
        for elev in elevation_data:
            diff = elev - current_elev
            if diff >= 0:
                climb += diff
            else:
                descend += diff
            current_elev = elev
        return min_elev, max_elev, climb, descend

    def generate_power_profile(self, time_data, power_data):
        valid_indices = self.get_valid_indices(power_data, time_data)
        power_data = power_data[valid_indices]
        time_data = time_data[valid_indices]

        fig, ax = plt.subplots(figsize=(12, 6))

        if len(valid_indices) == 0:
            return ax

        start, stop = time_data[0], time_data[-1]
        time_data = np.array([(t - start) for t in time_data])
        ax.plot(time_data, power_data, color='steelblue', linewidth=1)

        avg_power = self.get_avg_power(power_data[valid_indices], time_data[valid_indices])
        ax.plot([time_data[0], time_data[-1]], [avg_power]*2, '--', color='gray', label='Average Power')

        ax.set_xticks(np.arange(0, int(time_data[-1])+600, 600))
        ax.set_yticks(np.arange(0, int(np.max(power_data)+100), 50))
        ax.set_xlim(time_data[0], time_data[-1])
        ax.set_ylim(0,)
        ax.set_title('Power Profile')
        ax.set_xlabel('Time Elapsed (Seconds)')
        ax.set_ylabel('Power (Watts)')
        ax.legend(loc='upper right')
        ax.grid(alpha=0.2)

        return ax

    def generate_elevation_profile(self, time_data, elevation_data):
        valid_indices = self.get_valid_indices(elevation_data, time_data)
        elevation_data = elevation_data[valid_indices]
        time_data = time_data[valid_indices]

        fig, ax = plt.subplots(figsize=(12, 6))

        if len(valid_indices) == 0:
            return ax

        start, stop = time_data[0], time_data[-1]
        time_data = np.array([(t - start) for t in time_data])
        ax.plot(time_data, elevation_data, color='firebrick', linewidth=2)

        ax.set_xticks(np.arange(0, int(time_data[-1])+600, 600))
        ax.set_xlim(time_data[0], time_data[-1])
        ax.set_title('Elevation Profile')
        ax.set_xlabel('Time Elapsed (Seconds)')
        ax.set_ylabel('Elevation (Meters)')
        ax.grid(alpha=0.2)

        return ax
