"""
Cesium ion data browser items
"""

from qgis.core import (
    Qgis,
    QgsDataProvider,
    QgsDataItemProvider,
    QgsDataCollectionItem,
    QgsDataItem,
    QgsMimeDataUtils
)
from qgis.gui import (
    QgsDataItemGuiProvider,
    QgsCustomDropHandler
)
from qgis.utils import iface

from ..core import (
    Asset,
    AssetType,
    Status,
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
            'cesium_ion')
        self.asset = asset
        self.setState(
            Qgis.BrowserItemState.Populated
        )
        self.setIcon(GuiUtils.get_icon('cesium_3d_tile.svg'))

    # QgsDataItem interface:

    # pylint: disable=missing-docstring
    def hasDragEnabled(self):
        return True

    def mimeUri(self):
        u = QgsMimeDataUtils.Uri()
        u.layerType = "custom"
        u.providerKey = "cesium_ion"
        u.name = self.asset.name
        u.uri = str(self.asset.id)
        return u

    def mimeUris(self):  # pylint: disable=missing-docstring
        return [self.mimeUri()]

    # pylint: enable=missing-docstring


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


class CesiumIonLayerUtils:
    """
    Utilities for working with cesium ion QGIS map layers
    """

    @staticmethod
    def add_asset_interactive(asset: Asset):
        """
        Interactively allows users to add an asset to a project
        """
        # pylint: disable=import-outside-toplevel
        from .add_asset_dialog import AddAssetDialog
        # pylint: enable=import-outside-toplevel

        dialog = AddAssetDialog()
        if not dialog.exec_():
            return

        if dialog.existing_token():
            CesiumIonLayerUtils.add_asset_with_token(
                asset, dialog.existing_token()
            )
        else:
            new_token = API_CLIENT.create_token(
                dialog.new_token_name(),
                scopes=['assets:list', 'assets:read'],
                asset_ids=[int(asset.id)]
            )
            if new_token:
                CesiumIonLayerUtils.add_asset_with_token(
                    asset, new_token.token
                )

    @staticmethod
    def add_asset_with_token(asset: Asset, token: str):
        """
        Adds an asset with the specified token
        """
        ds = asset.as_qgis_data_source(token)
        iface.addTiledSceneLayer(
            ds, asset.name, 'cesiumtiles'
        )


class CesiumIonDataItemGuiProvider(QgsDataItemGuiProvider):
    """
    Data item GUI provider for Cesium ion items
    """

    # QgsDataItemGuiProvider interface:

    # pylint: disable=missing-docstring,unused-argument
    def name(self):
        return 'cesium_ion'

    def handleDoubleClick(self, item, context):
        if not isinstance(item, IonAssetItem):
            return False

        CesiumIonLayerUtils.add_asset_interactive(item.asset)
        return True

    # pylint: enable=missing-docstring,unused-argument


class CesiumIonDropHandler(QgsCustomDropHandler):
    """
    Custom drop handler for Cesium ion assets
    """

    # QgsCustomDropHandler interface:

    # pylint: disable=missing-docstring
    def customUriProviderKey(self):
        return 'cesium_ion'

    def handleCustomUriDrop(self, uri):
        asset = Asset(
            id=uri.uri,
            name=uri.name,
            type=AssetType.Tiles3D,
            status=Status.Complete
        )

        CesiumIonLayerUtils.add_asset_interactive(asset)

    # pylint: enable=missing-docstring
