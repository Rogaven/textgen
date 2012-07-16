# coding: utf-8
import os
import tempfile

import pymorphy

from unittest import TestCase

from textgen.words import Noun, Adjective, Verb, NounGroup, Fake
from textgen.templates import Args, Template, Dictionary, Vocabulary
from textgen.conf import APP_DIR, textgen_settings
from textgen.logic import import_texts
from textgen.exceptions import NormalFormNeeded

morph = pymorphy.get_morph(textgen_settings.PYMORPHY_DICTS_DIRECTORY)

class NounTest(TestCase):

    def test_create_from_baseword(self):
        noun = Noun.create_from_baseword(morph, u'обезьянка')
        self.assertEqual(noun.normalized, u'обезьянка')
        self.assertEqual(noun.properties, (u'жр',))
        self.assertEqual(noun.forms, (u'обезьянка',
                                      u'обезьянки',
                                      u'обезьянке',
                                      u'обезьянку',
                                      u'обезьянкой',
                                      u'обезьянке',
                                      u'обезьянки',
                                      u'обезьянок',
                                      u'обезьянкам',
                                      u'обезьянок',
                                      u'обезьянками',
                                      u'обезьянках'))

    def test_pluralize(self):
        noun = Noun.create_from_baseword(morph, u'монета')
        self.assertEqual(noun.normalized, u'монета')
        self.assertEqual(noun.pluralize(1, Args()), u'монета')
        self.assertEqual(noun.pluralize(2, Args()), u'монеты')
        self.assertEqual(noun.pluralize(3, Args()), u'монеты')
        self.assertEqual(noun.pluralize(5, Args()), u'монет')
        self.assertEqual(noun.pluralize(10, Args()), u'монет')
        self.assertEqual(noun.pluralize(11, Args()), u'монет')
        self.assertEqual(noun.pluralize(12, Args()), u'монет')
        self.assertEqual(noun.pluralize(21, Args()), u'монета')
        self.assertEqual(noun.pluralize(33, Args()), u'монеты')
        self.assertEqual(noun.pluralize(36, Args()), u'монет')
        self.assertEqual(noun.pluralize(113, Args()), u'монет')
        self.assertEqual(noun.pluralize(9003, Args()), u'монеты')

        self.assertEqual(noun.pluralize(1, Args(u'рд')), u'монеты')
        self.assertEqual(noun.pluralize(2, Args(u'рд')), u'монет')
        self.assertEqual(noun.pluralize(3, Args(u'рд')), u'монет')
        self.assertEqual(noun.pluralize(5, Args(u'рд')), u'монет')
        self.assertEqual(noun.pluralize(10, Args(u'рд')), u'монет')
        self.assertEqual(noun.pluralize(11, Args(u'рд')), u'монет')
        self.assertEqual(noun.pluralize(12, Args(u'рд')), u'монет')
        self.assertEqual(noun.pluralize(21, Args(u'рд')), u'монеты')
        self.assertEqual(noun.pluralize(33, Args(u'рд')), u'монет')
        self.assertEqual(noun.pluralize(36, Args(u'рд')), u'монет')
        self.assertEqual(noun.pluralize(113, Args(u'рд')), u'монет')
        self.assertEqual(noun.pluralize(9003, Args(u'рд')), u'монет')


        self.assertEqual(noun.pluralize(1, Args(u'вн')), u'монету')
        self.assertEqual(noun.pluralize(2, Args(u'вн')), u'монеты')
        self.assertEqual(noun.pluralize(3, Args(u'вн')), u'монеты')
        self.assertEqual(noun.pluralize(5, Args(u'вн')), u'монет')
        self.assertEqual(noun.pluralize(10, Args(u'вн')), u'монет')
        self.assertEqual(noun.pluralize(11, Args(u'вн')), u'монет')
        self.assertEqual(noun.pluralize(12, Args(u'вн')), u'монет')
        self.assertEqual(noun.pluralize(21, Args(u'вн')), u'монету')
        self.assertEqual(noun.pluralize(33, Args(u'вн')), u'монеты')
        self.assertEqual(noun.pluralize(36, Args(u'вн')), u'монет')
        self.assertEqual(noun.pluralize(113, Args(u'вн')), u'монет')
        self.assertEqual(noun.pluralize(9003, Args(u'вн')), u'монеты')

        self.assertEqual(noun.pluralize(1, Args(u'дт')), u'монете')
        self.assertEqual(noun.pluralize(2, Args(u'дт')), u'монетам')
        self.assertEqual(noun.pluralize(3, Args(u'дт')), u'монетам')
        self.assertEqual(noun.pluralize(5, Args(u'дт')), u'монетам')
        self.assertEqual(noun.pluralize(10, Args(u'дт')), u'монетам')
        self.assertEqual(noun.pluralize(11, Args(u'дт')), u'монетам')
        self.assertEqual(noun.pluralize(12, Args(u'дт')), u'монетам')
        self.assertEqual(noun.pluralize(21, Args(u'дт')), u'монете')
        self.assertEqual(noun.pluralize(33, Args(u'дт')), u'монетам')
        self.assertEqual(noun.pluralize(36, Args(u'дт')), u'монетам')
        self.assertEqual(noun.pluralize(113, Args(u'дт')), u'монетам')
        self.assertEqual(noun.pluralize(9003, Args(u'дт')), u'монетам')

        self.assertEqual(noun.pluralize(1, Args(u'тв')), u'монетой')
        self.assertEqual(noun.pluralize(2, Args(u'тв')), u'монетами')
        self.assertEqual(noun.pluralize(3, Args(u'тв')), u'монетами')
        self.assertEqual(noun.pluralize(5, Args(u'тв')), u'монетами')
        self.assertEqual(noun.pluralize(10, Args(u'тв')), u'монетами')
        self.assertEqual(noun.pluralize(11, Args(u'тв')), u'монетами')
        self.assertEqual(noun.pluralize(12, Args(u'тв')), u'монетами')
        self.assertEqual(noun.pluralize(21, Args(u'тв')), u'монетой')
        self.assertEqual(noun.pluralize(33, Args(u'тв')), u'монетами')
        self.assertEqual(noun.pluralize(36, Args(u'тв')), u'монетами')
        self.assertEqual(noun.pluralize(113, Args(u'тв')), u'монетами')
        self.assertEqual(noun.pluralize(9003, Args(u'тв')), u'монетами')

        self.assertEqual(noun.pluralize(1, Args(u'пр')), u'монете')
        self.assertEqual(noun.pluralize(2, Args(u'пр')), u'монетах')
        self.assertEqual(noun.pluralize(3, Args(u'пр')), u'монетах')
        self.assertEqual(noun.pluralize(5, Args(u'пр')), u'монетах')
        self.assertEqual(noun.pluralize(10, Args(u'пр')), u'монетах')
        self.assertEqual(noun.pluralize(11, Args(u'пр')), u'монетах')
        self.assertEqual(noun.pluralize(12, Args(u'пр')), u'монетах')
        self.assertEqual(noun.pluralize(21, Args(u'пр')), u'монете')
        self.assertEqual(noun.pluralize(33, Args(u'пр')), u'монетах')
        self.assertEqual(noun.pluralize(36, Args(u'пр')), u'монетах')
        self.assertEqual(noun.pluralize(113, Args(u'пр')), u'монетах')
        self.assertEqual(noun.pluralize(9003, Args(u'пр')), u'монетах')

    def test_get_form(self):
        noun = Noun.create_from_baseword(morph, u'обезьянка')
        self.assertEqual(noun.get_form(Args(u'рд', u'мн')), u'обезьянок')
        self.assertEqual(noun.get_form(Args(u'дт', u'ед')), u'обезьянке')

    def test_serialization(self):
        noun_1 = Noun.create_from_baseword(morph, u'обезьянка')
        data  = noun_1.serialize()

        noun_2 = Noun.deserialize(data)

        self.assertEqual(noun_1.normalized , noun_2.normalized)
        self.assertEqual(noun_1.forms, noun_2.forms)
        self.assertEqual(noun_1.properties, noun_2.properties)

    def test_normal_form(self):
        self.assertRaises(NormalFormNeeded, Noun.create_from_baseword, morph, u'обезьянки')
        Noun.create_from_baseword(morph, u'ножницы')


