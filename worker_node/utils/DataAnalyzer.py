import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from geopy.distance import distance as geodistance
import io

matplotlib.interactive(False)

class DataAnalyzer():
    def __init__(self):
        super().__init__()


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
                descend -= diff
            current_elev = elev
        return min_elev, max_elev, climb, descend

    def plot_power_profile(self, axis, time_data, power_data):
        valid_indices = self.get_valid_indices(time_data, power_data)
        power_data = power_data[valid_indices]
        time_data = time_data[valid_indices]

        if len(valid_indices) == 0:
            axis.text(0.5, 0.5, 'Power Data Unavailable', horizontalalignment='center', \
                      verticalalignment='center', transform=axis.transAxes)
            return axis

        start, stop = time_data[0], time_data[-1]
        time_data = np.array([(t - start) for t in time_data])
        axis.plot(time_data, power_data, color='steelblue', linewidth=1)

        avg_power = self.get_avg_power(power_data, time_data)
        axis.plot([time_data[0], time_data[-1]], [avg_power]*2, '--', color='gray', label='Average Power')

        axis.set_xticks(np.arange(0, int(time_data[-1])+600, 600))
        axis.set_yticks(np.arange(0, int(np.max(power_data)+100), 50))
        axis.set_xlim(time_data[0], time_data[-1])
        axis.set_ylim(0,)
        axis.set_title('Power Profile')
        axis.set_xlabel('Time Elapsed (Seconds)')
        axis.set_ylabel('Power (Watts)')
        axis.legend(loc='upper right')
        axis.grid(alpha=0.2)

        return axis

    def plot_elevation_profile(self, axis, time_data, elevation_data):
        valid_indices = self.get_valid_indices(elevation_data, time_data)
        elevation_data = elevation_data[valid_indices]
        time_data = time_data[valid_indices]

        if len(valid_indices) == 0:
            axis.text(0.5, 0.5, 'Elevation Data Unavailable', horizontalalignment='center', \
                      verticalalignment='center', transform=axis.transAxes)
            return axis

        start, stop = time_data[0], time_data[-1]
        time_data = np.array([(t - start) for t in time_data])
        axis.plot(time_data, elevation_data, color='firebrick', linewidth=2)

        axis.set_xticks(np.arange(0, int(time_data[-1])+600, 600))
        axis.set_xlim(time_data[0], time_data[-1])
        axis.set_title('Elevation Profile')
        axis.set_xlabel('Time Elapsed (Seconds)')
        axis.set_ylabel('Elevation (Meters)')
        axis.grid(alpha=0.2)

        return axis

    def generate_data_visualizations(self, time_data, power_data, elevation_data):
        fig, ax = plt.subplots(2, 1, figsize=(12, 14))

        self.plot_power_profile(ax[0], time_data, power_data)
        self.plot_elevation_profile(ax[1], time_data, elevation_data)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.close(fig)

        return buffer
