"""
Select token widget
"""
from typing import Optional

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    pyqtSignal
)
from qgis.PyQt.QtWidgets import (
    QWidget
)

from qgis.core import (
    QgsNetworkAccessManager
)

from .gui_utils import GuiUtils
from ..core import API_CLIENT

WIDGET, _ = uic.loadUiType(GuiUtils.get_ui_file_path('select_token.ui'))


class SelectTokenWidget(QWidget, WIDGET):
    """
    Custom widget for selecting access tokens
    """

    is_valid_changed = pyqtSignal(bool)

    def __init__(self,  # pylint: disable=too-many-statements
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setupUi(self)

        self.radio_existing.setChecked(True)
        self.widget_new.setEnabled(False)
        self.widget_existing.setEnabled(True)
        self.widget_manual.setEnabled(False)

        self.radio_new.toggled.connect(self.widget_new.setEnabled)
        self.radio_existing.toggled.connect(self.widget_existing.setEnabled)
        self.radio_manual.toggled.connect(self.widget_manual.setEnabled)

        self.radio_new.toggled.connect(self._validate)
        self.radio_existing.toggled.connect(self._validate)
        self.radio_manual.toggled.connect(self._validate)
        self.edit_new_token_name.textChanged.connect(self._validate)
        self.combo_existing.currentIndexChanged.connect(self._validate)
        self.edit_manual.textChanged.connect(self._validate)

        req = API_CLIENT.list_tokens_request()
        self._list_tokens_reply = QgsNetworkAccessManager.instance().get(req)
        self._list_tokens_reply.finished.connect(self._reply_finished)

    def _reply_finished(self):
        """
        Called when the list tokens reply is finished
        """
        tokens = API_CLIENT.parse_list_tokens_reply(self._list_tokens_reply)
        for token in tokens:
            self.combo_existing.addItem(token.name, token.token)

        if not tokens:
            self.radio_existing.setEnabled(False)
            if self.radio_existing.isChecked():
                self.radio_new.setChecked(True)

    def _validate(self):
        """
        Validates the current settings
        """
        self.is_valid_changed.emit(self.is_valid())

    def is_valid(self) -> bool:
        """
        Returns True if the settings are valid
        """
        if self.radio_new.isChecked():
            return bool(self.edit_new_token_name.text())

        if self.radio_existing.isChecked():
            return bool(self.combo_existing.currentData())

        if self.radio_manual.isChecked():
            return bool(self.edit_manual.text())

        return False

    def existing_token(self) -> Optional[str]:
        """
        Returns the selected existing token
        """
        if self.radio_existing.isChecked():
            return self.combo_existing.currentData()

        if self.radio_manual.isChecked():
            return self.edit_manual.text()

        return None

    def new_token_name(self) -> Optional[str]:
        """
        Returns the name for the new token
        """
        if self.radio_new.isChecked():
            return self.edit_new_token_name.text()

        return None
