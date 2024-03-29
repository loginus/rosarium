# Generated by Django 3.0.4 on 2020-03-28 18:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rosary', '0008_auto_20171115_2118'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mystery',
            name='group',
            field=models.CharField(choices=[('joyful', 'Tajemnica Radosna'), ('luminous', 'Tajemnica Światła'), ('sorrowful', 'Tajemnica Bolesna'), ('glorious', 'Tajemnica Chwalebna')], max_length=15),
        ),
        migrations.AlterField(
            model_name='mystery',
            name='image_path',
            field=models.ImageField(upload_to=''),
        ),
        migrations.AlterField(
            model_name='person',
            name='rosa',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, to='rosary.Rosa'),
        ),
        migrations.AlterField(
            model_name='personintension',
            name='intension',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rosary.Intension'),
        ),
        migrations.AlterField(
            model_name='personintension',
            name='mystery',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rosary.Mystery'),
        ),
        migrations.AlterField(
            model_name='personintension',
            name='person',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='rosary.Person'),
        ),
    ]
