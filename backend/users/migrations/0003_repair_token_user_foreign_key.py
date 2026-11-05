from django.db import migrations


def repair_token_user_foreign_key(apps, schema_editor):
    connection = schema_editor.connection
    Token = apps.get_model('authtoken', 'Token')
    User = apps.get_model('users', 'User')
    token_table = Token._meta.db_table
    user_table = User._meta.db_table

    if connection.vendor != 'sqlite':
        with connection.cursor() as cursor:
            constraints = connection.introspection.get_constraints(cursor, token_table)
        foreign_tables = {
            details['foreign_key'][0]
            for details in constraints.values()
            if details.get('foreign_key')
        }
        if user_table not in foreign_tables:
            raise RuntimeError(
                f'{token_table} must reference {user_table}; repair this database schema before signup.'
            )
        return

    quote = connection.ops.quote_name
    with connection.cursor() as cursor:
        cursor.execute(f'PRAGMA foreign_key_list({quote(token_table)})')
        if any(row[2] == user_table for row in cursor.fetchall()):
            return

        if connection.in_atomic_block:
            raise RuntimeError('Token table repair must run outside a transaction.')

        cursor.execute('PRAGMA foreign_keys = OFF')
        try:
            repaired_table = f'{token_table}_repaired'
            cursor.execute(f'DROP TABLE IF EXISTS {quote(repaired_table)}')
            cursor.execute(
                f'CREATE TABLE {quote(repaired_table)} ('
                '"key" varchar(40) NOT NULL PRIMARY KEY, '
                '"created" datetime NOT NULL, '
                f'"user_id" integer NOT NULL UNIQUE REFERENCES {quote(user_table)} ("id") '
                'DEFERRABLE INITIALLY DEFERRED)'
            )
            cursor.execute(
                f'INSERT INTO {quote(repaired_table)} ("key", "created", "user_id") '
                f'SELECT old."key", old."created", old."user_id" '
                f'FROM {quote(token_table)} AS old '
                f'INNER JOIN {quote(user_table)} AS user ON user."id" = old."user_id"'
            )
            cursor.execute(f'DROP TABLE {quote(token_table)}')
            cursor.execute(
                f'ALTER TABLE {quote(repaired_table)} RENAME TO {quote(token_table)}'
            )
        finally:
            cursor.execute('PRAGMA foreign_keys = ON')


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ('authtoken', '0004_alter_tokenproxy_options'),
        ('users', '0002_user_delivery_address_postal_code'),
    ]

    operations = [
        migrations.RunPython(
            repair_token_user_foreign_key,
            migrations.RunPython.noop,
        ),
    ]