class NounGroupTest(TestCase):

    def test_create_from_baseword(self):
        group = NounGroup.create_from_baseword(morph, u'жирная крыса')
        self.assertEqual(group.normalized, u'жирная крыса')
        self.assertEqual(group.properties, (u'жр',))
        self.assertEqual(group.forms, (u'жирная крыса',
                                       u'жирной крысы',
                                       u'жирной крысе',
                                       u'жирную крысу',
                                       u'жирной крысой',
                                       u'жирной крысе',
                                       u'жирные крысы',
                                       u'жирных крыс',
                                       u'жирным крысам',
                                       u'жирная крыс', #???????? possible bug in pymorphy
                                       u'жирными крысами',
                                       u'жирных крысах'))

    def test_pluralize(self):
        group = NounGroup.create_from_baseword(morph, u'жирная крыса')
        self.assertEqual(group.pluralize(1, Args()), u'жирная крыса')
        self.assertEqual(group.pluralize(2, Args()), u'жирные крысы')
        self.assertEqual(group.pluralize(3, Args()), u'жирные крысы')
        self.assertEqual(group.pluralize(5, Args()), u'жирных крыс')
        self.assertEqual(group.pluralize(10, Args()), u'жирных крыс')
        self.assertEqual(group.pluralize(11, Args()), u'жирных крыс')
        self.assertEqual(group.pluralize(12, Args()), u'жирных крыс')
        self.assertEqual(group.pluralize(21, Args()), u'жирная крыса')
        self.assertEqual(group.pluralize(33, Args()), u'жирные крысы')
        self.assertEqual(group.pluralize(36, Args()), u'жирных крыс')

        self.assertEqual(group.pluralize(1, Args(u'дт')), u'жирной крысе')
        self.assertEqual(group.pluralize(2, Args(u'дт')), u'жирным крысам')
        self.assertEqual(group.pluralize(3, Args(u'дт')), u'жирным крысам')
        self.assertEqual(group.pluralize(5, Args(u'дт')), u'жирным крысам')
        self.assertEqual(group.pluralize(10, Args(u'дт')), u'жирным крысам')
        self.assertEqual(group.pluralize(11, Args(u'дт')), u'жирным крысам')
        self.assertEqual(group.pluralize(12, Args(u'дт')), u'жирным крысам')
        self.assertEqual(group.pluralize(21, Args(u'дт')), u'жирной крысе')
        self.assertEqual(group.pluralize(33, Args(u'дт')), u'жирным крысам')
        self.assertEqual(group.pluralize(36, Args(u'дт')), u'жирным крысам')

    def test_get_form(self):
        group = NounGroup.create_from_baseword(morph, u'жирная крыса')
        self.assertEqual(group.get_form(Args(u'рд', u'мн')), u'жирных крыс')
        self.assertEqual(group.get_form(Args(u'дт')), u'жирной крысе')

    def test_serialization(self):
        group_1 = NounGroup.create_from_baseword(morph, u'жирная крыса')
        data = group_1.serialize()

        group_2 = NounGroup.deserialize(data)

        self.assertEqual(group_1.normalized , group_2.normalized)
        self.assertEqual(group_1.forms, group_2.forms)
        self.assertEqual(group_1.properties, group_2.properties)

    def test_2_adjective(self):
        group = NounGroup.create_from_baseword(morph, u'белая жирная крыса')
        self.assertEqual(group.normalized, u'белая жирная крыса')
        self.assertEqual(group.properties, (u'жр',))
        self.assertEqual(group.forms, (u'белая жирная крыса',
                                       u'белой жирной крысы',
                                       u'белой жирной крысе',
                                       u'белую жирную крысу',
                                       u'белой жирной крысой',
                                       u'белой жирной крысе',
                                       u'белые жирные крысы',
                                       u'белых жирных крыс',
                                       u'белым жирным крысам',
                                       u'белая жирная крыс', #???????? possible bug in pymorphy
                                       u'белыми жирными крысами',
                                       u'белых жирных крысах'))

    def test_2_nouns(self):
        group = NounGroup.create_from_baseword(morph, u'тень автора')
        self.assertEqual(group.normalized, u'тень автора')
        self.assertEqual(group.properties, (u'жр',))
        # for f in group.forms:
        #     print f
        # print group.forms[1]
        self.assertEqual(group.forms, (u'тень автора',
                                       u'тени автора',
                                       u'тени автора',
                                       u'тень автора',
                                       u'тенью автора',
                                       u'тени автора',
                                       u'тени автора',
                                       u'теней автора',
                                       u'теням автора',
                                       u'теней автора', #???????? possible bug in pymorphy
                                       u'тенями автора',
                                       u'тенях автора'))

    def test_normal_form(self):
        self.assertRaises(NormalFormNeeded, NounGroup.create_from_baseword, morph, u'добрые обезьянки')
        NounGroup.create_from_baseword(morph, u'большие ножницы')


