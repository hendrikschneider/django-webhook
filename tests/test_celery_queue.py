import pytest
from django.test import override_settings

from django_webhook.models import WebhookTopic
from django_webhook.test_factories import WebhookFactory, WebhookTopicFactory

from tests.model_data import TEST_JOIN_DATE, TEST_LAST_ACTIVE
from tests.models import User


pytestmark = pytest.mark.django_db


@override_settings(
    DJANGO_WEBHOOK=dict(
        MODELS=["tests.User"],
        CELERY_QUEUE="webhooks",
    )
)
def test_uses_configured_celery_queue(mocker):
    """Test that webhooks are sent to the configured Celery queue"""
    # Get or create the webhook topic
    topic, _ = WebhookTopic.objects.get_or_create(name="tests.User/create")

    # Create a webhook for User creation
    WebhookFactory(
        topics=[topic],
    )

    # Mock the fire_webhook task
    mock_fire_webhook = mocker.patch("django_webhook.signals.fire_webhook")

    # Create a user which should trigger the webhook
    User.objects.create(
        name="Test User",
        email="test@example.com",
        join_date=TEST_JOIN_DATE,
        last_active=TEST_LAST_ACTIVE,
    )

    # Verify that apply_async was called (not delay)
    assert mock_fire_webhook.apply_async.called
    assert not mock_fire_webhook.delay.called

    # Verify the queue parameter was passed
    call_kwargs = mock_fire_webhook.apply_async.call_args[1]
    assert "queue" in call_kwargs
    assert call_kwargs["queue"] == "webhooks"


@override_settings(
    DJANGO_WEBHOOK=dict(
        MODELS=["tests.User"],
    )
)
def test_uses_default_queue_when_not_configured(mocker):
    """Test that webhooks use delay() when no queue is configured"""
    # Get or create the webhook topic
    topic, _ = WebhookTopic.objects.get_or_create(name="tests.User/create")

    # Create a webhook for User creation
    WebhookFactory(
        topics=[topic],
    )

    # Mock the fire_webhook task
    mock_fire_webhook = mocker.patch("django_webhook.signals.fire_webhook")

    # Create a user which should trigger the webhook
    User.objects.create(
        name="Test User",
        email="test@example.com",
        join_date=TEST_JOIN_DATE,
        last_active=TEST_LAST_ACTIVE,
    )

    # Verify that delay was called (not apply_async)
    assert mock_fire_webhook.delay.called
    assert not mock_fire_webhook.apply_async.called


@override_settings(
    DJANGO_WEBHOOK=dict(
        MODELS=["tests.User"],
        CELERY_QUEUE=None,
    )
)
def test_uses_default_queue_when_explicitly_none(mocker):
    """Test that webhooks use delay() when queue is explicitly set to None"""
    # Get or create the webhook topic
    topic, _ = WebhookTopic.objects.get_or_create(name="tests.User/create")

    # Create a webhook for User creation
    WebhookFactory(
        topics=[topic],
    )

    # Mock the fire_webhook task
    mock_fire_webhook = mocker.patch("django_webhook.signals.fire_webhook")

    # Create a user which should trigger the webhook
    User.objects.create(
        name="Test User",
        email="test@example.com",
        join_date=TEST_JOIN_DATE,
        last_active=TEST_LAST_ACTIVE,
    )

    # Verify that delay was called (not apply_async)
    assert mock_fire_webhook.delay.called
    assert not mock_fire_webhook.apply_async.called
