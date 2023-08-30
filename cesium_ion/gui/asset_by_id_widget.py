"""
Asset by ID widget
"""
from typing import Optional

from qgis.PyQt import uic
from qgis.PyQt.QtCore import (
    pyqtSignal
)
from qgis.PyQt.QtWidgets import (
    QWidget
)

from .gui_utils import GuiUtils

WIDGET, _ = uic.loadUiType(GuiUtils.get_ui_file_path('asset_by_id.ui'))


class AssetByIdWidget(QWidget, WIDGET):
    """
    Custom widget for adding assets by ID
    """

    is_valid_changed = pyqtSignal(bool)

    def __init__(self,  # pylint: disable=too-many-statements
                 parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setupUi(self)

        self.edit_asset_id.textChanged.connect(self._validate)
        self.edit_access_token.textChanged.connect(self._validate)

    def _validate(self):
        """
        Validates the current settings
        """
        self.is_valid_changed.emit(self.is_valid())

    def is_valid(self) -> bool:
        """
        Returns True if the settings are valid
        """
        if not self.edit_asset_id.text().strip():
            return False

        if not self.edit_access_token.text().strip():
            return False

        return True

    def asset_id(self) -> str:
        """
        Returns the selected asset ID
        """
        return self.edit_asset_id.text().strip()

    def token(self) -> str:
        """
        Returns the selected token
        """
        return self.edit_access_token.text().strip()
