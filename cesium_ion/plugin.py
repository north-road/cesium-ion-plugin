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
from qgis.PyQt.QtWidgets import (
    QPushButton,
    QMessageBox
)
from qgis.core import (
    Qgis,
    QgsApplication,
    QgsAuthMethodConfig
)
from qgis.gui import (
    QgsGui,
    QgisInterface,
    QgsMessageBarItem
)

from .core import API_CLIENT
from .gui import (
    CesiumIonDataItemProvider,
    CesiumIonDataItemGuiProvider,
    CesiumIonDropHandler
)


class CesiumIonPlugin(QObject):
    """
    Felt QGIS plugin
    """

    def __init__(self, iface: QgisInterface):
        super().__init__()
        self.iface: QgisInterface = iface

        self.data_item_provider: Optional[CesiumIonDataItemProvider] = None
        self.data_item_gui_provider: Optional[CesiumIonDataItemGuiProvider] = \
            None
        self.drop_handler: Optional[CesiumIonDropHandler] = None

        self._current_message_bar_item: Optional[QgsMessageBarItem] = None

    # qgis plugin interface
    # pylint: disable=missing-function-docstring

    def initGui(self):
        if not self._create_oauth_config():
            return

        self.data_item_provider = CesiumIonDataItemProvider()
        QgsApplication.dataItemProviderRegistry().addProvider(
            self.data_item_provider
        )

        self.data_item_gui_provider = CesiumIonDataItemGuiProvider()
        QgsGui.dataItemGuiProviderRegistry().addProvider(
            self.data_item_gui_provider
        )

        self.drop_handler = CesiumIonDropHandler()
        self.iface.registerCustomDropHandler(self.drop_handler)

    def unload(self):
        if self.data_item_gui_provider and \
                not sip.isdeleted(self.data_item_gui_provider):
            QgsGui.dataItemGuiProviderRegistry().removeProvider(
                self.data_item_gui_provider
            )
        self.data_item_gui_provider = None

        if self.data_item_provider and \
                not sip.isdeleted(self.data_item_provider):
            QgsApplication.dataItemProviderRegistry().removeProvider(
                self.data_item_provider
            )
        self.data_item_provider = None

        self.iface.unregisterCustomDropHandler(self.drop_handler)
        self.drop_handler = None

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

    def _configure_auth(self):
        """
        Walks user through configuring QGIS authentication system
        """
        if (self._current_message_bar_item and
                not sip.isdeleted(self._current_message_bar_item)):
            self.iface.messageBar().popWidget(self._current_message_bar_item)
            self._current_message_bar_item = None

        QMessageBox.information(
            self.iface.mainWindow(),
            self.tr('Configure QGIS Authentication'),
            self.tr('In order to securely store access credentials, '
                    'the Cesium ion plugin requires use of the QGIS '
                    'Authentication database. This has not been setup for '
                    'this QGIS user profile.\n\n'
                    'On the next screen you\'ll be prompted for a master '
                    'password which will be used to secure the QGIS '
                    'Authentication system. Please enter a secure password '
                    'and store this safely!\n\n'
                    '(This password will not be accessible to the Cesium ion '
                    'plugin, and will never be shared with the Cesium ion '
                    'service. Don\'t use the same password as you use for '
                    'ion!)'),
            QMessageBox.Ok
        )

        QgsApplication.authManager().setMasterPassword()
        # remove unwanted message
        for item in self.iface.messageBar().items():
            if item.text().startswith('Retrieving password from your '
                                      'Wallet/KeyRing failed'):
                self.iface.messageBar().popWidget(item)
                break

        self.initGui()

    def _create_oauth_config(self) -> bool:
        """
        Creates the Cesium ion oauth config, if it doesn't already exist.

        Returns True if the oauth config is ready to use
        """
        if not QgsApplication.authManager().masterPasswordHashInDatabase() or \
                not QgsApplication.authManager().setMasterPassword(True):

            message_widget = self.iface.messageBar().createMessage(
                self.tr('Cesium ion'),
                self.tr(
                    'QGIS authentication system not available -- '
                    'please configure')
            )
            details_button = QPushButton(self.tr("Configure"))
            details_button.clicked.connect(self._configure_auth)
            message_widget.layout().addWidget(details_button)
            self._current_message_bar_item = (
                self.iface.messageBar().pushWidget(message_widget,
                                                   Qgis.MessageLevel.Warning,
                                                   0))
            return False

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

        return True
