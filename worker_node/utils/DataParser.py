import xml.etree.ElementTree as ET
import re
import numpy as np

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


    def extract_segment_data(self, segment):
        data = {'ele': [], 'time': [], 'power': []}
        child_data = ['ele', 'time']
        extension_data = ['power']
        for point in segment:
            for child in child_data:
                feature = point.find('gpx:{}'.format(child), self.namespace)
                if feature is not None:
                    try:
                        data[child].append(feature.text)
                    except AttributeError:
                        data[child].append(None)

            extensions = point.find('gpx:extensions', self.namespace)
            if extensions is not None:
                for extended_feature in extension_data:
                    feature = extensions.find('gpx:{}'.format(extended_feature), self.namespace)
                    try:
                        data[extended_feature].append(feature.text)
                    except AttributeError:
                        data[extended_feature].append(None)

        return data


    def get_ride_data(self):
        data = []
        segments = self.get_segments()
        for segment in segments:
            data.append(self.extract_segment_data(segment))
        return data
