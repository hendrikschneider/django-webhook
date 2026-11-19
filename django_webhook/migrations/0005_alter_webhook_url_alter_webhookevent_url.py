from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("django_webhook", "0004_alter_webhookevent_created_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="webhook",
            name="url",
            field=models.URLField(max_length=2048),
        ),
        migrations.AlterField(
            model_name="webhookevent",
            name="url",
            field=models.URLField(editable=False, max_length=2048),
        ),
    ]
