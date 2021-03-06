# coding: utf-8

from textgen.exceptions import TextgenException, NormalFormNeeded, NoGrammarFound
from textgen.logic import efication, get_gram_info, PROPERTIES

class WORD_TYPE:
    NOUN = 1
    ADJECTIVE = 2
    VERB = 3
    NUMERAL = 4
    NOUN_GROUP = 5
    FAKE = 6
    PARTICIPLE = 7
    SHORT_PARTICIPLE = 8
    PRONOUN = 9

WORD_TYPES_IDS_TO_WORD_TYPES = {u'сущ': WORD_TYPE.NOUN,
                                u'прил': WORD_TYPE.ADJECTIVE,
                                u'гл': WORD_TYPE.VERB,
                                u'числ': WORD_TYPE.NUMERAL,
                                u'сущ гр': WORD_TYPE.NOUN_GROUP,
                                u'фальш': WORD_TYPE.FAKE,
                                u'прич': WORD_TYPE.PARTICIPLE,
                                u'кр прич': WORD_TYPE.SHORT_PARTICIPLE,
                                u'мс': WORD_TYPE.PRONOUN}

WORD_CONSTRUCTORS = {}

class WordBase(object):

    TYPE = None

    def __init__(self, normalized, forms=[], properties=()):
        self.normalized = normalized
        self.forms = tuple(forms)
        self.properties = tuple(properties)

    @staticmethod
    def _pluralize_args(number, args):
        number %= 100

        if number % 10 == 1 and number != 11:
            args.update(u'ед')
        elif 2 <= number % 10 <= 4 and not (12 <= number <= 14):
            args.update(u'мн')
        else:
            args.update(u'мн')
            if args.case in (u'им', u'вн'):
                args.update(u'рд')

        return args

    def get_form(self, args):
        word = self._get_form(args)

        if args.word_case == u'загл':
            word = word[0].upper() + word[1:]

        return word

    def _get_form(self, args):
        raise NotImplementedError

    @property
    def has_forms(self): return self.forms # boolean

    @classmethod
    def pluralize_args(cls, number, args):
        raise NotImplementedError

    def pluralize(self, number, args):
        return self.get_form(self.pluralize_args(number, args.get_copy()))

    def update_args(self, arguments, dependence_class, dependence_args):
        raise NotImplementedError

    @classmethod
    def create_from_baseword(cls, src, tech_vocabulary={}):
        raise NotImplementedError

    @staticmethod
    def create_from_string(morph, string, tech_vocabulary={}):
        normalized = efication(string.upper())

        if ' ' in string:
            return WORD_CONSTRUCTORS[WORD_TYPE.NOUN_GROUP].create_from_baseword(morph, string, tech_vocabulary)

        class_, properties = get_gram_info(morph, normalized, tech_vocabulary)

        if class_ == u'С':
            return WORD_CONSTRUCTORS[WORD_TYPE.NOUN].create_from_baseword(morph, string, tech_vocabulary)
        elif class_ == u'П':
            return WORD_CONSTRUCTORS[WORD_TYPE.ADJECTIVE].create_from_baseword(morph, string, tech_vocabulary)
        elif class_ == u'КР_ПРИЛ':
            return WORD_CONSTRUCTORS[WORD_TYPE.ADJECTIVE].create_from_baseword(morph, string, tech_vocabulary)
        elif class_ == u'Г':
            return WORD_CONSTRUCTORS[WORD_TYPE.VERB].create_from_baseword(morph, string, tech_vocabulary)
        elif class_ == u'ПРИЧАСТИЕ':
            return WORD_CONSTRUCTORS[WORD_TYPE.PARTICIPLE].create_from_baseword(morph, string, tech_vocabulary)
        elif class_ == u'КР_ПРИЧАСТИЕ':
            return WORD_CONSTRUCTORS[WORD_TYPE.SHORT_PARTICIPLE].create_from_baseword(morph, string, tech_vocabulary)
        elif class_ == u'МС':
            return WORD_CONSTRUCTORS[WORD_TYPE.PRONOUN].create_from_baseword(morph, string, tech_vocabulary)
        elif class_ == u'МС-П':
            return WORD_CONSTRUCTORS[WORD_TYPE.ADJECTIVE].create_from_baseword(morph, string, tech_vocabulary)
        else:
            raise TextgenException(u'unknown word type: %s of word: %s' % (class_, string) )

    def serialize(self):
        return {'normalized': self.normalized,
                'type': self.TYPE,
                'forms': self.forms,
                'properties': self.properties}

    @staticmethod
    def deserialize(data):
        return WORD_CONSTRUCTORS[data['type']](normalized=data['normalized'],
                                               forms=data['forms'],
                                               properties=data['properties'])

    def __eq__(self, other):
        return (self.normalized == other.normalized and
                self.forms == other.forms and
                self.properties == other.properties)



