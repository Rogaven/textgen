# coding: utf-8
import os
import pymorphy

from textgen.conf import APP_DIR, textgen_settings
from textgen.logic import import_texts

morph = pymorphy.get_morph(textgen_settings.PYMORPHY_DICTS_DIRECTORY)

import_texts(morph,
             source_dir=os.path.join(APP_DIR, 'fixtures', 'texts_src'),
             tech_vocabulary_path=os.path.join(APP_DIR, 'fixtures', 'vocabulary.json'),
             voc_storage='/tmp/voc.json',
             dict_storage='/tmp/dict.json',
             print_undefined_words=True)
