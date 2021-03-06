# coding: utf-8
import os
import json
import copy
import numbers

from textgen.exceptions import NoGrammarFound, TextgenException


class PROPERTIES(object):
    CASES = (u'им', u'рд', u'дт', u'вн', u'тв', u'пр')
    ANIMACYTIES = (u'од', u'но')
    NUMBERS = (u'ед', u'мн')
    GENDERS = (u'мр', u'жр', u'ср') # REMBER about 'мн' case in pymorphy
    TIMES = (u'нст', u'прш', u'буд')
    PERSONS = (u'1л', u'2л', u'3л')
    WORD_CASE = (u'строч', u'загл',)

    @classmethod
    def is_argument_available(cls, arg):
        return (arg in cls.CASES or
                arg in cls.ANIMACYTIES or
                arg in cls.NUMBERS or
                arg in cls.GENDERS or
                arg in cls.TIMES or
                arg in cls.PERSONS or
                arg in cls.WORD_CASE)


class Args(object):

    __slots__ = ('case', 'number', 'gender', 'time', 'person', 'word_case')

    def __init__(self, *args):
        self.case = u'им'
        self.number = u'ед'
        self.gender = u'мр'
        self.time = u'нст'
        self.person = u'1л'
        self.word_case = u'строч'
        # self.case = u''
        # self.number = u''
        # self.gender = u''
        # self.time = u''
        # self.person = u''
        self.update(*args)

    def get_copy(self):
        return self.__class__(self.case, self.number, self.gender, self.time, self.person, self.word_case)

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
            elif arg in PROPERTIES.WORD_CASE:
                self.word_case = arg

        # if world exists only in multiple number (ножницы) there will be 2 u'мн' values - one for gender and one for number
        if args.count(u'мн') > 1:
            self.gender = u'мн'

    # order: time, case, time, gender
    def order_points(self, class_):
        distance = 0

        if class_ in (u'С',):
            if self.case != u'им': distance += 1
            # priority has forms with multiply gender, like "трусы"
            if self.number == u'мн' and self.gender != u'мн': distance += 1

        elif class_ == u'Г':
            if self.time != u'прш': distance += 1
            if self.gender != u'мр': distance += 1
            if self.number == u'мн': distance += 1

        elif class_ in (u'П', u'КР_ПРИЛ', u'МС-П', u'МС'):
            if self.case != u'им': distance += 1
            if self.gender != u'мр': distance += 1
            if self.number == u'мн': distance += 1

        elif class_ in (u'ПРИЧАСТИЕ', u'КР_ПРИЧАСТИЕ'):
            if self.time != u'прш': distance += 1
            if self.case != u'им': distance += 1
            if self.gender != u'мр': distance += 1
            if self.number == u'мн': distance += 1

        elif class_ ==  u'ИНФИНИТИВ':
            distance = 666 # we does not process infinitives

        else:
            raise TextgenException(u'unknown word class: "%s"' % class_)

        return distance


    def __unicode__(self):
        return (u'<%s, %s, %s, %s, %s, %s>' % (self.case, self.number, self.gender, self.time, self.person, self.word_case))

    def __str__(self): return self.__unicode__().encode('utf-8')



def efication(word):
    return word.replace(u'Ё', u'Е').replace(u'ё', u'е')

def get_gram_info(morph, word, tech_vocabulary={}):
    normalized = efication(word.lower())
    class_ = None

    if tech_vocabulary.get(normalized):
        class_ = tech_vocabulary[word.lower()][0] # TODO: ???

    # x = (u'МЯСО' == word)

    # if x: print '--------'

    properties = None

    result_class = class_

    for info in morph.get_graminfo(word.upper()):

        # if x: print info['class'], info['info']

        if class_ and info['class'] != class_:
            continue

        if u'имя' in info['info']:
            continue

        current_properties = Args(*info['info'].split(','))
        current_class = info['class']

        if not properties or properties.order_points(result_class) > current_properties.order_points(current_class):
            properties = current_properties
            result_class = current_class

    if not result_class:
        raise NoGrammarFound(u'can not find info about word: "%s"' % word)

    if properties is None:
        properties = Args()

    if normalized in tech_vocabulary:
        properties.update(*tech_vocabulary[normalized])

    # if x:
    #     print result_class, properties
    #     print '******************'


    return result_class, properties