class Fake(WordBase):

    TYPE = WORD_TYPE.FAKE

    def __init__(self, word):
        super(Fake, self).__init__(normalized=word.lower())
        self.forms = [word]

    def _get_form(self, args):
        return self.forms[0]

    @classmethod
    def pluralize_args(cls, number, args):
        return args

    def update_args(self, arguments, dependence, dependence_args):
        pass


class Noun(WordBase):

    TYPE = WORD_TYPE.NOUN
    FORMS_NUMBER = len(PROPERTIES.NUMBERS) * len(PROPERTIES.CASES)

    @classmethod
    def fast_construct(cls, base_word):
        return cls(normalized=base_word,
                   forms=[base_word] * cls.FORMS_NUMBER,
                   properties=(u'мр',))

    @property
    def gender(self): return self.properties[0]

    @property
    def is_valid(self):
        return len(self.forms) == self.FORMS_NUMBER

    def _get_form(self, args):
        if not self.forms:
            return self.normalized
        return self.forms[PROPERTIES.NUMBERS.index(args.number) * len(PROPERTIES.CASES) + PROPERTIES.CASES.index(args.case)]

    @classmethod
    def pluralize_args(cls, number, args):
        return cls._pluralize_args(number, args)

    def update_args(self, arguments, dependence, dependence_args):
        if isinstance(dependence, Numeral):
            self.pluralize_args(dependence.normalized, arguments)
            return

        arguments.number = dependence_args.number


    @classmethod
    def create_from_baseword(cls, morph, src, tech_vocabulary={}):
        normalized = efication(src.upper())
        try:
            class_, properties = get_gram_info(morph, normalized, tech_vocabulary)
        except NoGrammarFound:
            return cls(normalized=src)

        if u'им' != properties.case or (u'ед' != properties.number and properties.gender in (u'мр', u'ср', u'жр')):
            raise NormalFormNeeded(u'word "%s" not in normal form: %s' % (src, properties))

        forms = []

        for number in PROPERTIES.NUMBERS:
            for case in PROPERTIES.CASES:
                forms.append(morph.inflect_ru(normalized, u'%s,%s' % (case, number), class_ ).lower() )

        return cls(normalized=src, forms=forms, properties=[properties.gender])


class Numeral(WordBase):

    TYPE = WORD_TYPE.NUMERAL

    def __init__(self, number):
        super(Numeral, self).__init__(normalized=number)

    def _get_form(self, args):
        return self.normalized

    def update_args(self, arguments, dependence, dependence_args):
        pass


class Adjective(WordBase):

    TYPE = WORD_TYPE.ADJECTIVE

    def _get_form(self, args):
        if not self.forms:
            return self.normalized

        if args.number == u'ед':
            return self.forms[PROPERTIES.GENDERS.index(args.gender) * len(PROPERTIES.CASES) + PROPERTIES.CASES.index(args.case)]
        else:
            delta = len(PROPERTIES.CASES) * len(PROPERTIES.GENDERS)
            return self.forms[delta + PROPERTIES.CASES.index(args.case)]

    @classmethod
    def pluralize_args(cls, number, args):
        return cls._pluralize_args(number, args)


    def update_args(self, arguments, dependence, dependence_args):

        if isinstance(dependence, Numeral):
            self.pluralize_args(dependence.normalized, arguments)
            return

        arguments.number = dependence_args.number
        arguments.gender = dependence_args.gender
        arguments.case = dependence_args.case


    @classmethod
    def create_from_baseword(cls, morph, src, tech_vocabulary={}):
        normalized = efication(src.upper())
        try:
            class_, properties = get_gram_info(morph, normalized, tech_vocabulary)
        except NoGrammarFound:
            return cls(normalized=src)

        if u'им' != properties.case or u'ед' != properties.number:
            raise NormalFormNeeded(u'word "%s" not in normal form: %s' % (src, properties))

        forms = []

        # single
        for gender in PROPERTIES.GENDERS:
            for case in PROPERTIES.CASES:
                forms.append(morph.inflect_ru(normalized, u'%s,%s,ед' % (case, gender), class_).lower() )

        #multiple
        for case in PROPERTIES.CASES:
            forms.append(morph.inflect_ru(normalized, u'%s,%s' % (case, u'мн'), class_).lower() )

        return cls(normalized=src, forms=forms, properties=[])


