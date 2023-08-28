"""
Cesium ion plugin enums
"""

from enum import Enum, auto


class AssetType(Enum):
    """
    Asset types
    """
    Tiles3D = auto()
    GLTF = auto()
    Imagery = auto()
    Terrain = auto()
    KML = auto()
    CZML = auto()
    GeoJSON = auto()

    @staticmethod
    def from_string(string: str) -> 'AssetType':
        """
        Returns an asset type from a string value
        """
        return {
            '3DTILES': AssetType.Tiles3D,
            'GLTF': AssetType.GLTF,
            'IMAGERY': AssetType.Imagery,
            'TERRAIN': AssetType.Terrain,
            'KML': AssetType.KML,
            'CZML': AssetType.CZML,
            'GEOJSON': AssetType.GeoJSON
        }[string.upper()]


class Status(Enum):
    """
    Asset status
    """
    AwaitingFiles = auto()
    NotStarted = auto()
    InProgress = auto()
    Complete = auto()
    DataError = auto()
    Error = auto()

    @staticmethod
    def from_string(string: str) -> 'Status':
        """
        Returns a status from a string value
        """
        return {
            'AWAITING_FILES': Status.AwaitingFiles,
            'NOT_STARTED': Status.NotStarted,
            'IN_PROGRESS': Status.InProgress,
            'COMPLETE': Status.Complete,
            'DATA_ERROR': Status.DataError,
            'ERROR': Status.Error
        }[string.upper()]
