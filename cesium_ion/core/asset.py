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

    @staticmethod
    def from_qgis_drop_uri(name, uri):
        asset_id, asset_type_str = uri.split("\n")
        asset_type = AssetType.Tiles3D if asset_type_str == '3DTILES' else 'TERRAIN'
        return Asset(
            id=asset_id,
            name=name,
            type=asset_type,
            status=Status.Complete
        )

    def as_qgis_drop_uri(self) -> str:
        type_str = '3DTILES' if self.type == AssetType.Tiles3D else 'TERRAIN'
        return str(self.id) + "\n" + type_str

    def as_qgis_data_source(self, access_token: Optional[str] = None) -> str:
        """
        Returns a QGIS data source string representing a connection
        to the asset
        """
        if access_token:
            return 'ion://?assetId={}&accessToken={}'.format(
                self.id, access_token
            )

        # pylint: disable=import-outside-toplevel
        from .api_client import CesiumIonApiClient
        # pylint: enable=import-outside-toplevel
        return 'ion://?assetId={}&authcfg={}'.format(
            self.id, CesiumIonApiClient.OAUTH_ID
        )
