import pickle

from tf_core.document_corpus import DocumentCorpus
from tf_core.nltoolkit.library import corpus_reader
from nltk.tag.sequential import (DefaultTagger, NgramTagger, AffixTagger,
                                 RegexpTagger, #<--TODO
                                 ClassifierBasedPOSTagger)
import nltk.tag.brill
from nltk.tag.brill      import BrillTagger
from nltk.tag.brill_trainer import BrillTaggerTrainer
from nltk.tag.tnt        import TnT
from nltk.tag.hunpos     import HunposTagger
from nltk.tag.stanford   import StanfordTagger
#from nltk.tag.crf        import MalletCRF
from django.conf import settings
from nltk.corpus import brown, treebank, nps_chat
from nltk.tag.stanford import StanfordPOSTagger
import os
import re
import subprocess
from tree_tagger import TreeTagger
from crf_tagger import CRFTagger, PickleableCRFTagger
from nltk.tag import tnt
import nlp4j


class StanfordTagger(StanfordPOSTagger):

    def __init__(self, *args, **kwargs):
        super(StanfordTagger, self).__init__(*args, **kwargs)

    def train(self, corpus, widget_id):
        output_path = os.path.join(settings.STANFORD_POS_TAGGER, str(widget_id) + '.tsv')
        output_model = os.path.join(settings.STANFORD_POS_TAGGER,  str(widget_id) + '.tagger')
        if os.path.exists(output_model):
            os.remove(output_model)
        if os.path.exists(output_path):
            os.remove(output_path)
        with open(output_path, 'a') as f:
            for sentence in corpus:
                s = []
                for word, tag in sentence:
                    if word.strip() and tag.strip():
                        token = word.strip().replace(" ", "") + '_' + tag.strip()
                        if '_' in token:
                            s.append(token)
                new_sentence = " ".join(s)
                f.write(" " + new_sentence + " ")
        f.close()
        subprocess.call(
            ['java', '-mx4g',
             '-classpath', settings.STANFORD_POS_TAGGER_JAR,
             'edu.stanford.nlp.tagger.maxent.MaxentTagger',
             '-model', os.path.join(settings.STANFORD_POS_TAGGER,  str(widget_id) + '.tagger'),
             '-trainFile', os.path.join(settings.STANFORD_POS_TAGGER,  str(widget_id) + '.tsv'),
             '-tagSeparator', '_',
             '-props', settings.STANFORD_POS_TAGGER_PROPS])


def stanford_pos_tagger(input_dict, widget):
    name= 'StanfordPosTagger'
    if not input_dict['training_corpus']:
        tagger = StanfordTagger(model_filename=settings.STANFORD_POS_TAGGER_MODEL, path_to_jar=settings.STANFORD_POS_TAGGER_JAR, java_options='-mx4000m')
    else:
        chunk = input_dict['training_corpus']['chunk']
        corpus = input_dict['training_corpus']['corpus']
        training_corpus=corpus_reader(corpus, chunk)
        tagger = StanfordTagger(model_filename=settings.STANFORD_POS_TAGGER_MODEL, path_to_jar=settings.STANFORD_POS_TAGGER_JAR, java_options='-mx4000m')
        tagger.train(list(training_corpus), widget.id)
        tagger = StanfordTagger(model_filename=os.path.join(settings.STANFORD_POS_TAGGER,  str(widget.id) + '.tagger'), path_to_jar=settings.STANFORD_POS_TAGGER_JAR, java_options='-mx4000m')
    return {'pos_tagger': {
                'function':'tag_sents',
                'object': tagger,
                'name': name,

            }
    }


def tree_tagger(input_dict, widget):
    name= 'TreeTagger'
    if not input_dict['training_corpus']:
        tagger = TreeTagger(language='english', widget_id=widget.id)
    else:
        chunk = input_dict['training_corpus']['chunk']
        corpus = input_dict['training_corpus']['corpus']
        training_corpus=corpus_reader(corpus, chunk)
        tagger = TreeTagger(language='english', widget_id=widget.id, trained=True)
        tagger.train(list(training_corpus))
    return {'pos_tagger': {
                'function':'tag',
                'object': tagger,
                'name': name,
            }
    }


