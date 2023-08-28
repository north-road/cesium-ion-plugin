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


def classFactory(iface):
    """
    Creates the plugin
    """
    # pylint: disable=import-outside-toplevel
    from cesium_ion.plugin import CesiumIonPlugin

    return CesiumIonPlugin(iface)
