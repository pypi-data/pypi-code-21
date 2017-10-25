# coding: utf-8


def map_rus_to_lat(char):
    """ функция преобразует русские символы в такие же (по написанию) латинские """
    map_dict = {
        u'Е': u'E',
        u'Т': u'T',
        u'У': u'Y',
        u'О': u'O',
        u'Р': u'P',
        u'А': u'A',
        u'Н': u'H',
        u'К': u'K',
        u'Х': u'X',
        u'С': u'C',
        u'В': u'B',
        u'М': u'M',
    }
    # если буква есть в списке русских сиволов, преобразуем ее в латинский двойник
    if char in map_dict:
        return map_dict[char]
    else:
        return char


def transliterate(text, space=u' '):
    symbols = (
        u"абвгдеёзийклмнопрстуфхъыьэАБВГДЕЁЗИЙКЛМНОПРСТУФХЪЫЬЭ№" + u' ',
        u"abvgdeezijklmnoprstufh'y'eABVGDEEZIJKLMNOPRSTUFH'Y'E#" + space,
    )

    sequence = {
        u'ж': u'zh',
        u'ц': u'ts',
        u'ч': u'ch',
        u'ш': u'sh',
        u'щ': u'sch',
        u'ю': u'ju',
        u'я': u'ja',
        u'Ж': u'Zh',
        u'Ц': u'Ts',
        u'Ч': u'Ch',
        u'Ш': u'Sh',
        u'Ю': u'Ju',
        u'Щ': u'Sch',
        u'Я': u'Ja',
    }

    for char in sequence.keys():
        text = text.replace(char, sequence[char])

    tr = {ord(a): ord(b) for a, b in zip(*symbols)}
    result = text.translate(tr)
    return result
