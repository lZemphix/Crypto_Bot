import pytest
from unittest.mock import patch
from src.utils.telenotify import Telenotify


class TestTelenotify:

    @patch("src.utils.telenotify.os.getenv")
    def test_init(self, mock_getenv):
        mock_getenv.side_effect = ["test_token", "test_chat_id"]
        telenotify = Telenotify()
        assert telenotify.TOKEN == "test_token"
        assert telenotify.CHAT_ID == "test_chat_id"

    @patch("src.utils.telenotify.requests.post")
    @patch("src.utils.telenotify.os.getenv")
    def test_send_message(self, mock_getenv, mock_post):
        mock_getenv.side_effect = ["test_token", "test_chat_id"]
        telenotify = Telenotify()
        telenotify.send_message("Test Title", "Test Message")
        expected_url = "https://api.telegram.org/bottest_token/sendMessage"
        expected_payload = {
            "chat_id": "test_chat_id",
            "text": "*Test Title*\nTest Message",
            "parse_mode": "Markdown",
        }
        mock_post.assert_called_once_with(expected_url, json=expected_payload)

    @patch("src.utils.telenotify.requests.post")
    @patch("src.utils.telenotify.os.getenv")
    def test_send_message_status_false(self, mock_getenv, mock_post):
        mock_getenv.side_effect = ["test_token", "test_chat_id"]
        telenotify = Telenotify(status=False)
        telenotify.send_message("Test Title", "Test Message")
        mock_post.assert_not_called()

    @patch.object(Telenotify, "send_message")
    def test_bot_status(self, mock_send_message):
        telenotify = Telenotify()
        telenotify.bot_status("Bot is running")
        mock_send_message.assert_called_once_with("🔔Bot status!", "Bot is running")

    @patch.object(Telenotify, "send_message")
    def test_bought(self, mock_send_message):
        telenotify = Telenotify()
        telenotify.bought("Bought 1 ETH")
        mock_send_message.assert_called_once_with("📉Buy!", "Bought 1 ETH")

    @patch.object(Telenotify, "send_message")
    def test_sold(self, mock_send_message):
        telenotify = Telenotify()
        telenotify.sold("Sold 1 ETH")
        mock_send_message.assert_called_once_with("📈Sell!", "Sold 1 ETH")

    @patch.object(Telenotify, "send_message")
    def test_error(self, mock_send_message):
        telenotify = Telenotify()
        telenotify.error("An error occurred")
        mock_send_message.assert_called_once_with("❌Error!", "An error occurred")

    @patch.object(Telenotify, "send_message")
    def test_warning(self, mock_send_message):
        telenotify = Telenotify()
        telenotify.warning("A warning occurred")
        mock_send_message.assert_called_once_with("⚠️Warning!", "A warning occurred")
