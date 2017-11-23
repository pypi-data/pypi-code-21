# -*- coding: utf-8 -*-
"""
@file
@brief Default options for the application.
"""
import os
from .competition import Competition


class LightMLBoardDefaultOptions:
    """
    Default options for the web application.
    """

    lang = "fr"

    debug = True

    logging = True

    title = "Compétition de Machine Learning"

    subtitle = "ENSAE"

    cookie_secret = "bZJc2sWbQLKos6GkHn/VB9oXwQt8S0R0kRvJ5/xJ89E="

    description = """Tableaux de résultats pour la compétition
        de machine learning organisé dans le cadre du cours
        <a href="http://www.xavierdupre.fr/app/ensae_teaching_cs/helpsphinx3/index.html">Python pour un data scientist économiste</a>.
        """.replace("        ", "")

    description2 = """Détails de la compétition :
        <a href="http://www.xavierdupre.fr/app/ensae_teaching_cs/helpsphinx3/questions/competition_2A.html#l-competition-2017-2a">
        Compétition 2017 - additifs alimentaires</a>.
        """.replace("        ", "")

    title_main = "Principe"
    description_main = """..."""

    allowed_users = None

    competitions = [Competition(
        cpt_id=0,
        name="Prédiction de la présence d'additifs",
        link="http://www.xavierdupre.fr/app/ensae_teaching_cs/helpsphinx3/questions/competition_2A.html#competition-2017-additifs-alimentaires",
        expected_values=os.path.join(
            os.path.dirname(__file__), "data", "dummy_prediction.data"),
        metric=["roc_auc_score_micro", "roc_auc_score_macro"],
        description="""Le site OpenFoodFacts recense la composition de milliers de produits.
                        La base de données peut être téléchargée (data). On veut savoir si les additifs ajoutés
                        apparaissent plus fréquemment avec certains produits ou certaines compositions. Une façon
                        est de prédire la présence d'additifs en fonction de toutes les autres variables.
                        Si un modèle de prédiction fait mieux que le hasard, cela signifie que certaines
                        corrélations existent. C'est un problème de classification binaire.""")]