class AdjectiveTest(TestCase):

    def test_create_from_baseword(self):
        adj = Adjective.create_from_baseword(morph, u'глупый')
        self.assertEqual(adj.normalized, u'глупый')
        self.assertEqual(adj.forms[18], (u'глупый',
                                     u'глупого',
                                     u'глупому',
                                     u'глупый',
                                     u'глупым',
                                     u'глупом',
                                     u'глупая',
                                     u'глупой',
                                     u'глупой',
                                     u'глупую',
                                     u'глупой',
                                     u'глупой',
                                     u'глупое',
                                     u'глупого',
                                     u'глупому',
                                     u'глупое',
                                     u'глупым',
                                     u'глупом',
                                     u'глупые',
                                     u'глупых',
                                     u'глупым',
                                     u'глупый', #???????? possible bug in pymorphy
                                     u'глупыми',
                                     u'глупых')[18])

    def test_pluralize(self):
        adj = Adjective.create_from_baseword(morph, u'красивый')

        self.assertEqual(adj.normalized, u'красивый')

        self.assertEqual(adj.pluralize(1, Args()), u'красивый')
        self.assertEqual(adj.pluralize(2, Args()), u'красивые')
        self.assertEqual(adj.pluralize(3, Args()), u'красивые')
        self.assertEqual(adj.pluralize(5, Args()), u'красивых')
        self.assertEqual(adj.pluralize(10, Args()), u'красивых')
        self.assertEqual(adj.pluralize(11, Args()), u'красивых')
        self.assertEqual(adj.pluralize(12, Args()), u'красивых')
        self.assertEqual(adj.pluralize(21, Args()), u'красивый')
        self.assertEqual(adj.pluralize(33, Args()), u'красивые')
        self.assertEqual(adj.pluralize(36, Args()), u'красивых')

        self.assertEqual(adj.pluralize(1, Args(u'дт', u'жр')), u'красивой')
        self.assertEqual(adj.pluralize(2, Args(u'дт', u'жр')), u'красивым')
        self.assertEqual(adj.pluralize(3, Args(u'дт', u'жр')), u'красивым')
        self.assertEqual(adj.pluralize(5, Args(u'дт', u'жр')), u'красивым')
        self.assertEqual(adj.pluralize(10, Args(u'дт', u'жр')), u'красивым')
        self.assertEqual(adj.pluralize(11, Args(u'дт', u'жр')), u'красивым')
        self.assertEqual(adj.pluralize(12, Args(u'дт', u'жр')), u'красивым')
        self.assertEqual(adj.pluralize(21, Args(u'дт', u'жр')), u'красивой')
        self.assertEqual(adj.pluralize(33, Args(u'дт', u'жр')), u'красивым')
        self.assertEqual(adj.pluralize(36, Args(u'дт', u'жр')), u'красивым')

        self.assertEqual(adj.pluralize(1, Args(u'тв')), u'красивым')
        self.assertEqual(adj.pluralize(2, Args(u'тв')), u'красивыми')
        self.assertEqual(adj.pluralize(3, Args(u'тв')), u'красивыми')
        self.assertEqual(adj.pluralize(5, Args(u'тв')), u'красивыми')
        self.assertEqual(adj.pluralize(10, Args(u'тв')), u'красивыми')
        self.assertEqual(adj.pluralize(11, Args(u'тв')), u'красивыми')
        self.assertEqual(adj.pluralize(12, Args(u'тв')), u'красивыми')
        self.assertEqual(adj.pluralize(21, Args(u'тв')), u'красивым')
        self.assertEqual(adj.pluralize(33, Args(u'тв')), u'красивыми')
        self.assertEqual(adj.pluralize(36, Args(u'тв')), u'красивыми')


    def test_serialization(self):
        adj_1 = Adjective.create_from_baseword(morph, u'обезьянка')
        data = adj_1.serialize()

        adj_2 = Adjective.deserialize(data)

        self.assertEqual(adj_1.normalized , adj_2.normalized)
        self.assertEqual(adj_1.forms, adj_2.forms)
        self.assertEqual(adj_1.properties, adj_2.properties)

    def test_normal_form(self):
        self.assertRaises(NormalFormNeeded, Adjective.create_from_baseword, morph, u'добрые')