class Pronoun(Adjective):

    TYPE = WORD_TYPE.PRONOUN

    @classmethod
    def create_from_baseword(cls, morph, src, tech_vocabulary={}):
        normalized = efication(src.upper())

        # pymorphy do not change gender of PRONOUNS, and we always need some words, so we hardcode them

        if normalized == u'ОН':
            return cls(normalized=src,
                       forms=(u'он', u'его', u'ему', u'его', u'им', u'нем',
                              u'она', u'ее', u'ей', u'ее', u'ей', u'ней',
                              u'оно', u'его', u'ему', u'его', u'им', u'нём',
                              u'они', u'их', u'им', u'их',  u'ими', u'них'),
                       properties=[])

        if normalized == u'Я':
            return cls(normalized=src,
                       forms=(u'я', u'меня', u'мне', u'меня', u'мной', u'мне',
                              u'я', u'меня', u'мне', u'меня', u'мной', u'мне',
                              u'я', u'меня', u'мне', u'меня', u'мной', u'мне',
                              u'я', u'меня', u'мне', u'меня', u'мной', u'мне'),
                       properties=[])

        return Adjective.create_from_baseword(morph, src, tech_vocabulary)



class Verb(WordBase):

    TYPE = WORD_TYPE.VERB

    def _get_form(self, args):

        if not self.forms:
            return self.normalized

        if args.time == u'прш':
            if args.number == u'мн':
                return self.forms[3]
            else:
                return self.forms[PROPERTIES.GENDERS.index(args.gender)]
        elif args.time == u'нст':
            delta = len(PROPERTIES.GENDERS) + 1
            return self.forms[delta + len(PROPERTIES.NUMBERS) * PROPERTIES.PERSONS.index(args.person) + PROPERTIES.NUMBERS.index(args.number)]
        elif args.time == u'буд':
            delta = len(PROPERTIES.GENDERS) + 1 + len(PROPERTIES.NUMBERS) * len(PROPERTIES.PERSONS)
            return self.forms[delta + len(PROPERTIES.NUMBERS) * PROPERTIES.PERSONS.index(args.person) + PROPERTIES.NUMBERS.index(args.number)]

    @classmethod
    def pluralize_args(cls, number, args):
        return cls._pluralize_args(number, args)

    def update_args(self, arguments, dependence, dependence_args):
        if isinstance(dependence, Numeral):
            self.pluralize_args(dependence.normalized, arguments)
            return

        arguments.number = dependence_args.number
        arguments.gender = dependence_args.gender



    @classmethod
    def create_from_baseword(cls, morph, src, tech_vocabulary={}):
        normalized = efication(src.upper())
        try:
            class_, properties = get_gram_info(morph, normalized, tech_vocabulary)
        except NoGrammarFound:
            return cls(normalized=src)

        if u'прш' != properties.time or u'ед' != properties.number or u'мр' != properties.gender:
            raise NormalFormNeeded(u'word "%s" not in normal form: %s' % (src, properties))

        base = morph.inflect_ru(normalized, u'ед,мр', u'Г')

        forms = [morph.inflect_ru(base, u'прш,мр,ед').lower(),
                 morph.inflect_ru(base, u'прш,жр,ед').lower(),
                 morph.inflect_ru(base, u'прш,ср,ед').lower(),
                 morph.inflect_ru(base, u'прш,мн').lower(),
                 morph.inflect_ru(base, u'нст,1л,ед').lower(),
                 morph.inflect_ru(base, u'нст,1л,мн').lower(),
                 morph.inflect_ru(base, u'нст,2л,ед').lower(),
                 morph.inflect_ru(base, u'нст,2л,мн').lower(),
                 morph.inflect_ru(base, u'нст,3л,ед').lower(),
                 morph.inflect_ru(base, u'нст,3л,мн').lower(),
                 morph.inflect_ru(base, u'буд,1л,ед').lower(),
                 morph.inflect_ru(base, u'буд,1л,мн').lower(),
                 morph.inflect_ru(base, u'буд,2л,ед').lower(),
                 morph.inflect_ru(base, u'буд,2л,мн').lower(),
                 morph.inflect_ru(base, u'буд,3л,ед').lower(),
                 morph.inflect_ru(base, u'буд,3л,мн').lower()]

        return cls(normalized=src, forms=forms, properties=[])