def get_tech_vocabulary(tech_vocabulary_path):
    tech_vocabulary = {}
    if os.path.exists(tech_vocabulary_path):
        with open(tech_vocabulary_path) as f:
            tmp_tech_vocabulary = json.loads(f.read())
            for key, value in tmp_tech_vocabulary.items():
                tech_vocabulary[key] = [v.strip() for v in value.split(',')]
    return tech_vocabulary


def get_user_data_for_module(module):

    if 'name' not in module or 'description' not in module:
        return None

    data = {'name': module['name'],
            'description': module['description'],
            'types': {}}

    prefix = module['prefix']

    variables_verbose = module['variables_verbose']

    for suffix, type_data in module['types'].items():
        if 'name' not in type_data or 'description' not in type_data:
            continue

        variables = copy.deepcopy(module.get('variables', {}))
        variables.update(type_data.get('variables', {}))

        data['types']['%s_%s' % (prefix , suffix)] = {'name': type_data['name'],
                                                      'description': type_data['description'],
                                                      'example': type_data['phrases'][0][1],
                                                      'variables': variables.keys()}

    data['variables_verbose'] = variables_verbose


    return data

def import_texts(morph, source_dir, tech_vocabulary_path, voc_storage, dict_storage, tmp_dir='/tmp', check=False):
    from textgen.templates import Dictionary, Vocabulary, Template
    from textgen.words import WordBase

    vocabulary = Vocabulary()

    user_data = {'modules': {}}

    if not check:
        if os.path.exists(voc_storage):
            vocabulary.load(storage=voc_storage)

    dictionary = Dictionary()
    if os.path.exists(dict_storage):
        dictionary.load(storage=dict_storage)

    tech_vocabulary = get_tech_vocabulary(tech_vocabulary_path)

    for word in tech_vocabulary.keys():
        word = WordBase.create_from_string(morph, word.strip(), tech_vocabulary)
        dictionary.add_word(word)

    for filename in os.listdir(source_dir):

        if not filename.endswith('.json'):
            continue

        texts_path = os.path.join(source_dir, filename)

        if not os.path.isfile(texts_path):
            continue

        group = filename[:-5]

        if check:
            check_path = os.path.join(tmp_dir, 'textgen-files-check-'+filename)

            if os.path.exists(check_path) and os.path.getmtime(check_path) > os.path.getmtime(texts_path):
                print 'group "%s" has been already processed' % group
                continue

        print 'load "%s"' % group

        with open(texts_path) as f:
            data = json.loads(f.read())

            if group != data['prefix']:
                raise Exception('filename MUST be equal to prefix')

            for suffix in data['types']:
                if suffix == '':
                    raise Exception('type MUST be not equal to empty string')

            user_data['modules'][data['prefix']] = get_user_data_for_module(data)

            variables_verbose = data['variables_verbose']

            global_variables = data.get('variables', {})

            for variable_name in global_variables.keys():
                if not variables_verbose.get(variable_name):
                    raise Exception('no verbose name for variable "%s"' % variable_name)

            for suffix, type_ in data['types'].items():
                phrase_key = '%s_%s' % (group , suffix)

                vocabulary.register_type(phrase_key)

                if isinstance(type_, list):
                    phrases = type_
                    local_variables = {}
                else:
                    phrases = type_['phrases']
                    local_variables = type_.get('variables', {})

                for variable_name in local_variables.keys():
                    if not variables_verbose.get(variable_name):
                        raise Exception('no verbose name for variable "%s"' % variable_name)

                variables = copy.copy(global_variables)
                variables.update(local_variables)

                for phrase in phrases:
                    template_phrase, test_phrase = phrase

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

                    test_result_normalized = efication(test_result)
                    test_phrase_normalized = efication(test_phrase)

                    if test_result_normalized != test_phrase_normalized:
                        msg = None
                        for i in xrange(min(len(test_result_normalized), len(test_phrase_normalized))):
                            if test_result_normalized[i] != test_phrase_normalized[i]:
                                msg = '''
wrong test_render for phrase "%s"

prefix: "%s"

diff: %s|%s''' % (template_phrase, test_result_normalized[:i], test_result_normalized[i], test_phrase_normalized[i])
                                break

                        if msg is None:
                            msg = 'different len: "%s"|"%s"' % (test_result_normalized[i:], test_phrase_normalized[i:])

                        raise TextgenException(msg)

        if check:
            with open(check_path, 'w') as f:
                f.write('1')

    if not check:
        vocabulary.save(storage=voc_storage)
        dictionary.save(storage=dict_storage)

    return user_data
