from unittest.mock import patch

import pytest
from freezegun import freeze_time

from django_webhook.tasks import fire_webhook
from django_webhook.test_factories import (
    WebhookFactory,
    WebhookSecretFactory,
    WebhookTopicFactory,
)

pytestmark = pytest.mark.django_db


@freeze_time("2012-01-14 03:21:34")
def test_fire(responses):
    webhook = WebhookFactory(
        secrets__token="stevan-labudovic",
        topics=[WebhookTopicFactory(name="tests.User/create")],
    )
    responses.post(webhook.url)
    fire_webhook.delay(webhook.id, payload='{"hello": "world"}')
    assert len(responses.calls) == 1
    req = responses.calls[0].request
    assert req.body == b'{"hello": "world"}'
    h = req.headers
    assert h["Django-Webhook-Request-Timestamp"] == "1326511294"
    assert (
        h["Django-Webhook-Signature-v1"]
        == "b8989925491ccd7f040a92e371bd95d746c370acebae86c6b7deec3b7b0b66ed"
    )
    assert h["Content-Type"] == "application/json"


# TODO: Maybe in signals
def test_does_not_fire_inactive(responses):
    webhook = WebhookFactory(active=False)
    fire_webhook.delay(webhook.id, payload=dict(hello="world"))
    assert len(responses.calls) == 0


@freeze_time("2012-01-14 03:21:34")
def test_multiple_signatures(responses):
    webhook = WebhookFactory(
        topics=[WebhookTopicFactory(name="tests.User/create")], secrets=[]
    )
    WebhookSecretFactory(webhook=webhook, token="Hugh-Clowers-Thompson-Jr")
    WebhookSecretFactory(webhook=webhook, token="Augusto-César-Sandino")
    responses.post(webhook.url)
    fire_webhook.delay(webhook.id, payload='{"hello": "world"}')
    assert len(responses.calls) == 1
    h = responses.calls[0].request.headers
    # pylint: disable=line-too-long
    assert (
        h["Django-Webhook-Signature-v1"]
        == "7cde1ddd304f5e4c88fe5429cbe318ce83fd1f610a8004c8cafc20bc3289661f,28e85307029745b99e205c6003a4a5a7aa44f95f950a4cf44dfaa95df4a73d0c"
    )


def test_webhook_request_uses_timeout():
    """Test that webhook requests include a 10-second timeout"""
    webhook = WebhookFactory(
        secrets__token="test-token",
        topics=[WebhookTopicFactory(name="tests.User/create")],
    )

    with patch("django_webhook.tasks.Session") as mock_session_class:
        mock_session = mock_session_class.return_value
        mock_response = mock_session.send.return_value
        mock_response.raise_for_status.return_value = None

        fire_webhook.delay(webhook.id, payload='{"hello": "world"}')

        # Verify that send was called with timeout=10
        mock_session.send.assert_called_once()
        args, kwargs = mock_session.send.call_args
        assert "timeout" in kwargs
        assert kwargs["timeout"] == 10
