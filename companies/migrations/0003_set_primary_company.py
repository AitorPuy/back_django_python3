# Generated manually

from django.db import migrations


def set_first_company_as_primary(apps, schema_editor):
    Company = apps.get_model('companies', 'Company')
    # Marcar el primer registro como principal si existe
    first_company = Company.objects.first()
    if first_company:
        first_company.is_primary = True
        first_company.save()


def reverse_set_primary(apps, schema_editor):
    Company = apps.get_model('companies', 'Company')
    # Desmarcar todos como principal
    Company.objects.update(is_primary=False)


class Migration(migrations.Migration):

    dependencies = [
        ('companies', '0002_company_is_primary'),
    ]

    operations = [
        migrations.RunPython(set_first_company_as_primary, reverse_set_primary),
    ]
