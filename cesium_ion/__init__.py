"""
Cesium ion QGIS plugin
"""


def classFactory(iface):
    """
    Creates the plugin
    """
    # pylint: disable=import-outside-toplevel
    from cesium_ion.plugin import CesiumIonPlugin

    return CesiumIonPlugin(iface)
