# misc/migrations/0009_load_reportcraft_fixture.py

import os
from django.db import migrations
from django.core import serializers


def load_fixture(apps, schema_editor):
    fixture_path = os.path.join(
        os.path.dirname(__file__),
        '..',  # migrations/
        'fixtures',
        '001-reportcraft.yml'
    )
    db_alias = schema_editor.connection.alias
    with open(fixture_path, 'r') as fixture_file:
        objects = serializers.deserialize('yaml', fixture_file)
        for obj in objects:
            obj.save(using=db_alias)


class Migration(migrations.Migration):

    dependencies = [
        ('misc', '0008_auto_20250909_1647'),  # Son migration dosyanın ismini buraya yaz
    ]

    operations = [
        migrations.RunPython(load_fixture, reverse_code=migrations.RunPython.noop),
    ]
