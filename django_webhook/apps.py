# pylint: disable=import-outside-toplevel
from django.apps import AppConfig
from django.db.models.signals import post_migrate


class WebhooksConfig(AppConfig):
    name = "django_webhook"
    default_auto_field = "django.db.models.AutoField"

    def ready(self):
        # --- SAFE: no DB access here --------------------
        import django_webhook.checks  # noqa: F401  # pylint: disable=unused-import,import-outside-toplevel

        from django_webhook.signals import connect_signals

        connect_signals()

        # --- DB-dependent logic: defer until DB exists ---
        post_migrate.connect(
            self._populate_topics,
            sender=self,
            dispatch_uid="django_webhook.populate_topics",
        )

    @staticmethod
    def _populate_topics(**kwargs):
        from django_webhook.models import populate_topics_from_settings

        populate_topics_from_settings()