def crf_pos_tagger(input_dict, widget):
    name= 'CRFPosTagger'
   
    crf_tagger = CRFTagger()
    chunk = input_dict['training_corpus']['chunk']
    corpus = input_dict['training_corpus']['corpus']
    training_corpus=corpus_reader(corpus, chunk)
    model_path = os.path.join(settings.CRF_TAGGER,  str(widget.id) + '.crf.tagger')
    crf_tagger.train(list(training_corpus), model_path)
    tagger = PickleableCRFTagger(model_path)
    #print(crf_tagger.tag_sents([['test', 'is'], ['hey', 'there']]))

    return {'pos_tagger': {
                'function':'tag_sents',
                'object': tagger,
                'name': name,
            }
    }

def tnt_pos_tagger(input_dict):
    name= 'TNTPosTagger'

    tnt_tagger = tnt.TnT()
    chunk = input_dict['training_corpus']['chunk']
    corpus = input_dict['training_corpus']['corpus']
    training_corpus=corpus_reader(corpus, chunk)
    tnt_tagger.train(list(training_corpus))

    return {'pos_tagger': {
                'function':'tagdata',
                'object': tnt_tagger,
                'name': name
            }
    }

def nlp4j_tagger(input_dict, widget):
    name= 'NLP4jPosTagger'
    if not input_dict['training_corpus']:
        NLP4J_INPUT = os.path.join(settings.NLP4J_INPUT, str(widget.id) + '_nlp4j_input.txt')
        NLP4J_CONFIG = os.path.join(settings.NLP4J_CONFIG, 'config_pretrained.xml')
        NLP4J_TRAIN_SET = os.path.join(settings.NLP4J_INPUT, str(widget.id) + '_nlp4j_train.tsv')
        NLP4J_DEV_SET = os.path.join(settings.NLP4J_INPUT, str(widget.id) + '_nlp4j_dev.tsv')
        NLP4J_MODEL = os.path.join(settings.NLP4J_MODEL, str(widget.id) + '.xz')
        NLP4J_CONFIG_TRAINED = os.path.join(settings.NLP4J_CONFIG, "config_trained.xml")
        nlp4j_tagger = nlp4j.NLP4JTagger(settings.NLP4J_BINARIES, NLP4J_CONFIG, NLP4J_INPUT, NLP4J_TRAIN_SET, NLP4J_DEV_SET, NLP4J_MODEL, NLP4J_CONFIG_TRAINED, pretrained=False)
    else:
        chunk = input_dict['training_corpus']['chunk']
        corpus = input_dict['training_corpus']['corpus']
        training_corpus=corpus_reader(corpus, chunk)

        NLP4J_INPUT = os.path.join(settings.NLP4J_INPUT, str(widget.id) + '_nlp4j_input.txt')
        NLP4J_MODEL = os.path.join(settings.NLP4J_MODEL, str(widget.id) + '.xz')
        NLP4J_CONFIG = os.path.join(settings.NLP4J_CONFIG, str(widget.id) + '.xml')
        NLP4J_CONFIG_TRAINED = os.path.join(settings.NLP4J_CONFIG, "config_trained.xml")
        NLP4J_TRAIN_SET = os.path.join(settings.NLP4J_INPUT, str(widget.id) + '_nlp4j_train.tsv')
        NLP4J_DEV_SET = os.path.join(settings.NLP4J_INPUT, str(widget.id) + '_nlp4j_dev.tsv')
        nlp4j_tagger = nlp4j.NLP4JTagger(settings.NLP4J_BINARIES, NLP4J_CONFIG, NLP4J_INPUT, NLP4J_TRAIN_SET, NLP4J_DEV_SET, NLP4J_MODEL, NLP4J_CONFIG_TRAINED, pretrained=False)
        nlp4j_tagger.train(list(training_corpus))

    return {'pos_tagger': {
            'function':'decode',
            'object':nlp4j_tagger,
            'name': name,
        }
    }









