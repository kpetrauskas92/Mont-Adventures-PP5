from django.db import migrations

def run_generate_dates(apps, schema_editor):
    from django.core import management
    try:
        management.call_command("generate_dates")
    except Exception:
        # keep deploy alive even if command is idempotent or already applied
        pass

def noop(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    dependencies = [
        ("trip_packages", "0001_initial"),
    ]
    operations = [
        migrations.RunPython(run_generate_dates, noop),
    ]
