"""
Cesium ion token class
"""

from dataclasses import dataclass, field
from typing import Optional, Dict, List

from qgis.PyQt.QtCore import (
    Qt,
    QDateTime
)


@dataclass
class Token:
    """
    Represents an ion asset
    """
    id: str
    name: str
    token: str
    scopes: str
    date_added: Optional[QDateTime] = None
    date_modified: Optional[QDateTime] = None
    date_last_used: Optional[QDateTime] = None
    asset_ids: List[int] = field(default_factory=list)
    is_default: Optional[bool] = None

    @staticmethod
    def from_json(json: Dict) -> 'Token':
        """
        Creates an asset from a JSON object
        """
        return Token(
            id=json['id'],
            name=json['name'],
            token=json.get('token'),
            date_added=QDateTime.fromString(
                json['dateAdded'], Qt.DateFormat.ISODate
            ) if 'dateAdded' in json else None,
            date_modified=QDateTime.fromString(
                json['dateModified'], Qt.DateFormat.ISODate
            ) if 'dateModified' in json else None,
            date_last_used=QDateTime.fromString(
                json['dateLastUsed'], Qt.DateFormat.ISODate
            ) if 'dateLastUsed' in json else None,
            asset_ids=json.get('assetIds', []),
            is_default=json.get('isDefault'),
            scopes=json['scopes']
        )
