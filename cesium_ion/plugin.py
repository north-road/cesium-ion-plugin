"""
Cesium ion QGIS plugin
"""
import os
from typing import Optional

from qgis.PyQt import sip
from qgis.PyQt.QtCore import (
    QObject,
    QCoreApplication
)
from qgis.PyQt.QtWidgets import QPushButton
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsAuthMethodConfig
)
from qgis.gui import (
    QgisInterface
)

from .core import API_CLIENT
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
        self._create_oauth_config()

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

    def _create_oauth_config(self):
        """
        Creates the Cesium ion oauth config, if it doesn't already exist
        """
        if not QgsApplication.authManager().masterPasswordHashInDatabase() or \
                not QgsApplication.authManager().setMasterPassword(True):
            def show_options(_):
                self.iface.showOptionsDialog(
                    self.iface.mainWindow(), 'mOptionsPageAuth')

            message_widget = self.iface.messageBar().createMessage(
                self.tr('Cesium ion'),
                self.tr(
                    'QGIS authentication system not available -- please configure and retry')
            )
            details_button = QPushButton(self.tr("Configure"))
            details_button.clicked.connect(show_options)
            message_widget.layout().addWidget(details_button)
            self.iface.messageBar().pushWidget(message_widget,
                                               Qgis.MessageLevel.Warning, 0)
            return

        config = QgsAuthMethodConfig(method='OAuth2')
        config.setName('Cesium ion')
        config.setId(API_CLIENT.OAUTH_ID)

        config_json_path = os.path.join(
            os.path.dirname(__file__),
            'resources',
            'auth_cfg.json')

        with open(config_json_path, 'rt', encoding='utf8') as config_json_file:
            config_json = config_json_file.read()

        config.setConfig('oauth2config', config_json)

        if API_CLIENT.OAUTH_ID in QgsApplication.authManager().configIds():
            QgsApplication.authManager().updateAuthenticationConfig(config)
        else:
            QgsApplication.authManager().storeAuthenticationConfig(config)
