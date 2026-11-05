import copy

from django.db import migrations


def repair_custom_user_foreign_keys(apps, schema_editor):
    models_and_fields = [
        ('admin', 'LogEntry', 'user'),
        ('restaurants', 'Restaurant', 'owner'),
        ('orders', 'Order', 'customer'),
        ('orders', 'Cart', 'customer'),
    ]
    user_model = apps.get_model('users', 'User')

    for app_label, model_name, field_name in models_and_fields:
        model = apps.get_model(app_label, model_name)
        field = model._meta.get_field(field_name)
        field.remote_field.model = user_model
        unconstrained_field = copy.copy(field)
        unconstrained_field.db_constraint = False

        schema_editor.alter_field(
            model,
            field,
            unconstrained_field,
            strict=False,
        )
        schema_editor.alter_field(
            model,
            unconstrained_field,
            field,
            strict=False,
        )


class Migration(migrations.Migration):

    dependencies = [
        ('admin', '0001_initial'),
        ('orders', '0002_alter_order_estimated_preparation_time_cart_cartitem_and_more'),
        ('restaurants', '0002_category_fooditem'),
        ('users', '0004_contactmessage'),
    ]

    operations = [
        migrations.RunPython(
            repair_custom_user_foreign_keys,
            migrations.RunPython.noop,
        ),
    ]
