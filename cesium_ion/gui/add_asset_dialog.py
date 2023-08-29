"""
Add asset dialog
"""
from typing import Optional

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import (
    QDialog,
    QWidget,
    QVBoxLayout,
    QDialogButtonBox
)

from qgis.gui import (
    QgsGui
)

from .select_token_widget import SelectTokenWidget


class AddAssetDialog(QDialog):

    def __init__(self, parent: Optional[QWidget]=None):
        super().__init__(parent)

        self.setObjectName('AddAssetDialog')
        QgsGui.enableAutoGeometryRestore(self)

        self.setWindowTitle(self.tr('Select Cesium ion Token'))

        vl = QVBoxLayout()
        self.select_token_widget = SelectTokenWidget()
        vl.addWidget(self.select_token_widget)

        self.button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        vl.addWidget(self.button_box)

        self.setLayout(vl)

        self.select_token_widget.is_valid_changed.connect(self._set_valid)
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(
            self.select_token_widget.is_valid()
        )

    def _set_valid(self, is_valid: bool):
        self.button_box.button(QDialogButtonBox.Ok).setEnabled(
            is_valid
        )

    def existing_token(self) -> Optional[str]:
        """
        Returns the selected existing token
        """
        return self.select_token_widget.existing_token()

    def new_token_name(self) -> Optional[str]:
        """
        Returns the name for the new token
        """
        return self.select_token_widget.new_token_name()
