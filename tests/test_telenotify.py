from unittest.mock import patch, MagicMock
from utils.telenotify import Telenotify


@patch('utils.telenotify.os.getenv')
@patch('utils.telenotify.requests.post')
def test_telenotify_send_message_status_true(mock_post, mock_getenv):
    mock_getenv.side_effect = lambda key: 'test_token' if key == 'BOT_TOKEN' else 'test_chat_id'
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_post.return_value = mock_response

    notify = Telenotify(status=True)
    status_code = notify.send_message("Test Title", "Test Message")

    assert status_code == 200
    expected_url = "https://api.telegram.org/bottest_token/sendMessage"
    expected_payload = {
        "chat_id": "test_chat_id",
        "text": "*Test Title*\nTest Message",
        "parse_mode": "Markdown"
    }
    mock_post.assert_called_once_with(expected_url, json=expected_payload)


@patch('utils.telenotify.requests.post')
def test_telenotify_send_message_status_false(mock_post):
    notify = Telenotify(status=False)
    notify.send_message("Test Title", "Test Message")
    mock_post.assert_not_called()


@patch.object(Telenotify, 'send_message')
def test_telenotify_helper_methods(mock_send_message):
    notify = Telenotify()

    notify.bot_status("Bot started")
    mock_send_message.assert_called_with("🔔Bot status!", "Bot started")

    notify.bought("Bought 1 BTC")
    mock_send_message.assert_called_with("📉Buy!", "Bought 1 BTC")

    notify.sold("Sold 1 BTC")
    mock_send_message.assert_called_with("📈Sell!", "Sold 1 BTC")

    notify.error("An error occurred")
    mock_send_message.assert_called_with("❌Error!", "An error occurred")

    notify.warning("A warning occurred")
    mock_send_message.assert_called_with("⚠️Warning!", "A warning occurred")
