#textgen

Библиотека для генерации русского текста.

позволяет из шаблонов вида:

```
"[[hero|им]] [{вытер|hero|прш}] оружие и [{принялся|hero|прш}] деловито обыскивать [{поверженый|mob|вн}] [[mob|вн]]"
```

получать такие строки:

```
"Привидение вытерло оружие и принялось деловито обыскивать поверженую крысу"
```

Разрабатывается для проекта the-tale.org (браузерная рпг с непрямым управлением персонажами)

Использует pymorphy (http://packages.python.org/pymorphy/) для автоматического получения морфологической информации, но может быть доработана для независимой работы

## быстрый старт

### устанавливаем

```
pip install pymorphy
pip install --upgrade git+git://github.com/Tiendil/textgen.git#egg=Textgen
mkdir ./tgen
cd ./tgen/
mkdir ./src
mkdir ./storage
```

### готовим

Создаём базу исходников для наших фраз. Обратите внимание, на следующие вещи:

- имя файла должно совпадать с полем prefix
- фразы групируются по типам (иными словами - по контекстами)
- для каждой фразы задаётся проверочная, т.к. очень просто допустить ошибку или опечатку в описании.                                            

./src/test.json
```
{
    "description": "",
    "prefix": "test",
    "types": {
        "start": {
            "description": "",
            "variables": {"hero": "привидение", "mob": "крыса"},
            "phrases": [
                ["[{Ужасный|mob|}] [[mob|им]] [{выскочил|mob|прш}] из кустов",
                 "Ужасная крыса выскочила из кустов"],
                ["Как [[hero|им]] ни [{пытался|hero|прш}] притвориться [{мёртвый|hero|тв}], [[mob|им]] всё равно [{пошел|mob|прш}] в наступление",
                 "Как привидение ни пыталось притвориться мёртвым, крыса всё равно пошла в наступление"],
                ["[[mob|им]] на горизонте, в бой!",
                 "Крыса на горизонте, в бой!"]
            ]
        },
        "battle_stun": {
            "description": "",
            "variables": {"actor": "привидение"},
            "phrases": [
                ["[[actor|им]] в шоке и не может атаковать",
                 "Привидение в шоке и не может атаковать"],
                ["[[actor|им]] с увлечением ловит летающие вокруг головы звёздочки",
                 "Привидение с увлечением ловит летающие вокруг головы звёздочки"],
                ["[[actor|им]] было [{подумал|actor|прш}] ударить, но [{оказался|actor|прш}] не в состоянии додумать мысль",
                 "Привидение было подумало ударить, но оказалось не в состоянии додумать мысль"]
            ]
        }
    }
}
```

Создаём вспомогательный словарь, в котором будет храниться дополнительная информация по словам, неоднозначно распознаваемым pymorphy. Для нас он не нужен, поэтому будет пустым.

./tech.json
```
{}
```

Скрипт, компилирующий нашу базу из исходников. 
Результат его работы попадает в каталог ./storage

- ./storage/dictionary.json - формы используемых слов. Слова, попавшие в этот файл не перетираются и не удаляются при повторных импортах. Сделано так из-за существенного процента ошибок pymorphy, которые приходится устранять руками.
- ./storage/vocabulary.json - скопилированые фразы

test_prepair.py
```python
# coding: utf-8
import pymorphy

from textgen import logic as textgen_logic
from textgen.conf import textgen_settings

morph = pymorphy.get_morph(textgen_settings.PYMORPHY_DICTS_DIRECTORY) # см. документацию по pymorphy

VOCABULARY_STORAGE = './storage/vocabulary.json'
DICTIONARY_STORAGE = './storage/dictionary.json'
TECH_VOCABULARY = './tech.json'

# загружаем фразы и слова из них
textgen_logic.import_texts(morph,
                           source_dir='./src/',
                           tech_vocabulary_path=TECH_VOCABULARY,
                           voc_storage=VOCABULARY_STORAGE,
                           dict_storage=DICTIONARY_STORAGE,
                           debug=True)

```

основной код, выводит три фразы подряд

test.py
```python
# coding: utf-8

from textgen.templates import Vocabulary, Dictionary

VOCABULARY_STORAGE = './storage/vocabulary.json'
DICTIONARY_STORAGE = './storage/dictionary.json'

vocabulary = Vocabulary()
vocabulary.load(storage=VOCABULARY_STORAGE)

dictionary = Dictionary()
dictionary.load(storage=DICTIONARY_STORAGE)

for i in xrange(3):
    template = vocabulary.get_random_phrase('test_start')
    # используем уже добалвенные слова, но поменяем их местами (по сравнению с проверочными в исходниках)
    print template.substitute(dictionary, {'mob': u'привидение', 'hero': u'крыса'})

```

### запускаем
```bash
python ./test_prepair.py
python ./test.py
```

результат
```
Как крыса ни пыталась притвориться мертвой, привидение всё равно пошло в наступление
ужасное привидение выскочило из кустов
Как крыса ни пыталась притвориться мертвой, привидение всё равно пошло в наступление
```