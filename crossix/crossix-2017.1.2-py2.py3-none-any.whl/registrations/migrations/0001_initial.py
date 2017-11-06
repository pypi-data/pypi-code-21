# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import crossix.registrations.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('name', models.CharField(unique=True, verbose_name='name', max_length=200)),
                ('gender', models.CharField(choices=[('M', 'Homme'), ('F', 'Femme')], verbose_name='gender', max_length=1)),
                ('min_age', models.IntegerField(verbose_name='min_age')),
            ],
            options={
                'verbose_name_plural': 'categories',
                'verbose_name': 'category',
            },
        ),
        migrations.CreateModel(
            name='Edition',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('date', models.DateField(unique=True, verbose_name='date')),
                ('close_registrations', models.DateField(unique=True, verbose_name='registration deadline')),
                ('location', models.CharField(choices=[('X', 'École polytechnique'), ('HEC', 'HEC'), ('ECP', 'École Centrale')], verbose_name='location', max_length=3)),
            ],
            options={
                'verbose_name_plural': 'editions',
                'verbose_name': 'edition',
            },
        ),
        migrations.CreateModel(
            name='Participant',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('firstname', models.CharField(verbose_name='firstname', max_length=200)),
                ('lastname', models.CharField(verbose_name='lastname', max_length=200)),
                ('birthyear', models.CharField(blank=True, choices=[('1998', '1998'), ('1997', '1997'), ('1996', '1996'), ('1995', '1995'), ('1994', '1994'), ('1993', '1993'), ('1992', '1992'), ('1991', '1991'), ('1990', '1990'), ('1989', '1989'), ('1988', '1988'), ('1987', '1987'), ('1986', '1986'), ('1985', '1985'), ('1984', '1984'), ('1983', '1983'), ('1982', '1982'), ('1981', '1981'), ('1980', '1980'), ('1979', '1979'), ('1978', '1978'), ('1977', '1977'), ('1976', '1976'), ('1975', '1975'), ('1974', '1974'), ('1973', '1973'), ('1972', '1972'), ('1971', '1971'), ('1970', '1970'), ('1969', '1969'), ('1968', '1968'), ('1967', '1967'), ('1966', '1966'), ('1965', '1965'), ('1964', '1964'), ('1963', '1963'), ('1962', '1962'), ('1961', '1961'), ('1960', '1960'), ('1959', '1959'), ('1958', '1958'), ('1957', '1957'), ('1956', '1956'), ('1955', '1955'), ('1954', '1954'), ('1953', '1953'), ('1952', '1952'), ('1951', '1951'), ('1950', '1950'), ('1949', '1949'), ('1948', '1948'), ('1947', '1947'), ('1946', '1946'), ('1945', '1945'), ('1944', '1944'), ('1943', '1943'), ('1942', '1942'), ('1941', '1941'), ('1940', '1940'), ('1939', '1939'), ('1938', '1938'), ('1937', '1937'), ('1936', '1936'), ('1935', '1935'), ('1934', '1934'), ('1933', '1933'), ('1932', '1932'), ('1931', '1931'), ('1930', '1930'), ('1929', '1929'), ('1928', '1928'), ('1927', '1927'), ('1926', '1926'), ('1925', '1925'), ('1924', '1924'), ('1923', '1923'), ('1922', '1922'), ('1921', '1921'), ('1920', '1920'), ('1919', '1919'), ('1918', '1918'), ('1917', '1917'), ('1916', '1916'), ('1915', '1915'), ('1914', '1914'), ('1913', '1913'), ('1912', '1912'), ('1911', '1911'), ('1910', '1910'), ('1909', '1909'), ('1908', '1908'), ('1907', '1907'), ('1906', '1906'), ('1905', '1905'), ('1904', '1904'), ('1903', '1903'), ('1902', '1902'), ('1901', '1901')], verbose_name='birthyear', max_length=4, null=True)),
                ('gender', models.CharField(choices=[('M', 'Homme'), ('F', 'Femme')], verbose_name='gender', max_length=1)),
                ('email', models.EmailField(verbose_name='email', max_length=254)),
                ('school', models.CharField(choices=[('X', 'Polytechnique'), ('HEC', 'HEC'), ('ECP', 'Centrale'), ('OTHER', 'Accompagnant')], verbose_name='school', max_length=5)),
                ('promo', models.IntegerField(blank=True, verbose_name='promo', null=True)),
                ('category', models.ForeignKey(to='registrations.Category', verbose_name='category')),
                ('last_edition', models.ForeignKey(to='registrations.Edition', default=crossix.registrations.models.next_edition)),
            ],
        ),
    ]
