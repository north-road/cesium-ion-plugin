"""
Cesium ion data browser items
"""
from functools import partial

from qgis.PyQt.QtCore import (
    QCoreApplication
)
from qgis.PyQt.QtWidgets import (
    QAction
)
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

from .gui_utils import GuiUtils
from ..core import (
    Asset,
    AssetType,
    Status,
    API_CLIENT
)


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
        u.uri = self.asset.as_qgis_drop_uri()
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
        return QgsDataProvider.Dir

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
    def add_asset_by_id_interactive():
        """
        Interactively allows users to add an asset by ID to a project
        """
        # pylint: disable=import-outside-toplevel
        from .add_asset_dialog import AddAssetByIdDialog
        # pylint: enable=import-outside-toplevel

        dialog = AddAssetByIdDialog()
        if not dialog.exec_():
            return

        asset = Asset(
            id=dialog.asset_id(),
            name='Unknown',
            type=AssetType.Tiles3D,
            status=Status.Complete
        )
        CesiumIonLayerUtils.add_asset_with_token(
            asset, dialog.token()
        )

    @staticmethod
    def add_asset_with_token(asset: Asset, token: str):
        """
        Adds an asset with the specified token
        """
        ds = asset.as_qgis_data_source(token)
        provider = asset.type.to_qgis_data_provider()
        iface.addTiledSceneLayer(
            ds, asset.name, provider
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

    def tr(self, string, context=''):
        if context == '':
            context = self.__class__.__name__
        return QCoreApplication.translate(context, string)

    def populateContextMenu(self, item, menu, selectedItems, context):
        if isinstance(item, IonAssetItem):
            add_to_project_action = QAction(self.tr('Add Asset to Project…'),
                                            menu)
            add_to_project_action.triggered.connect(
                partial(self._add_asset, item.asset))
            menu.addAction(add_to_project_action)
        elif isinstance(item, IonRootItem):
            add_by_id_action = QAction(self.tr('Add Asset by ID…'),
                                       menu)
            add_by_id_action.triggered.connect(self._add_asset_by_id)
            menu.addAction(add_by_id_action)

    # pylint: enable=missing-docstring,unused-argument

    def _add_asset(self, asset: Asset):
        """
        Adds an asset to the project
        """
        CesiumIonLayerUtils.add_asset_interactive(asset)

    def _add_asset_by_id(self):
        """
        Interactively adds an asset by ID
        """
        CesiumIonLayerUtils.add_asset_by_id_interactive()


class CesiumIonDropHandler(QgsCustomDropHandler):
    """
    Custom drop handler for Cesium ion assets
    """

    # QgsCustomDropHandler interface:

    # pylint: disable=missing-docstring
    def customUriProviderKey(self):
        return 'cesium_ion'

    def handleCustomUriDrop(self, uri):
        asset = Asset.from_qgis_drop_uri(uri.name, uri.uri)

        CesiumIonLayerUtils.add_asset_interactive(asset)

    # pylint: enable=missing-docstring
