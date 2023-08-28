"""
Cesium ion data browser items
"""

from qgis.core import (
    Qgis,
    QgsDataProvider,
    QgsDataItemProvider,
    QgsDataCollectionItem,
    QgsLayerItem,
    QgsDataItem
)

from .gui_utils import GuiUtils


class IonAssetItem(QgsLayerItem):
    """
    Represents an individual asset on Cesium ion
    """

    def __init__(self,
                 parent: QgsDataItem,
                 name: str,
                 asset_id: str,
                 uri: str):  # NOQA
        super().__init__(
            parent,
            name,
            'ion{}'.format(asset_id),
            uri,
            Qgis.BrowserLayerTypes.TiledScene,
            'cesiumtiles')


class IonRootItem(QgsDataCollectionItem):
    """
    Root item for Cesium ion browser entries
    """

    def __init__(self):
        super().__init__(None, 'Cesium ion', 'cesium_ion', 'cesium_ion')
        self.setCapabilitiesV2(
            Qgis.BrowserItemCapabilities(
                Qgis.BrowserItemCapability.Fertile
            )
        )

        self.setIcon(GuiUtils.get_icon('browser_root.svg'))
        self.populate()

    def createChildren(self):
        res = []
        return res


class CesiumIonDataItemProvider(QgsDataItemProvider):
    """
    Data item provider for Cesium ion items in the QGIS browser
    """

    def __init__(self):
        super().__init__()

    def name(self):
        return 'cesium_ion'

    def dataProviderKey(self):
        return 'cesium_ion'

    def capabilities(self):
        return int(QgsDataProvider.Dir)

    def createDataItem(self, path, parentItem):
        if not path:
            return IonRootItem()

        return None