class VerbTest(TestCase):

    def test_create_from_baseword(self):
        verb = Verb.create_from_baseword(morph, u'говорил')
        self.assertEqual(verb.normalized, u'говорил')
        self.assertEqual(verb.forms, (u'говорил',
                                      u'говорила',
                                      u'говорило',
                                      u'говорили',
                                      u'говорю',
                                      u'говорим',
                                      u'говоришь',
                                      u'говорите',
                                      u'говорит',
                                      u'говорят',
                                      u'говорил',
                                      u'говорил',
                                      u'говорил',
                                      u'говорил',
                                      u'говорил',
                                      u'говорил',))

        verb = Verb.create_from_baseword(morph, u'поговорил')
        self.assertEqual(verb.normalized, u'поговорил')
        self.assertEqual(verb.forms, (u'поговорил',
                                      u'поговорила',
                                      u'поговорило',
                                      u'поговорили',
                                      u'поговорил',
                                      u'поговорил',
                                      u'поговорил',
                                      u'поговорил',
                                      u'поговорил',
                                      u'поговорил',
                                      u'поговорю',
                                      u'поговорим',
                                      u'поговоришь',
                                      u'поговорите',
                                      u'поговорит',
                                      u'поговорят',))

    def test_word_recover(self):
        verb = Verb.create_from_baseword(morph, u'восстановил')
        self.assertEqual(verb.normalized, u'восстановил')
        self.assertEqual(verb.forms, (u'восстановил',
                                      u'восстановила',
                                      u'восстановило',
                                      u'восстановили',
                                      u'восстановил',
                                      u'восстановил',
                                      u'восстановил',
                                      u'восстановил',
                                      u'восстановил',
                                      u'восстановил',
                                      u'восстановлю',
                                      u'восстановим',
                                      u'восстановишь',
                                      u'восстановите',
                                      u'восстановит',
                                      u'восстановят',))

    def test_pluralize(self):
        verb = Verb.create_from_baseword(morph, u'взметнулся')
        self.assertEqual(verb.pluralize(1, Args(u'прш', u'жр')), u'взметнулась')
        self.assertEqual(verb.pluralize(2, Args(u'прш', u'жр')), u'взметнулись')
        self.assertEqual(verb.pluralize(3, Args(u'прш', u'жр')), u'взметнулись')
        self.assertEqual(verb.pluralize(5, Args(u'прш', u'жр')), u'взметнулись')
        self.assertEqual(verb.pluralize(10, Args(u'прш', u'жр')), u'взметнулись')
        self.assertEqual(verb.pluralize(11, Args(u'прш', u'жр')), u'взметнулись')
        self.assertEqual(verb.pluralize(12, Args(u'прш', u'жр')), u'взметнулись')
        self.assertEqual(verb.pluralize(21, Args(u'прш', u'жр')), u'взметнулась')
        self.assertEqual(verb.pluralize(33, Args(u'прш', u'жр')), u'взметнулись')
        self.assertEqual(verb.pluralize(36, Args(u'прш', u'жр')), u'взметнулись')


    def test_serialization(self):
        verb_1 = Verb.create_from_baseword(morph, u'бежал')
        data = verb_1.serialize()

        verb_2 = Verb.deserialize(data)

        self.assertEqual(verb_1.normalized , verb_2.normalized)
        self.assertEqual(verb_1.forms, verb_2.forms)
        self.assertEqual(verb_1.properties, verb_2.properties)

    def test_normal_form(self):
        self.assertRaises(NormalFormNeeded, Verb.create_from_baseword, morph, u'бежит')
        self.assertRaises(NormalFormNeeded, Verb.create_from_baseword, morph, u'бежали')
        self.assertRaises(NormalFormNeeded, Verb.create_from_baseword, morph, u'бежала')
        Verb.create_from_baseword(morph, u'бежал')
        self.assertRaises(NormalFormNeeded, Verb.create_from_baseword, morph, u'побежит')
        self.assertRaises(NormalFormNeeded, Verb.create_from_baseword, morph, u'побежали')
        self.assertRaises(NormalFormNeeded, Verb.create_from_baseword, morph, u'побежала')
        Verb.create_from_baseword(morph, u'побежал')


