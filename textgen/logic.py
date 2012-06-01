# coding: utf-8
import os
import json
import numbers

from textgen.exceptions import NoGrammarFound
from textgen.conf import textgen_settings

class PROPERTIES(object):
    CASES = (u'им', u'рд', u'дт', u'вн', u'тв', u'пр')
    ANIMACYTIES = (u'од', u'но')
    NUMBERS = (u'ед', u'мн')
    GENDERS = (u'мр', u'жр', u'ср') # REMBER about 'мн' case in pymorphy
    TIMES = (u'нст', u'прш', u'буд')
    PERSONS = (u'1л', u'2л', u'3л')

    @classmethod
    def is_argument_available(cls, arg):
        return (arg in cls.CASES or
                arg in cls.ANIMACYTIES or
                arg in cls.NUMBERS or
                arg in cls.GENDERS or
                arg in cls.TIMES or
                arg in cls.PERSONS)


class Args(object):

    __slots__ = ('case', 'number', 'gender', 'time', 'person')

    def __init__(self, *args):
        self.case = u'им'
        self.number = u'ед'
        self.gender = u'мр'
        self.time = u'нст'
        self.person = u'1л'
        self.update(*args)

    def get_copy(self):
        return self.__class__(self.case, self.number, self.gender, self.time, self.person)

    def update(self, *args):
        for arg in args:
            if arg in PROPERTIES.CASES:
                self.case = arg
            elif arg in PROPERTIES.NUMBERS:
                self.number = arg
            elif arg in PROPERTIES.GENDERS:
                self.gender = arg
            elif arg in PROPERTIES.TIMES:
                self.time = arg
            elif arg in PROPERTIES.PERSONS:
                self.person = arg

        # if world exists only in multiple number (ножницы) there will be 2 u'мн' values - one for gender and one for number
        if args.count(u'мн') > 1:
            self.gender = u'мн'

    # order: time, case, time, gender
    # - прш, ед, мр
    # - прш, ед|мр
    # - прш
    # - им, ед, мр
    # - им, ед|мр
    # - им
    @property
    def order_points(self):
        points = 0

        if self.time == u'прш': points += 1
        points *=2

        if self.case == u'им': points += 1
        points *= 2

        if self.time == u'мн': points += 1
        points *= 2

        if self.gender == u'мр': points += 1

        return points

    def has_priority(self, other):
        return self.order_points > other.order_points


    def __unicode__(self):
        return (u'<%s, %s, %s, %s, %s>' % (self.case, self.number, self.gender, self.time, self.person)).encode('utf-8')

    def __str__(self): return self.__unicode__()



def efication(word):
    return word.replace(u'Ё', u'Е').replace(u'ё', u'е')

def get_gram_info(morph, word, tech_vocabulary={}):
    normalized = word.lower()
    class_ = None
    if tech_vocabulary.get(normalized):
        class_ = tech_vocabulary[word.lower()] # TODO: ???

    properties = None
    for info in morph.get_graminfo(word.upper()):

        if class_ and info['class'] != class_:
            continue

        if u'имя' in info['info']:
            continue

        current_properties = Args(*info['info'].split(','))

        if not properties or not properties.has_priority(current_properties):
            properties = current_properties
            class_ = info['class']

    if not class_:
        raise NoGrammarFound(u'can not find info about word: "%s"' % word)

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
