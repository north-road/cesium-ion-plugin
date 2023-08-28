# -*- coding: utf-8 -*-
"""Cesium ion QGIS plugin

.. note:: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.
"""

__author__ = '(C) 2023 by Nyall Dawson'
__date__ = '28/08/2023'
__copyright__ = 'Copyright 2023, North Road'
# This will get replaced with a git SHA1 when you do a git archive
__revision__ = '$Format:%H$'

from qgis.PyQt.QtCore import (
    QObject,
    QCoreApplication
)

from qgis.gui import (
    QgisInterface
)


class CesiumIonPlugin(QObject):
    """
    Felt QGIS plugin
    """

    def __init__(self, iface: QgisInterface):
        super().__init__()
        self.iface: QgisInterface = iface

    # qgis plugin interface
    # pylint: disable=missing-function-docstring

    def initGui(self):
        pass

    def unload(self):
        pass

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