class Participle(WordBase):

    TYPE = WORD_TYPE.PARTICIPLE

    def _get_form(self, args):

        if not self.forms:
            return self.normalized

        delta = 0

        if args.time != u'прш':
            delta = len(PROPERTIES.CASES) * len(PROPERTIES.GENDERS) + len(PROPERTIES.CASES)

        if args.number == u'ед':
            return self.forms[delta + PROPERTIES.GENDERS.index(args.gender) * len(PROPERTIES.CASES) + PROPERTIES.CASES.index(args.case)]
        else:
            delta += len(PROPERTIES.CASES) * len(PROPERTIES.GENDERS)
            return self.forms[delta + PROPERTIES.CASES.index(args.case)]

    @classmethod
    def pluralize_args(cls, number, args):
        return cls._pluralize_args(number, args)

    def update_args(self, arguments, dependence, dependence_args):
        if isinstance(dependence, Numeral):
            self.pluralize_args(dependence.normalized, arguments)
            return

        arguments.number = dependence_args.number
        arguments.case = dependence_args.case
        arguments.gender = dependence_args.gender



    @classmethod
    def create_from_baseword(cls, morph, src, tech_vocabulary={}):
        normalized = efication(src.upper())
        try:
            class_, properties = get_gram_info(morph, normalized, tech_vocabulary)
        except NoGrammarFound:
            return cls(normalized=src)

        if properties.time not in (u'прш', u'нст') or u'ед' != properties.number or u'мр' != properties.gender or u'им' != properties.case:
            raise NormalFormNeeded(u'word "%s" not in normal form: %s' % (src, properties))

        forms = []

        for time in (u'прш', u'нст'):
            # single
            for gender in PROPERTIES.GENDERS:
                for case in PROPERTIES.CASES:
                    forms.append(morph.inflect_ru(normalized, u'%s,%s,%s,ед' % (time, case, gender), class_).lower() )

            #multiple
            for case in PROPERTIES.CASES:
                forms.append(morph.inflect_ru(normalized, u'%s,%s,%s' % (time, case, u'мн'), class_).lower() )

        return cls(normalized=src, forms=forms, properties=[])

class ShortParticiple(WordBase):

    TYPE = WORD_TYPE.SHORT_PARTICIPLE

    def _get_form(self, args):

        if not self.forms:
            return self.normalized

        delta = 0

        if args.time != u'прш':
            delta = len(PROPERTIES.GENDERS) + 1

        if args.number == u'ед':
            return self.forms[delta + PROPERTIES.GENDERS.index(args.gender)]
        else:
            delta += len(PROPERTIES.GENDERS)
            return self.forms[delta]

    @classmethod
    def pluralize_args(cls, number, args):
        return cls._pluralize_args(number, args)

    def update_args(self, arguments, dependence, dependence_args):

        if isinstance(dependence, Numeral):
            self.pluralize_args(dependence.normalized, arguments)
            return

        arguments.number = dependence_args.number
        arguments.case = dependence_args.case
        arguments.gender = dependence_args.gender


    @classmethod
    def create_from_baseword(cls, morph, src, tech_vocabulary={}):
        normalized = efication(src.upper())
        try:
            class_, properties = get_gram_info(morph, normalized, tech_vocabulary)
        except NoGrammarFound:
            return cls(normalized=src)

        if u'прш' != properties.time or u'ед' != properties.number or u'мр' != properties.gender:
            raise NormalFormNeeded(u'word "%s" not in normal form: %s' % (src, properties))

        forms = []

        for time in (u'прш', u'нст'):
            for gender in PROPERTIES.GENDERS:
                forms.append(morph.inflect_ru(normalized, u'%s,%s,ед' % (time, gender), class_).lower() )

            forms.append(morph.inflect_ru(normalized, u'%s,мн' % (time, ), class_).lower() )

        return cls(normalized=src, forms=forms, properties=[])



class NounGroup(Noun):

    TYPE = WORD_TYPE.NOUN_GROUP

    @classmethod
    def create_from_baseword(cls, morph, src, tech_vocabulary={}):
        '''
        one noun MUST be in им
        there are problems with nouns in multiple number: рога
        '''
        main_noun = None
        main_properties = None

        phrase = []

        for word in src.split(' '):
            if word:
                try:
                    class_, properties = get_gram_info(morph, efication(word.upper()), tech_vocabulary)
                except NoGrammarFound:
                    return cls(normalized=src)

                if class_ == u'С':
                    if u'им' == properties.case and (u'ед' == properties.number or properties.gender == u'мн'):
                        main_noun = word
                        main_properties = properties
                        phrase.append((class_, efication(word).upper(), False))
                    else:
                        phrase.append((class_, efication(word).upper(), True))
                else:
                    phrase.append((class_, efication(word).upper(), False))

        if not main_noun:
            # return cls(normalized=src)
            raise NormalFormNeeded('no main noun found in phrase "%s"' % src)

        forms = []

        for number in PROPERTIES.NUMBERS:

            additional_properties = []
            # if number == u'ед':
            #     additional_properties = [properties.gender]

            for case in PROPERTIES.CASES:
                phrase_form = []

                for class_, word, constant in phrase:
                    if constant:
                        phrase_form.append(word.lower())
                    else:
                        phrase_form.append(morph.inflect_ru(word, u','.join([case, number]+additional_properties), class_ ).lower())
                forms.append( ' '.join(phrase_form))

        return cls(normalized=src, forms=forms, properties=[main_properties.gender])



WORD_CONSTRUCTORS = dict([(class_.TYPE, class_)
                          for class_name, class_ in globals().items()
                          if isinstance(class_, type) and issubclass(class_, WordBase) and class_ != WordBase])