class DictionaryTest(TestCase):

    def setUp(self):
        self.monkey = Noun.create_from_baseword(morph, u'обезьянка')
        self.silly = Adjective.create_from_baseword(morph, u'глупый')
        self.hit = Verb.create_from_baseword(morph, u'ударил')

    def test_create(self):
        dictionary = Dictionary()

        dictionary.add_word(self.monkey)
        dictionary.add_word(self.silly)
        dictionary.add_word(self.hit)

        self.assertEqual(dictionary.get_word(u'обезьянка'), self.monkey)
        self.assertEqual(dictionary.get_word(u'глупый'), self.silly)
        self.assertEqual(dictionary.get_word(u'ударил'), self.hit)

    def test_serialization(self):

        with tempfile.NamedTemporaryFile(delete=False) as f:
            dictionary = Dictionary()

            dictionary.add_word(self.monkey)
            dictionary.add_word(self.silly)
            dictionary.add_word(self.hit)

            dictionary.save(storage=f.name)

            dictionary = Dictionary()
            dictionary.load(storage=f.name)

            self.assertEqual(dictionary.get_word(u'обезьянка').normalized, u'обезьянка')
            self.assertEqual(dictionary.get_word(u'глупый').normalized, u'глупый')
            self.assertEqual(dictionary.get_word(u'ударил').normalized, u'ударил')


