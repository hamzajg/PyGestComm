"""Normalise existing client phones to the canonical form (ADR 0010).

0006 changed the column type; SQLite kept the digits but not the meaning of
the legacy `0` ("no phone") and left whatever separators a row happened to
hold. This migration applies `phones.canonical_phone` to the rows already in
the table. Values that cannot be canonicalised (for example a three-digit
legacy number) are left exactly as they are rather than being blanked: this
migration must never destroy data.
"""

from django.db import migrations

from GestCommApp.phones import canonical_phone


def forwards(apps, schema_editor):
    Client = apps.get_model('GestCommApp', 'Client')
    for client in Client.objects.all():
        changed = False
        for field in ('numTelClient1', 'numTelClient2'):
            raw = getattr(client, field)
            try:
                canonical = canonical_phone(raw)
            except ValueError:
                continue
            if canonical != raw:
                setattr(client, field, canonical)
                changed = True
        if changed:
            client.save(update_fields=['numTelClient1', 'numTelClient2'])


class Migration(migrations.Migration):

    dependencies = [
        ('GestCommApp', '0006_alter_client_numtelclient1_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards, migrations.RunPython.noop),
    ]
