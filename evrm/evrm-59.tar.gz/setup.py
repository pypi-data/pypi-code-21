#!/usr/bin/env python3
#
#

import os
import sys
import os.path

def j(*args):
    if not args: return
    todo = list(map(str, filter(None, args)))
    return os.path.join(*todo)

if sys.version_info.major < 3:
    print("you need to run evrm with python3")
    os._exit(1)

try:
    use_setuptools()
except:
    pass

try:
    from setuptools import setup
except Exception as ex:
    print(str(ex))
    os._exit(1)

target = "evrm"
upload = []

def uploadfiles(dir):
    upl = []
    if not os.path.isdir(dir):
        print("%s does not exist" % dir)
        os._exit(1)
    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if not os.path.isdir(d):
            if file.endswith(".pyc") or file.startswith("__pycache"):
                continue
            upl.append(d)
    return upl

def uploadlist(dir):
    upl = []

    for file in os.listdir(dir):
        if not file or file.startswith('.'):
            continue
        d = dir + os.sep + file
        if os.path.isdir(d):   
            upl.extend(uploadlist(d))
        else:
            if file.endswith(".pyc") or file.startswith("__pycache"):
                continue
            upl.append(d)

    return upl

setup(
    name='evrm',
    version='59',
    url='https://bitbucket.org/thatebart/evrm2',
    author='Bart Thate',
    author_email='bthate@dds.nl',
    description="Gif toedienende artsen de cel in !!",
    license='MIT',
    include_package_data=True,
    zip_safe=False,
    install_requires=["botlib"],
    scripts=["bin/evrm"],
    packages=['evrm', ],
    long_description='''"
MINISTER-PRESIDENT

"After 17 to 27 months of treatment, both haloperidol- and olanzapine-treated monkeys had an equivalent and highly significant 8% to 11% decrease in fresh brain weight and volume when compared with the sham group.", zie (3)

Geachte Minister-President,

|  omdat de Koningin gemeld heeft dat ze vanwege ministeriele verantwoordelijkheden geen tussenkomst kan bieden, wend ik mij tot u.

Ik ben Bart Thate, een 50 jaar oude schizofrenie patient. 

Op 20 Oktober 2012 heb ik na correspondentie met de Koningin een klacht tegen de Nederland ingedient (Thate tegen Nederland 69389/12). 
De klacht betrof het falen van de (F)ACT methodiek, de methode die GGZ Nederland gebruikt om vorm te geven aan de wetten die gedwongen behandeling in Nederland mogelijk maken.
De uitspraak` is niet-ontvankelijk.

Het is voor mij niet mogelijk gebleken om aangifte te doen van mishandeling als de psychiater zijn patient met gif mishandelt:

* De IGZ treft geen structurele onzorgvuldigheid in de afhandeling van klachten bij GGZ-NHN aan.
* De Hoge Raad concludeert dat het geen verantwoordelijkheid heeft en verwijst naar het Openbaar Ministerie, dat niet reageert.
* Daarna heb ik het Europeese Hof voor de Rechten van de Mens aangeschreven om een klacht tegen Nederland in te dienen. 
* Pas na een gang langs het EVRM reageert Het Openbaar Ministerie wel en verwijst naar de IGZ, die de klacht melding al heeft afgesloten. 

Het ontbreekt de GGZ patient aan een daadwerkelijke remedie om een einde te kunnen maken aan de mishandeling die een arts pleegt als hij gif toedient.

Er is bewijs dat antipsychotica gif zijn:

1) haloperiodol (haldol) - https://echa.europa.eu/substance-information/-/substanceinfo/100.000.142
2) clozapine (leponex) - https://echa.europa.eu/substance-information/-/substanceinfo/100.024.831
3) olanzapine (zyprexa) - https://echa.europa.eu/substance-information/-/substanceinfo/100.125.320
4) aripriprazole (abilify) https://echa.europa.eu/substance-information/-/substanceinfo/100.112.532

Gif toedienen is dodelijk, doordat de patient potentieel dodelijke lichamelijke aandoeninngen kan op doen.
Bijvoorbeeld clozapine kent de volgende potentieel dodelijke aandoeningen, zie (2):

* neutropenia (tekort witte bloedcellen)
* myocarditis (ontsteking hartspier)
* cardiomyopathy (ook hartspier)
* Hypotension (lage bloeddruk)
* bradycardia (trage hartslag)
* syncope (flauwvallen)
* cardiac carrest (hartstilstand)
* neuroleptic malignant syndrome (NMS)
* constipation (dikke darm verstopping)
* intestinal obstruction (darm problemen)
* fecal impaction (vastzittend stront)
* paralytic ileus (ook voedsel vastzittend in de darm)

Los van bijwerkingen die dodelijk kunnen zijn, kan dit medicijn ook in dodelijk hoeveelheid toegediend worden. 
12,5 mg is als dodelijk genoteerd, standaard OD is 2.5 gram, sommige overleven boven de 4 gram.

Dat het hier gif betreft en niet een onschadelijk medicijn maakt dat men een strafbaar feit pleegt.
U bent verantwoordelijk voor de zorg die de meest kwetsbaren hier in Nederland krijgen, u dient daarom te zorgen dat de zorg/verpleging die men ontvangt niet het plegen van strafbare feiten omvat.

Daarom eis ik van u dat u direct gif toedienende artsen door het Openbaar Ministerie laat vervolgen.

Omdat de GGZ patient niet instaat is om de mishandeling met gif door een arts te laten stoppen eis ik ook van u dat u voor de GGZ patient de vervolging zult doen.

Er van uitgaande dat u mijn eisen inwilligt,


Bart Thate 


p.s.

1) Het ligt niet in mijn vermogen om u via de rechter te dwingen deze eisen in te willigen.
2) https://drive.google.com/open?id=0BwaFXkZBje4OdnBmS05sQ2dkUEE
3) https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3476840/


''',
   data_files=[("docs", ["docs/conf.py","docs/index.rst"]),
               (j('docs', 'jpg'), uploadlist(os.path.join("docs","jpg"))),
               (j('docs', 'txt'), uploadlist(os.path.join("docs", "txt"))),
               (j('docs', '_templates'), uploadlist(os.path.join("docs", "_templates")))
              ],
   package_data={'': ["*.crt"],
                 },
   classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Topic :: Utilities'],
)
