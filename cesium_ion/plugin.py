"""
Cesium ion QGIS plugin
"""
from typing import Optional

from qgis.PyQt import sip
from qgis.PyQt.QtCore import (
    QObject,
    QCoreApplication
)

from qgis.core import (
    QgsApplication
)
from qgis.gui import (
    QgisInterface
)

from .gui import (
    CesiumIonDataItemProvider
)


class CesiumIonPlugin(QObject):
    """
    Felt QGIS plugin
    """

    def __init__(self, iface: QgisInterface):
        super().__init__()
        self.iface: QgisInterface = iface

        self.data_item_provider: Optional[CesiumIonDataItemProvider] = None


    # qgis plugin interface
    # pylint: disable=missing-function-docstring

    def initGui(self):
        self.data_item_provider = CesiumIonDataItemProvider()
        QgsApplication.dataItemProviderRegistry().addProvider(
            self.data_item_provider
        )

    def unload(self):
        if self.data_item_provider and \
                not sip.isdeleted(self.data_item_provider):
            QgsApplication.dataItemProviderRegistry().removeProvider(
                self.data_item_provider
            )
        self.data_item_provider = None

    # pylint: enable=missing-function-docstring

    @staticmethod
    def tr(message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Cesium ION', message)