class VocabularyTest(TestCase):

    def setUp(self):
        self.t1 = Template.create(morph, u'ударить [[hero|вн]]')
        self.t2 = Template.create(morph, u'ударить [[hero|вн,мн]]')
        self.t3 = Template.create(morph, u'[{тенью|hero|тв}] [[hero|рд]]')

    def __assertChoices(self, voc):
        choosed_2 = False
        choosed_3 = False

        for i in xrange(100):
            self.assertEqual(voc.get_random_phrase('type_1').template, self.t1.template)

            choice = voc.get_random_phrase('type_2')
            if choice.template == self.t2.template:
                choosed_2 = True
            if choice.template == self.t3.template:
                choosed_3 = True
            self.assertTrue(choice.template in [self.t2.template, self.t3.template])

        self.assertTrue(choosed_2 and choosed_3)


    def test_create(self):

        voc = Vocabulary()

        voc.add_phrase('type_1', self.t1)
        voc.add_phrase('type_2', self.t2)
        voc.add_phrase('type_2', self.t3)

        self.__assertChoices(voc)

    def test_save_load(self):
        with tempfile.NamedTemporaryFile(delete=False) as f:
            voc = Vocabulary()

            voc.add_phrase('type_1', self.t1)
            voc.add_phrase('type_2', self.t2)
            voc.add_phrase('type_2', self.t3)

            voc.save(storage=f.name)

            voc = Vocabulary()

            voc.load(storage=f.name)

            self.__assertChoices(voc)



