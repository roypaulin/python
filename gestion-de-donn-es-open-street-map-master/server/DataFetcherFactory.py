
from HighwayDataFetcher import HighwayDataFetcher
from BuildingDataFetcher import BuildingDataFetcher
from WaterwayDataFetcher import WaterwayDataFetcher

class DataFetcherFactory:
    switcher = {
        'highway': HighwayDataFetcher,
        'building': BuildingDataFetcher,
        'waterway': WaterwayDataFetcher,
    }

    @staticmethod
    def create(name, bbox, srid):
        return DataFetcherFactory.switcher.get(name)(bbox, srid)
    
    @staticmethod
    def getAllowedLayers():
        return list(DataFetcherFactory.switcher.keys())
