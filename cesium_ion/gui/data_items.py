"""
Cesium ion data browser items
"""

from qgis.core import (
    Qgis,
    QgsDataProvider,
    QgsDataItemProvider,
    QgsDataCollectionItem,
    QgsDataItem
)
from qgis.gui import (
    QgsDataItemGuiProvider
)
from qgis.utils import iface

from ..core import (
    Asset,
    API_CLIENT
)
from .gui_utils import GuiUtils


class IonAssetItem(QgsDataItem):
    """
    Represents an individual asset.py on Cesium ion
    """

    def __init__(self,
                 parent: QgsDataItem,
                 asset: Asset):  # NOQA
        super().__init__(
            Qgis.BrowserItemType.Custom,
            parent,
            asset.name,
            'ion{}'.format(asset.id),
            'cesiumion')
        self.asset = asset
        self.setState(
            Qgis.BrowserItemState.Populated
        )
        self.setIcon(GuiUtils.get_icon('cesium_3d_tile.svg'))

    def hasDragEnabled(self):
        return True


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

    # QgsDataCollectionItem interface

    # pylint: disable=missing-function-docstring
    def createChildren(self):
        assets = API_CLIENT.list_assets_blocking()
        res = []
        for asset in assets:
            res.append(IonAssetItem(self, asset))
        return res
    # pylint: enable=missing-function-docstring


class CesiumIonDataItemProvider(QgsDataItemProvider):
    """
    Data item provider for Cesium ion items in the QGIS browser
    """

    # QgsDataItemProvider interface
    # pylint: disable=missing-function-docstring,unused-argument
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
    # pylint: enable=missing-function-docstring,unused-argument


class CesiumIonDataItemGuiProvider(QgsDataItemGuiProvider):
    """
    Data item GUI provider for Cesium ion items
    """

    def name(self):
        return 'cesium_ion'

    def handleDoubleClick(self, item, context):
        if not isinstance(item, IonAssetItem):
            return False

        from .add_asset_dialog import AddAssetDialog
        dialog = AddAssetDialog()
        if dialog.exec_():
            if dialog.existing_token():
                ds = item.asset.as_qgis_data_source(dialog.existing_token())
                iface.addTiledSceneLayer(
                    ds, item.asset.name, 'cesiumtiles'
                )

        return True
