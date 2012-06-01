# coding: utf-8
import os
import json
import numbers

from textgen.exceptions import TextgenException
from textgen.conf import textgen_settings


def efication(word):
    return word.replace(u'Ё', u'Е').replace(u'ё', u'е')

def get_gram_info(morph, word, tech_vocabulary={}):
    normalized = word.lower()
    if tech_vocabulary.get(normalized):
        class_ = tech_vocabulary[word.lower()] # TODO: ???
    else:
        gram_info = morph.get_graminfo(word.upper())

        classes = set([info['class'] for info in gram_info])

        if len(classes) > 1:
            raise TextgenException(u'more then one grammar info for word: %s' % word)

        if not classes:
            raise TextgenException(u'can not find info about word: "%s"' % word)

        class_ = list(classes)[0]

    properties = ()
    for info in morph.get_graminfo(word.upper()):
        if u'имя' in info['info']:
            continue
        if info['class'] == class_:
            properties = tuple(info['info'].split(','))

            break #TODO: stop of most common form ("им" for nouns)

    return class_, properties


def get_tech_vocabulary():
    tech_vocabulary_file_name = os.path.join(textgen_settings.TEXTS_DIRECTORY, 'vocabulary.json')
    if not os.path.exists(tech_vocabulary_file_name):
        tech_vocabulary = {}
    else:
        with open(tech_vocabulary_file_name) as f:
            tech_vocabulary = json.loads(f.read())
    return tech_vocabulary


def import_texts(morph, voc_storage, dict_storage, debug=False):
    from textgen.templates import Dictionary, Vocabulary, Template
    from textgen.words import WordBase

    vocabulary = Vocabulary()
    vocabulary.load(storage=voc_storage)

    dictionary = Dictionary()
    dictionary.load(storage=dict_storage)

    tech_vocabulary = get_tech_vocabulary()

    for word in tech_vocabulary.keys():
        word = WordBase.create_from_string(morph, word.strip(), tech_vocabulary)
        dictionary.add_word(word)

    for filename in os.listdir(textgen_settings.TEXTS_DIRECTORY):

        if not filename.endswith('.json'):
            continue

        if filename == 'vocabulary.json':
            continue

        texts_path = os.path.join(textgen_settings.TEXTS_DIRECTORY, filename)

        if not os.path.isfile(texts_path):
            continue

        group = filename[:-5]

        if debug:
            print 'load %s' % group

        with open(texts_path) as f:
            data = json.loads(f.read())

            if group != data['prefix']:
                raise Exception('filename MUST be equal to prefix')

            for suffix in data['types']:
                if suffix == '':
                    raise Exception('type MUST be not equal to empty string')

            for suffix, type_ in data['types'].items():
                phrase_key = '%s_%s' % (group , suffix)
                for phrase in type_['phrases']:
                    template_phrase, test_phrase = phrase
                    variables = type_['variables']
                    template = Template.create(morph, template_phrase, available_externals=variables.keys(), tech_vocabulary=tech_vocabulary)

                    vocabulary.add_phrase(phrase_key, template)

                    for value in variables.values():
                        if isinstance(value, numbers.Number):
                            continue
                        word = WordBase.create_from_string(morph, value, tech_vocabulary)
                        dictionary.add_word(word)

                    for string in template.get_internal_words():
                        word = WordBase.create_from_string(morph, string, tech_vocabulary)
                        dictionary.add_word(word)

                    test_result = template.substitute(dictionary, variables)
                    if efication(test_result.lower()) != efication(test_phrase.lower()):
                        raise TextgenException(u'wrong test render for phrase "%s": "%s"' % (template_phrase, test_result))


    vocabulary.save(storage=voc_storage)
    dictionary.save(storage=dict_storage)
