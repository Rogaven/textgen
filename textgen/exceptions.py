# coding: utf-8

class TextgenException(Exception):

    def __str__(self):
        return (u'%s' % (self.args[0],)).encode('utf-8')


class NormalFormNeeded(TextgenException): pass


class NoGrammarFound(TextgenException): pass
