import unittest
import mock

import gather_keys_cli


class TestGatherKeysCLI(unittest.TestCase):

    @mock.patch('gather_keys_cli.webbrowser.open')
    @mock.patch('gather_keys_cli.FitbitOauthClient')
    @mock.patch('__builtin__.raw_input')  # Python 2.7 input
    def test_gather_keys_success(self, mock_raw_input, mock_client_cls, mock_browser):
        """
        Test successful OAuth flow in gather_keys()
        """

        # Arrange
        mock_raw_input.return_value = 'test_verifier_code'

        mock_client = mock.Mock()
        mock_client.fetch_request_token.return_value = {
            'oauth_token': 'request_token'
        }
        mock_client.authorize_token_url.return_value = 'http://example.com/auth'
        mock_client.fetch_access_token.return_value = {
            'oauth_token': 'access_token',
            'oauth_token_secret': 'access_secret'
        }

        mock_client_cls.return_value = mock_client

        # Set globals expected by the script
        gather_keys_cli.CLIENT_KEY = 'test_client_key'
        gather_keys_cli.CLIENT_SECRET = 'test_client_secret'

        # Act
        gather_keys_cli.gather_keys()

        # Assert
        mock_client_cls.assert_called_once_with(
            'test_client_key',
            'test_client_secret'
        )
        mock_client.fetch_request_token.assert_called_once_with()
        mock_browser.assert_called_once_with('http://example.com/auth')
        mock_client.fetch_access_token.assert_called_once_with('test_verifier_code')
