# coding: utf-8
import re
import itertools
import numbers
import random
import json

from textgen.exceptions import TextgenException
from textgen.words import WordBase, Fake, Numeral
from textgen.logic import efication, Args, PROPERTIES

class Dictionary(object):

    def __init__(self):
        self.data = {}

    def add_word(self, word, overwrite=False):
        if not overwrite and word.normalized in self.data:
            # TODO: add test
            return
        self.data[efication(word.normalized)] = word

    def get_word(self, normalized):
        normalized = efication(normalized)
        if normalized in self.data:
            return self.data[normalized]
        return Fake(u'<word not found: %s>' % normalized)

    def clear(self):
        self.data = {}

    def save(self, storage):
        data = {}
        for norm, word in self.data.items():
            data[norm] = word.serialize()

        with open(storage, 'w') as f:
            f.write(json.dumps(data, ensure_ascii=False, check_circular=True, allow_nan=False, indent=2).encode('utf-8'))

    def load(self, storage):
        with open(storage, 'r') as f:
            raw_data = f.read()
            if not raw_data:
                return
            data = json.loads(raw_data)

        for word_data in data.values():
            self.add_word(WordBase.deserialize(word_data))

    def get_undefined_words(self):
        result = []
        for key, word in self.data.items():
            if not word.has_forms:
                result.append(key)
        return result


class Vocabulary(object):

    def __init__(self):
        self.data = {}

    def add_phrase(self, type_, template):
        if type_ not in self.data:
            raise TextgenException('type %s has not registered in vocabulary' % type_)
        self.data[type_].append(template)

    def register_type(self, type_):
        if type_ in self.data:
            raise TextgenException('type %s has already registered in vocabulary' % type_)
        self.data[type_] = []

    def get_random_phrase(self, type_, default=None):
        if type_ in self.data and self.data[type_]:
            return random.choice(self.data[type_])
        return default

    def __contains__(self, type_):
        return type_ in self.data

    def clear(self):
        self.data = {}

    def save(self, storage):
        data = {}
        for type_, phrases in self.data.items():
            data[type_] = [phrase.serialize() for phrase in phrases]

        with open(storage, 'w') as f:
            f.write(json.dumps(data, ensure_ascii=False, check_circular=True, allow_nan=False, indent=2).encode('utf-8'))

    def load(self, storage):
        with open(storage, 'r') as f:
            raw_data = f.read()
            if not raw_data:
                return
            data = json.loads(raw_data)

        for type_, phrases in data.items():
            self.data[type_] = [Template.deserialize(phrase_data) for phrase_data in phrases]



class Template(object):

    # [[external_id|dependece|dependece|arguments]]
    EXTERNAL_REGEX = re.compile(u'\[\[[^\]]+\]\]', re.UNICODE)

    # [{internal_id|dependece|dependece|arguments}]
    INTERNAL_REGEX = re.compile(u'\[\{[^\]]+\}\]', re.UNICODE)

    def __init__(self, template, externals, internals):
        self.template = template
        self.externals = externals
        self.internals = internals

    @classmethod
    def prepair_words(cls, morph, regex, src, subsitute_pattern, is_internal, tech_vocabulary={}):
        words = []
        word_macroses = regex.findall(src)

        for i, word_macros in enumerate(word_macroses):
            slugs = word_macros[2:-2].split('|')

            id_ = slugs[0]
            args = u''
            if len(slugs) > 1:
                args = slugs[-1]
            dependences = slugs[1:-1]

            if dependences == ['']: dependences = ()

            str_id = subsitute_pattern % i
            src = src.replace(word_macros, '%%(%s)s' % str_id)

            # if is_internal:
            #     source = efication(id_.upper())
            #     class_, properties = get_gram_info(morph, source, tech_vocabulary)

            arguments = tuple(args.split(u','))
            if arguments == (u'',):
                arguments = ()

            words.append((id_, dependences, str_id, arguments, id_))

        return src, words


    @classmethod
    def create(cls, morph, src, available_externals=[], tech_vocabulary={}):
        internals = []

        src, externals = cls.prepair_words(morph, cls.EXTERNAL_REGEX, src, 'e_%d', False, tech_vocabulary)
        src, internals = cls.prepair_words(morph, cls.INTERNAL_REGEX, src, 'i_%d', True, tech_vocabulary)

        #check arguments
        for id_, dependences, str_id, arguments, word_src in itertools.chain(externals, internals):
            if not all([PROPERTIES.is_argument_available(arg) for arg in arguments]):
                raise TextgenException(u'wrong arguments: (%s) in template %s' % (','.join(arguments), src) )

        #check externals
        if available_externals:
            used_externals = []
            for id_, dependences, str_id, arguments, word_src in externals:
                used_externals.append(id_)
                used_externals.extend(dependences)
            for id_, dependences, str_id, arguments, word_src in internals:
                used_externals.extend(dependences)
            if set(used_externals) - set(available_externals):
                raise TextgenException(u'wrong externals in template %s: [%s]' % (src, ', '.join(set(used_externals) - set(available_externals))))

        return cls(src, externals, internals)

    def get_internal_words(self):
        return [word_src for normalized, dependences, str_id, arguments, word_src in self.internals]

    def _preprocess_externals(self, dictionary, externals):
        processed_externals = {}

        for external_id, external in externals.items():
            additional_args = ()
            if isinstance(external, tuple):
                normalized, additional_args = external
                additional_args = additional_args.split(u',') if isinstance(additional_args, basestring) else additional_args
            else:
                normalized = external

            if isinstance(normalized, numbers.Number):
                word = Numeral(normalized)
                arguments = Args()
            elif isinstance(normalized, WordBase):
                word = normalized
                arguments = Args(*word.properties)
            else:
                word = dictionary.get_word(efication(normalized))
                arguments = Args(*word.properties)

            arguments.update(*additional_args)

            processed_externals[external_id] = (word, arguments)

        return processed_externals

    def _create_substitution(self, word, arguments, dependences, externals, args):
        number = None

        for dependence in dependences:
            dependence_word, dependence_args = externals[dependence]
            if isinstance(dependence_word, Numeral):
                number = dependence_word
            else:
                word.update_args(arguments, dependence_word, dependence_args)

        arguments.update(*args)

        if number is not None:
            word.update_args(arguments, number, arguments.get_copy())

        return word.get_form(arguments)


    def substitute(self, dictionary, externals):

        substitutions = {}
        processed_externals = self._preprocess_externals(dictionary, externals)

        for external_id, dependences, str_id, args, word_src in self.externals:
            word, arguments = processed_externals[external_id]
            substitutions[str_id] = self._create_substitution(word, arguments.get_copy(), dependences, processed_externals, args)

        for internal_str, dependences, str_id, args, word_src in self.internals:
            word = dictionary.get_word(internal_str)
            substitutions[str_id] = self._create_substitution(word, Args(), dependences, processed_externals, args)


        return self.template % substitutions


    def serialize(self):
        return {'template': self.template,
                'internals': self.internals,
                'externals': self.externals}

    @classmethod
    def deserialize(cls, data):
        return cls(data['template'], data['externals'], data['internals'])
