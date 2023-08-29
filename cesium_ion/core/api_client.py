"""
Cesium ion API client
"""

import json
from typing import (
    Dict,
    Optional,
    List
)

from qgis.PyQt.QtCore import (
    QUrl,
    QUrlQuery,
    QObject,
    pyqtSignal
)
from qgis.PyQt.QtNetwork import (
    QNetworkRequest,
    QNetworkReply
)
from qgis.core import (
    QgsApplication,
    QgsBlockingNetworkRequest
)

from .asset import Asset
from .meta import PLUGIN_METADATA_PARSER
from .token import Token


class CesiumIonApiClient(QObject):
    """
    Client for the Cesium ion REST API
    """

    URL = 'https://api.cesium.com'
    LIST_ASSETS_ENDPOINT = '/v1/assets'
    LIST_TOKENS_ENDPOINT = '/v2/tokens'
    CREATE_TOKEN_ENDPOINT = '/v2/tokens'
    OAUTH_ID = 'cesiion'

    error_occurred = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        # default headers to add to all requests
        self.headers = {
            'accept': 'application/json',
            'x-qgis-plugin-version': PLUGIN_METADATA_PARSER.get_version()
        }

    @staticmethod
    def build_url(endpoint: str) -> QUrl:
        """
        Returns the full url of the specified endpoint
        """
        return QUrl(CesiumIonApiClient.URL + endpoint)

    @staticmethod
    def _to_url_query(parameters: Dict[str, object]) -> QUrlQuery:
        """
        Converts query parameters as a dictionary to a URL query
        """
        query = QUrlQuery()
        for name, value in parameters.items():
            if isinstance(value, (list, tuple)):
                for v in value:
                    query.addQueryItem(name, str(v))
            else:
                query.addQueryItem(name, str(value))
        return query

    def _build_request(self, endpoint: str, headers=None, params=None) \
            -> QNetworkRequest:
        """
        Builds a network request
        """
        url = self.build_url(endpoint)

        if params:
            url.setQuery(CesiumIonApiClient._to_url_query(params))

        network_request = QNetworkRequest(url)

        combined_headers = self.headers
        if headers:
            combined_headers.update(headers)

        for header, value in combined_headers.items():
            network_request.setRawHeader(header.encode(), value.encode())

        return network_request

    def list_assets_request(self,
                            page: Optional[int] = None,
                            filter_string: Optional[str] = None) \
            -> QNetworkRequest:
        """
        List assets asynchronously
        """
        params = {}
        if page is not None:
            params['page'] = page
        if filter_string:
            params['search'] = filter_string

        params['status'] = 'COMPLETE'
        params['type'] = '3DTILES'

        request = self._build_request(
            self.LIST_ASSETS_ENDPOINT,
            params=params
        )
        return request

    def list_assets_blocking(self,
                             page: Optional[int] = None,
                             filter_string: Optional[str] = None
                             ) -> List[Asset]:
        """
        Parse a list assets reply and return as a list of Asset objects
        """
        req = self.list_assets_request(page, filter_string)
        blocking_request = QgsBlockingNetworkRequest()
        blocking_request.setAuthCfg(API_CLIENT.OAUTH_ID)

        res = blocking_request.get(req)
        if res != QgsBlockingNetworkRequest.NoError:
            self.error_occurred.emit(blocking_request.errorMessage())
            return []

        reply = blocking_request.reply()
        if reply.error() == QNetworkReply.OperationCanceledError:
            return []

        if reply.error() != QNetworkReply.NoError:
            self.error_occurred.emit(reply.errorString())
            return []

        assets_json = json.loads(reply.content().data().decode())['items']
        return [Asset.from_json(asset) for asset in assets_json]

    def list_tokens_request(self,
                            page: Optional[int] = None,
                            filter_string: Optional[str] = None) \
            -> QNetworkRequest:
        """
        Creates a list tokens request
        """
        params = {}
        if page is not None:
            params['page'] = page
        if filter_string:
            params['search'] = filter_string

        request = self._build_request(
            self.LIST_TOKENS_ENDPOINT,
            params=params
        )
        QgsApplication.authManager().updateNetworkRequest(
            request, API_CLIENT.OAUTH_ID
        )
        return request

    def parse_list_tokens_reply(self,
                                reply: QNetworkReply
                                ) -> List[Token]:
        """
        Parses a list tokens reply and returns a list of tokens
        """
        if reply.error() != QNetworkReply.NoError:
            self.error_occurred.emit(reply.errorString())
            return []

        if reply.error() == QNetworkReply.OperationCanceledError:
            return []

        reply_data = reply.readAll()
        tokens_json = json.loads(reply_data.data().decode())['items']
        return [Token.from_json(token) for token in tokens_json]

    def create_token(self, token_name: str,
                     scopes: List[str],
                     asset_ids: Optional[List[int]] = None) -> Optional[Token]:
        """
        Creates a new token
        """
        params = {'name': token_name,
                  'scopes': scopes}
        if asset_ids:
            params['assetIds'] = asset_ids

        request = self._build_request(
            self.CREATE_TOKEN_ENDPOINT,
            {'Content-Type': 'application/json'}
        )

        blocking_request = QgsBlockingNetworkRequest()
        blocking_request.setAuthCfg(API_CLIENT.OAUTH_ID)

        res = blocking_request.post(request, json.dumps(params).encode())
        if res != QgsBlockingNetworkRequest.NoError:
            self.error_occurred.emit(blocking_request.errorMessage())
            return None

        reply = blocking_request.reply()
        if reply.error() == QNetworkReply.OperationCanceledError:
            return None

        if reply.error() != QNetworkReply.NoError:
            self.error_occurred.emit(reply.errorString())
            return None

        token_json = json.loads(reply.content().data().decode())
        return Token.from_json(token_json)


API_CLIENT = CesiumIonApiClient()
