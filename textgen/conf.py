# coding: utf-8
import os

APP_DIR = os.path.abspath(os.path.dirname(__file__))

class TextgenSettings(object):

    def __init__(self,
                 texts_directory=os.path.join(APP_DIR, 'fixtures'),
                 pymorphy_dicts_directory=os.path.join(APP_DIR, 'dicts', 'ru_sqlite')):
        self.TEXTS_DIRECTORY = texts_directory
        self.PYMORPHY_DICTS_DIRECTORY = pymorphy_dicts_directory

textgen_settings = TextgenSettings()
