import numpy as np

class DataAnalyzer():
    def __init__(self):
        super().__init__()

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


    def get_avg_power(self, power_data, time_data):
        accumulated_power = 0
        for i in range(len(time_data)-1):
            accumulated_power += (power_data[i] * (time_data[i+1] - time_data[i]))
        return accumulated_power / float(self.get_elapsed_time(time_data))


    def get_normalized_power(self, power_data, time_data):
        pass


    def get_elapsed_time(self, time_data):
        # return elapsed time in seconds
        return time_data[-1] - time_data[0]

    def get_elevation_statistics(self, elevation_data):
        # return min elevation, max elevation, meters climbed, meters descended
        min_elev, max_elev, climb, descend = 0, 0, 0, 0
        if len(elevation_data) > 0:
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

    def generate_power_profile(self):
        pass

    def generate_elevation_profile(self):
        pass
