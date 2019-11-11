import xml.etree.ElementTree as ET
import re
import numpy as np
from time import strptime

class GPXDataParser():
    def __init__(self, xml_str):
        self.root = root = ET.fromstring(xml_str)
        self.namespace = self.get_namespace()
        if 'gpx' not in self.namespace:
            raise ValueError('No namespace exists in GPX data')


    def get_namespace(self):
        ns_dict = {}
        ns_regex = re.compile(r'http://www\.topografix\.com/GPX/\d+/\d+')
        for i, j in self.root.items():
            if 'schemaLocation' in i:
                candidate_namespaces = self.root.attrib[i]
                namespaces = [url for url in candidate_namespaces.split() if re.match(ns_regex, url)]
        if len(namespaces) > 0:
            ns_dict = {'gpx': namespaces[0]}

        return ns_dict


    def get_segments(self):
        segments = []
        tracks = self.root.findall('gpx:trk', self.namespace)
        for track in tracks:
            for segment in track.findall('gpx:trkseg', self.namespace):
                segments.append(segment)

        return segments


    def format_time_data(self, time_data):
        times = []
        for ts in time_data:
            try:
                t = strptime(ts, '%Y-%m-%dT%H:%M:%SZ')
                times.append(float(t.tm_hour)*3600 + float(t.tm_min)*60 + float(t.tm_sec))
            except (TypeError, ValueError):
                times.append(None)
        return times


    def cast_data_as_numeric(self, data_dict):
        for data_key in data_dict.keys():
            data_dict[data_key] = np.array(data_dict[data_key])
            if data_key == 'time':
                continue
            else:
                try:
                    data_dict[data_key] = data_dict[data_key].astype(float)
                except ValueError:
                    continue

        return data_dict


    def extract_segment_data(self, segment):
        data = {'ele': [], 'time': [], 'power': [], 'coords': []}
        child_data = ['ele', 'time']
        extension_data = ['power']
        for point in segment:
            lat, lon = float(point.attrib['lat']), float(point.attrib['lon'])
            data['coords'].append([lat, lon])
            for child in child_data:
                feature = point.find('gpx:{}'.format(child), self.namespace)
                if feature is not None:
                    try:
                        data[child].append(feature.text)
                    except AttributeError:
                        data[child].append(None)
                else:
                    data[child].append(None)

            extensions = point.find('gpx:extensions', self.namespace)
            if extensions is not None:
                for extended_feature in extension_data:
                    feature = extensions.find('gpx:{}'.format(extended_feature), self.namespace)
                    try:
                        data[extended_feature].append(feature.text)
                    except AttributeError:
                        data[extended_feature].append(None)
            else:
                for extended_feature in extension_data:
                    data[extended_feature].append(None)

        data['time'] = self.format_time_data(data['time'])
        data = self.cast_data_as_numeric(data)

        return data


    def get_ride_data(self):
        data = []
        segments = self.get_segments()
        for segment in segments:
            data.append(self.extract_segment_data(segment))
        return data