class TemplateTest(TestCase):

    def setUp(self):
        self.dictionary = Dictionary()
        self.dictionary.add_word(Noun.create_from_baseword(morph, u'обезьянка'))
        self.dictionary.add_word(Noun.create_from_baseword(morph, u'тень'))
        self.dictionary.add_word(Adjective.create_from_baseword(morph, u'глупый'))
        self.dictionary.add_word(Verb.create_from_baseword(morph, u'ударил'))
        self.dictionary.add_word(Adjective.create_from_baseword(morph, u'целый'))

    def test_externals(self):
        template = Template.create(morph, u'ударить [[hero|вн]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': u'обезьянка'}), u'ударить обезьянку')

        template = Template.create(morph, u'ударить [[hero|вн,мн]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': u'обезьянка' } ), u'ударить обезьянок')

    def test_partial_dependence(self):
        template = Template.create(morph, u'ударить [[hero|вн]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': (u'обезьянка', u'мн') } ), u'ударить обезьянок')


    def test_internals(self):
        template = Template.create(morph, u'[{тень|hero|тв}] [[hero|рд]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': (u'обезьянка', u'мн')} ), u'тенями обезьянок')

    def test_noun_dependences(self):
        template = Template.create(morph, u'[[shadow|hero|тв]] [[hero|рд]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': (u'обезьянка', u'мн'),
                                                               'shadow': u'тень'} ), u'тенями обезьянок')

    def test_numeral_1_dependences(self):
        template = Template.create(morph, u'[[number||]] [[hero|number|им]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': u'обезьянка',
                                                               'number': 1} ), u'1 обезьянка')

        template = Template.create(morph, u'[[number||]] [[hero|number|рд]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': u'обезьянка',
                                                               'number': 1} ), u'1 обезьянки')

        template = Template.create(morph, u'[[number||]] [[hero|number|дт]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': u'обезьянка',
                                                               'number': 1} ), u'1 обезьянке')

    def test_numeral_2_dependences(self):
        template = Template.create(morph, u'[[number||]] [[hero|number|им]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': u'обезьянка',
                                                               'number': 2} ), u'2 обезьянки')

        template = Template.create(morph, u'[[number||]] [[hero|number|рд]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': u'обезьянка',
                                                               'number': 2} ), u'2 обезьянок')

        template = Template.create(morph, u'[[number||]] [[hero|number|дт]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': u'обезьянка',
                                                               'number': 2} ), u'2 обезьянкам')

    def test_numeral_13_adj_dependences(self):
        template = Template.create(morph, u'[[number||]] [{целый|number|}]')
        self.assertEqual(template.substitute(self.dictionary, {'number': 13} ), u'13 целых')


    def test_numeral_5_dependences(self):
        template = Template.create(morph, u'[[number||]] [[hero|number|им]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': u'обезьянка',
                                                               'number': 5} ), u'5 обезьянок')

        template = Template.create(morph, u'[[number||]] [[hero|number|рд]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': u'обезьянка',
                                                               'number': 5} ), u'5 обезьянок')

        template = Template.create(morph, u'[[number||]] [[hero|number|дт]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': u'обезьянка',
                                                               'number': 5} ), u'5 обезьянкам')


    def test_dependences(self):
        template = Template.create(morph, u'[{глупый|hero|рд}] [[hero|рд]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': u'обезьянка'} ), u'глупой обезьянки')

        template = Template.create(morph, u'враг [{ударил|hero|буд,3л}] [[hero|вн]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': u'обезьянка'} ), u'враг ударит обезьянку')

        template = Template.create(morph, u'крыса [{ударил|прш,жр}] [[hero|вн]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': u'обезьянка'} ), u'крыса ударила обезьянку')


    def test_fake_substitutions(self):
        template = Template.create(morph, u'[{глупый|hero|рд}] [[hero|рд]]')
        self.assertEqual(template.substitute(self.dictionary, {'hero': Fake(u'19x5')} ), u'глупого 19x5')


class LoadDataTest(TestCase):

    def setUp(self):
        pass

    def test_load(self):
        with tempfile.NamedTemporaryFile(delete=False) as voc_f:
            with tempfile.NamedTemporaryFile(delete=False) as dict_f:
                import_texts(morph,
                             source_dir=os.path.join(APP_DIR, 'fixtures', 'texts_src'),
                             tech_vocabulary_path=os.path.join(APP_DIR, 'fixtures', 'vocabulary.json'),
                             voc_storage=voc_f.name,
                             dict_storage=dict_f.name)
