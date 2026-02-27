import unittest
import mock

import gather_keys_oauth2
from oauthlib.oauth2.rfc6749.errors import (
    MissingTokenError,
    MismatchingStateError
)


class TestOAuth2Server(unittest.TestCase):

    def setUp(self):
        self.client_id = 'client_id'
        self.client_secret = 'client_secret'
        self.server = gather_keys_oauth2.OAuth2Server(
            self.client_id,
            self.client_secret
        )

    @mock.patch('gather_keys_oauth2.cherrypy.quickstart')
    @mock.patch('gather_keys_oauth2.threading.Timer')
    def test_browser_authorize(self, mock_timer, mock_quickstart):
        # Arrange
        self.server.oauth.authorize_token_url = mock.Mock(
            return_value=('http://example.com/auth', None)
        )

        # Act
        self.server.browser_authorize()

        # Assert
        self.server.oauth.authorize_token_url.assert_called_once_with(
            redirect_uri=self.server.redirect_uri
        )
        self.assertEqual(mock_timer.call_count, 1)  # Python2 mock compatibility
        mock_quickstart.assert_called_once_with(self.server)

    @mock.patch.object(gather_keys_oauth2.OAuth2Server, '_shutdown_cherrypy')
    def test_index_success(self, mock_shutdown):
        # Arrange
        self.server.oauth.fetch_access_token = mock.Mock()

        # Act
        response = self.server.index(
            state='state123',
            code='auth_code'
        )

        # Assert
        self.server.oauth.fetch_access_token.assert_called_once_with(
            'auth_code',
            self.server.redirect_uri
        )
        self.assertEqual(mock_shutdown.call_count, 1)  # Python2 mock compatibility
        self.assertIn('authorized to access the Fitbit API', response)

    @mock.patch.object(gather_keys_oauth2.OAuth2Server, '_shutdown_cherrypy')
    def test_index_missing_token_error(self, mock_shutdown):
        # Arrange
        self.server.oauth.fetch_access_token = mock.Mock(
            side_effect=MissingTokenError()
        )

        # Act
        response = self.server.index(
            state='state123',
            code='auth_code'
        )

        # Assert
        self.assertIn('Missing access token parameter', response)
        self.assertEqual(mock_shutdown.call_count, 1)  # Python2 mock compatibility

    @mock.patch.object(gather_keys_oauth2.OAuth2Server, '_shutdown_cherrypy')
    def test_index_mismatching_state_error(self, mock_shutdown):
        # Arrange
        self.server.oauth.fetch_access_token = mock.Mock(
            side_effect=MismatchingStateError()
        )

        # Act
        response = self.server.index(
            state='bad_state',
            code='auth_code'
        )

        # Assert
        self.assertIn('CSRF Warning', response)
        self.assertEqual(mock_shutdown.call_count, 1)  # Python2 mock compatibility

    @mock.patch.object(gather_keys_oauth2.OAuth2Server, '_shutdown_cherrypy')
    def test_index_without_code(self, mock_shutdown):
        # Act
        response = self.server.index(
            state='state123',
            code=None
        )

        # Assert
        self.assertIn('Unknown error while authenticating', response)
        self.assertEqual(mock_shutdown.call_count, 1)  # Python2 mock compatibility
