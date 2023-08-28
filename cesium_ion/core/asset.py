"""
Cesium ion asset class
"""

from dataclasses import dataclass
from typing import Optional, Dict

from qgis.PyQt.QtCore import (
    Qt,
    QDateTime
)

from .enums import (
    AssetType,
    Status
)


@dataclass
class Asset:
    """
    Represents an ion asset
    """
    id: str
    name: str
    type: AssetType
    status: Status
    description: Optional[str] = None
    attribution: Optional[str] = None
    bytes: Optional[int] = None
    date_added: Optional[QDateTime] = None
    percent_complete: Optional[int] = None
    archivable: Optional[bool] = None
    exportable: Optional[bool] = None

    @staticmethod
    def from_json(json: Dict) -> 'Asset':
        """
        Creates an asset from a JSON object
        """
        return Asset(
            id=json['id'],
            name=json['name'],
            description=json.get('description'),
            attribution=json.get('attribution'),
            type=AssetType.from_string(json['type']),
            bytes=json.get('bytes'),
            date_added=QDateTime.fromString(
                json['dateAdded'], Qt.DateFormat.ISODate
            ) if 'dateAdded' in json else None,
            status=Status.from_string(json['status']),
            percent_complete=json.get('percentComplete'),
            archivable=json.get('archivable'),
            exportable=json.get('exportable')
        )

    def as_qgis_data_source(self) -> str:
        """
        Returns a QGIS data source string representing a connection
        to the asset
        """
        # pylint: disable=import-outside-toplevel
        from .api_client import CesiumIonApiClient
        # pylint: enable=import-outside-toplevel
        return 'ion://?assetId={}&authcfg={}'.format(
            self.id, CesiumIonApiClient.OAUTH_ID
        )
