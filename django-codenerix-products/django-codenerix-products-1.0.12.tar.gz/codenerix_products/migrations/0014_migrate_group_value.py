# -*- coding: utf-8 -*-
# Generated by Django 1.10.6 on 2017-05-05 10:34
from __future__ import unicode_literals

from django.db import migrations
from django.db import connection, transaction
from django.conf import settings

from codenerix_products.models import MODELS, \
    GroupValueAttribute, Attribute, OptionValueAttribute, \
    GroupValueFeature, Feature, OptionValueFeature, \
    GroupValueFeatureSpecial, FeatureSpecial, OptionValueFeatureSpecial

for info in MODELS:
    field = info[0]
    model = info[1]
    for lang_code in settings.LANGUAGES_DATABASES:
        cad = "from codenerix_products.models import {}Text{}\n".format(model, lang_code)
        exec(cad)


def migrate_group_value(model_group, table_source, model_option):
        model_str = str(model_option).replace('"', '').replace("'", '').replace(">", '').split(".")[-1]
        
        cursor = connection.cursor()
        # select all the groups related to the source table
        query = """
            SELECT cpa.id, cpa.list_value_id, cpg.name
            FROM {table} AS cpa, codenerix_products_groupvalue AS cpg
            WHERE cpa.list_value_id = cpg.id
        """.format(**{'table': table_source})
        cursor.execute(query)
        for src in cursor:
            if src[1]:
                group_id = src[1]
                group_name = src[2]

                # If the group does not exist, it is created
                group = model_group.objects.filter(name=group_name).first()
                if not group:
                    group = model_group()
                    group.name = src[2]
                    group.save()

                # List with language information
                text_lang = []
                # List with table names
                froms = ['codenerix_products_optionvalue cpo', ]
                # List of query conditions
                conditions = ['cpo.group_id = {}'.format(group_id), ]
                # List of values to get from the query
                values = []

                for lang_code in settings.LANGUAGES_DATABASES:
                    # We get the model according to language
                    model_lang = globals()["{}Text{}".format(model_str, lang_code)]
                    # We save the language information
                    # Language, table name in database and model
                    text_lang.append((lang_code, model_lang._meta.db_table, model_lang))

                    alias = "t{}".format(lang_code.lower())
                    values.append('{}.description'.format(alias))
                    froms.append('codenerix_products_optionvaluetext{lang} {alias}'.format(**{'lang': lang_code.lower(), 'alias': alias}))
                    conditions.append('{}.option_value_id = cpo.id'.format(alias))

                # We get the information of the option with the values in all their languages
                query_text = "SELECT {} FROM {} WHERE {}".format(",".join(values), ",".join(froms), " AND ".join(conditions))
                
                # Re-initialize the form list
                froms = ['codenerix_products_optionvalue cpo', ]
                # Initialize conditions again
                conditions = ['cpo.group_id = {}'.format(group_id), ]
                for tl in text_lang:
                    alias = "t{}".format(tl[0].lower())
                    table = tl[1]
                    # Name of the final table where the new options should be
                    froms.append('{} {}'.format(table, alias))
                    # Relationship between the language table and the options table
                    conditions.append('{}.option_value_id = cpo.id'.format(alias))
                
                cursor.execute(query_text)

                for option in cursor:
                    # List of new conditionals
                    cond_extra = []
                    for v, o in zip(values, option):
                        # Field name, description value
                        cond_extra.append('{} = "{}"'.format(v, o))

                    # We built the new query
                    q_option = "SELECT COUNT(*) FROM {} WHERE {} AND {}".format(
                        ",".join(froms),
                        " AND ".join(conditions),
                        " AND ".join(cond_extra)
                    )

                    cursor.execute(q_option)
                    count = cursor.fetchone()

                    if count[0] == 0:
                        opt = model_option()
                        opt.group = group
                        opt.save()

                        for info_lang, description in zip(text_lang, option):
                            model_lang = info_lang[2]
                            opt_lang = model_lang()
                            opt_lang.description = description
                            opt_lang.option_value = opt
                            opt_lang.save()
        return 0


def run_migrate(apps, schema_editor):
    migrate_group_value(GroupValueAttribute, 'codenerix_products_attribute', OptionValueAttribute)
    migrate_group_value(GroupValueFeature, 'codenerix_products_feature', OptionValueFeature)
    migrate_group_value(GroupValueFeatureSpecial, 'codenerix_products_featurespecial', OptionValueFeatureSpecial)


class Migration(migrations.Migration):
    dependencies = [
        ('codenerix_products', '0013_optionvalueattributetexten_optionvalueattributetextes_optionvaluefeaturespecialtexten_optionvaluefea'),
    ]

    operations = [
        migrations.RunPython(run_migrate),
    ]
