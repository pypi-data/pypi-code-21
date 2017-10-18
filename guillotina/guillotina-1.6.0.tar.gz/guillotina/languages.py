# -*- encoding: utf-8 -*-
from guillotina import configure
from guillotina.interfaces import IDefaultLayer
from guillotina.interfaces import ILanguage


class IEN(ILanguage):
    pass


class IENUS(IEN):
    pass


class ICA(ILanguage):
    pass


class IFI(ILanguage):
    pass


class DefaultLanguage(object):
    def translate(self):
        return self.context


@configure.adapter(
    for_=IDefaultLayer,
    provides=IEN)
class EN(DefaultLanguage):
    def __init__(self, content):
        self.content = content


@configure.adapter(
    for_=IDefaultLayer,
    provides=ICA)
class CA(DefaultLanguage):
    def __init__(self, content):
        self.content = content


@configure.adapter(
    for_=IDefaultLayer,
    provides=IFI)
class FI(DefaultLanguage):
    def __init__(self, content):
        self.content = content


@configure.adapter(
    for_=IDefaultLayer,
    provides=IENUS)
class ENUS(DefaultLanguage):
    def __init__(self, content):
        self.content = content


# This is a dictionary of dictonaries:
#
# 'langcode-variation' : {'native' : 'Native name',
#                         'name' : 'English name'}
#
# This list follows ISO-639-1. The list retains entries for mo and sh,
# even tough these have later been deprecated from the standard.

_languagelist = {
    'aa': {'native': 'магIарул мацI',
           'name': 'Afar'},
    'ab': {'native': 'бызшәа',
           'name': 'Abkhazian'},
    'ae': {'native': 'avesta',
           'name': 'Avestan'},
    'af': {'native': 'Afrikaans',
           'name': 'Afrikaans'},
    'ak': {'native': 'Akan',
           'name': 'Akan'},
    'am': {'native': 'አማርኛ',
           'name': 'Amharic'},
    'an': {'native': 'aragonés',
           'name': 'Aragonese'},
    'ar': {'native': 'العربية',
           'name': 'Arabic'},
    'as': {'native': 'অসমিয়া',
           'name': 'Assamese'},
    'ay': {'native': 'Aymara',
           'name': 'Aymara'},
    'az': {'native': 'Azəri Türkçəsi',
           'name': 'Azerbaijani'},
    'ba': {'native': 'Bashkir',
           'name': 'Bashkir'},
    'be': {'native': 'Беларускі',
           'name': 'Belarussian'},
    'bg': {'native': 'Български',
           'name': 'Bulgarian'},
    'bh': {'native': 'Bihari',
           'name': 'Bihari'},
    'bi': {'native': 'Bislama',
           'name': 'Bislama'},
    'bm': {'native': 'bamanankan',
           'name': 'Bambara'},
    'bn': {'native': 'বাংলা',
           'name': 'Bengali'},
    'bo': {'native': 'བོད་སྐད་',
           'name': 'Tibetan'},
    'br': {'native': 'brezhoneg',
           'name': 'Breton'},
    'bs': {'native': 'Bosanski',
           'name': 'Bosnian'},
    'ca': {'native': 'Català',
           'name': 'Catalan'},
    'ce': {'native': 'нохчийн мотт',
           'name': 'Chechen'},
    'ch': {'native': 'Chamor',
           'name': 'Chamorro'},
    'co': {'native': 'Cors',
           'name': 'Corsican'},
    'cr': {'native': 'ᓀᐦᐃᔭᐍᐏᐣ',
           'name': 'Cree'},
    'cs': {'native': 'Čeština',
           'name': 'Czech'},
    'c': {'native': 'ѩзыкъ словѣньскъ',
          'name': 'Old Church Slavonic'},
    'cv': {'native': 'чӑваш чӗлхи',
           'name': 'Chuvash'},
    'cy': {'native': 'Cymraeg',
           'name': 'Welsh'},
    'da': {'native': 'Dansk',
           'name': 'Danish'},
    'de': {'native': 'Deutsch',
           'name': 'German'},
    'dv': {'native': 'Divehi',
           'name': 'Maldivian'},
    'dz': {'native': 'Bhutani',
           'name': 'Indian Bhutani'},
    'ee': {'native': 'Eʋegbe',
           'name': 'Ewe'},
    'el': {'native': 'Ελληνικά',
           'name': 'Greek'},
    'en': {'native': 'English',
           'name': 'English'},
    'eo': {'native': 'Esperanto',
           'name': 'Esperanto'},
    'es': {'native': 'Español',
           'name': 'Spanish'},
    'et': {'native': 'Eesti',
           'name': 'Estonian'},
    'e': {'native': 'Euskara',
          'name': 'Basque'},
    'fa': {'native': 'فارسی',
           'name': 'Persian'},
    'ff': {'native': 'Fulfulde',
           'name': 'Fula'},
    'fi': {'native': 'Suomi',
           'name': 'Finnish'},
    'fj': {'native': 'Fiji',
           'name': 'Fiji'},
    'fo': {'native': 'Føroyska',
           'name': 'Faroese'},
    'fr': {'native': 'Français',
           'name': 'French'},
    'fy': {'native': 'Frysk',
           'name': 'Frisian'},
    'ga': {'native': 'Gaeilge',
           'name': 'Irish Gaelic'},
    'gd': {'native': 'Gàidhlig',
           'name': 'Scottish Gaelic'},
    'gl': {'native': 'Galego',
           'name': 'Galician'},
    'gn': {'native': 'Guarani',
           'name': 'Guarani'},
    'g': {'native': 'ગુજરાતી',
          'name': 'Gujarati'},
    'gv': {'native': 'Gaelg',
           'name': 'Manx Gaelic'},
    'ha': {'native': 'هَوُس',
           'name': 'Hausa'},
    'he': {'native': 'עברית',
           'name': 'Hebrew'},
    'hi': {'native': 'हिंदी',
           'name': 'Hindi'},
    'ho': {'native': 'Hiri Mot',
           'name': 'Hiri Mot'},
    'hr': {'native': 'Hrvatski',
           'name': 'Croatian'},
    'ht': {'native': 'Kreyòl ayisyen',
           'name': 'Haitian'},
    'h': {'native': 'Magyar',
          'name': 'Hungarian'},
    'hy': {'native': 'Հայերէն',
           'name': 'Armenian'},
    'hz': {'native': 'Otjiherero',
           'name': 'Herero'},
    'ia': {'native': 'Interlingua',
           'name': 'Interlingua'},
    'id': {'native': 'Bahasa Indonesia',
           'name': 'Indonesian'},
    'ie': {'native': 'Interlingue',
           'name': 'Interlingue'},
    'ig': {'native': 'Asụsụ Igbo',
           'name': 'Igbo'},
    'ii': {'native': 'Nuos',
           'name': 'Nuos'},
    'ik': {'native': 'Iñupiaq',
           'name': 'Inupiak'},
    'io': {'native': 'Ido',
           'name': 'Ido'},
    'is': {'native': 'Íslenska',
           'name': 'Icelandic'},
    'it': {'native': 'Italiano',
           'name': 'Italian'},
    'i': {'native': 'ᐃᓄᒃᑎᑐᑦ',
          'name': 'Inuktitut'},
    'ja': {'native': '日本語',
           'name': 'Japanese'},
    'jv': {'native': 'Javanese',
           'name': 'basa Jawa'},
    'ka': {'native': 'ქართული',
           'name': 'Georgian'},
    'kg': {'native': 'KiKongo',
           'name': 'Kongo'},
    'ki': {'native': 'Gĩkũyũ',
           'name': 'Kikuy'},
    'kj': {'native': 'Kuanyama',
           'name': 'Kwanyama'},
    'kk': {'native': 'ﻗﺎﺯﺍﻗﺸﺎ',
           'name': 'Kazakh'},
    'kl': {'native': 'Greenlandic',
           'name': 'Greenlandic'},
    'km': {'native': 'ខ្មែរ',
           'name': 'Cambodian/Khmer'},
    'kn': {'native': 'ಕನ್ನಡ',
           'name': 'Kannada'},
    'ko': {'native': '한국어',
           'name': 'Korean'},
    'kr': {'native': 'Kanuri',
           'name': 'Kanuri'},
    'ks': {'native': 'काऽशुर',
           'name': 'Kashmiri'},
    'k': {'native': 'Kurdí',
          'name': 'Kurdish'},
    'kv': {'native': 'коми кыв',
           'name': 'Komi'},
    'kw': {'native': 'Kernewek',
           'name': 'Cornish'},
    'ky': {'native': 'Кыргыз',
           'name': 'Kirghiz'},
    'la': {'native': 'Latin',
           'name': 'Latin'},
    'lb': {'native': 'Lëtzebuergesch',
           'name': 'Luxemburgish'},
    'lg': {'native': 'Luganda',
           'name': 'Ganda'},
    'li': {'native': 'Limburgs',
           'name': 'Limburgish'},
    'ln': {'native': 'Lingala',
           'name': 'Lingala'},
    'lo': {'native': 'ພາສາລາວ',
           'name': 'Laotian'},
    'lt': {'native': 'Lietuviskai',
           'name': 'Lithuanian'},
    'l': {'native': 'Tshiluba',
          'name': 'Luba-Katanga'},
    'lv': {'native': 'Latvieš',
           'name': 'Latvian'},
    'mg': {'native': 'Malagasy',
           'name': 'Madagascarian'},
    'mh': {'native': 'Kajin M̧ajeļ',
           'name': 'Marshallese'},
    'mi': {'native': 'Maori',
           'name': 'Maori'},
    'mk': {'native': 'Македонски',
           'name': 'Macedonian'},
    'ml': {'native': 'മലയാളം',
           'name': 'Malayalam'},
    'mn': {'native': 'Монгол',
           'name': 'Mongolian'},
    'mo': {'native': 'Moldavian',
           'name': 'Moldavian'},
    'mr': {'native': 'मराठी',
           'name': 'Marathi'},
    'ms': {'native': 'Bahasa Melay',
           'name': 'Malay'},
    'mt': {'native': 'Malti',
           'name': 'Maltese'},
    'my': {'native': 'Burmese',
           'name': 'Burmese'},
    'na': {'native': 'Naur',
           'name': 'Nauruan'},
    'nb': {'native': 'Norsk bokmål',
           'name': 'Norwegian Bokmål'},
    'nd': {'native': 'Ndebele (North)',
           'name': 'Ndebele (North)'},
    'ne': {'native': 'नेपाली',
           'name': 'Nepali'},
    'ng': {'native': 'Owambo',
           'name': 'Ndonga'},
    'nl': {'native': 'Nederlands',
           'name': 'Dutch'},
    'nn': {'native': 'Nynorsk',
           'name': 'Nynorsk'},
    'no': {'native': 'Norsk',
           'name': 'Norwegian'},
    'nr': {'native': 'IsiNdebele',
           'name': 'Ndebele (South)'},
    'nv': {'native': 'Diné bizaad',
           'name': 'Navajo'},
    'ny': {'native': 'chiCheŵa',
           'name': 'Chichewa'},
    'oc': {'native': 'Occitan',
           'name': 'Occitan'},
    'oj': {'native': 'ᐊᓂᔑᓈᐯᒧᐎᓐ',
           'name': 'Ojibwe'},
    'om': {'native': 'Oromo',
           'name': 'Oromo'},
    'or': {'native': 'ଓଡ଼ିଆ',
           'name': 'Oriya'},
    'os': {'native': 'ирон æвзаг',
           'name': 'Ossetian'},
    'pa': {'native': 'ਪੰਜਾਬੀ',
           'name': 'Punjabi'},
    'pi': {'native': 'पाऴि',
           'name': 'Pāli'},
    'pl': {'native': 'Polski',
           'name': 'Polish'},
    'ps': {'native': 'پښتو',
           'name': 'Pashto'},
    'pt': {'native': 'Português',
           'name': 'Portuguese'},
    'q': {'native': 'Quechua',
          'name': 'Quechua'},
    'rm': {'native': 'Rhaeto-Romance',
           'name': 'Rhaeto-Romance'},
    'rn': {'native': 'Kirundi',
           'name': 'Kirundi'},
    'ro': {'native': 'Română',
           'name': 'Romanian'},
    'r': {'native': 'Русский',
          'name': 'Russian'},
    'rw': {'native': 'Kinyarwanda',
           'name': 'Kinyarwanda'},
    'sa': {'native': 'संस्कृत',
           'name': 'Sanskrit'},
    'sc': {'native': 'sard',
           'name': 'Sardinian'},
    'sd': {'native': 'Sindhi',
           'name': 'Sindhi'},
    'se': {'native': 'Northern Sámi',
           'name': 'Northern Sámi'},
    'sg': {'native': 'Sangho',
           'name': 'Sangho'},
    'sh': {'native': 'Serbo-Croatian',
           'name': 'Serbo-Croatian'},
    'si': {'native': 'Singhalese',
           'name': 'Singhalese'},
    'sk': {'native': 'Slovenčina',
           'name': 'Slovak'},
    'sl': {'native': 'Slovenščina',
           'name': 'Slovenian'},
    'sm': {'native': 'Samoan',
           'name': 'Samoan'},
    'sn': {'native': 'Shona',
           'name': 'Shona'},
    'so': {'native': 'Somali',
           'name': 'Somali'},
    'sq': {'native': 'Shqip',
           'name': 'Albanian'},
    'sr': {'native': 'српски',
           'name': 'Serbian'},
    'ss': {'native': 'SiSwati',
           'name': 'Swati'},
    'st': {'native': 'Sesotho',
           'name': 'Southern Sotho'},
    's': {'native': 'Sudanese',
          'name': 'Sudanese'},
    'sv': {'native': 'Svenska',
           'name': 'Swedish'},
    'sw': {'native': 'Kiswahili',
           'name': 'Swahili'},
    'ta': {'native': 'தமிழ',
           'name': 'Tamil'},
    'te': {'native': 'తెలుగు',
           'name': 'Telug'},
    'tg': {'native': 'Тоҷики',
           'name': 'Tadjik'},
    'th': {'native': 'ไทย',
           'name': 'Thai'},
    'ti': {'native': 'ትግርኛ',
           'name': 'Tigrinya'},
    'tk': {'native': 'түркmенче',
           'name': 'Turkmen'},
    'tl': {'native': 'Tagalog',
           'name': 'Tagalog'},
    'tn': {'native': 'Setswana',
           'name': 'Tswana'},
    'to': {'native': 'Tonga',
           'name': 'Tonga'},
    'tr': {'native': 'Türkçe',
           'name': 'Turkish'},
    'ts': {'native': 'Xitsonga',
           'name': 'Tsonga'},
    'tt': {'native': 'татарча',
           'name': 'Tatar'},
    'tw': {'native': 'Twi',
           'name': 'Twi'},
    'ty': {'native': 'Reo Tahiti',
           'name': 'Tahitian'},
    'ug': {'native': 'Uigur',
           'name': 'Uigur'},
    'uk': {'native': 'Українська',
           'name': 'Ukrainian'},
    'ur': {'native': 'اردو',
           'name': 'Urd'},
    'uz': {'native': 'Ўзбекча',
           'name': 'Uzbek'},
    've': {'native': 'Tshivenḓa',
           'name': 'Venda'},
    'vi': {'native': 'Tiếng Việt',
           'name': 'Vietnamese'},
    'vk': {'native': 'Ovalingo',
           'name': 'Viking'},
    'vo': {'native': 'Volapük',
           'name': 'Volapük'},
    'wa': {'native': 'Walon',
           'name': 'Walloon'},
    'wo': {'native': 'Wolof',
           'name': 'Wolof'},
    'xh': {'native': 'IsiXhosa',
           'name': 'Xhosa'},
    'yi': {'native': 'ײִדיש',
           'name': 'Yiddish'},
    'yo': {'native': 'Yorùbá',
           'name': 'Yorouba'},
    'za': {'native': 'Zhuang',
           'name': 'Zhuang'},
    'zh': {'native': '中文',
           'name': 'Chinese'},
    'z': {'native': 'IsiZul',
          'name': 'Zul'},
}

_combinedlanguagelist = {
    'ar-ae': {'name': 'Arabic (United Arab Emirates)'},
    'ar-bh': {'name': 'Arabic (Bahrain)'},
    'ar-dz': {'name': 'Arabic (Algeria)'},
    'ar-eg': {'name': 'Arabic (Egypt)'},
    'ar-il': {'name': 'Arabic (Israel)'},
    'ar-iq': {'name': 'Arabic (Iraq)'},
    'ar-jo': {'name': 'Arabic (Jordan)'},
    'ar-kw': {'name': 'Arabic (Kuwait)'},
    'ar-lb': {'name': 'Arabic (Lebanon)'},
    'ar-ly': {'name': 'Arabic (Libya)'},
    'ar-ma': {'name': 'Arabic (Morocco)'},
    'ar-mr': {'name': 'Arabic (Mauritania)'},
    'ar-om': {'name': 'Arabic (Oman)'},
    'ar-ps': {'name': 'Arabic (Palestinian West Bank and Gaza)'},
    'ar-qa': {'name': 'Arabic (Qatar)'},
    'ar-sa': {'name': 'Arabic (Saudi Arabia)'},
    'ar-sd': {'name': 'Arabic (Sudan)'},
    'ar-so': {'name': 'Arabic (Somalia)'},
    'ar-sy': {'name': 'Arabic (Syria)'},
    'ar-td': {'name': 'Arabic (Chad)'},
    'ar-tn': {'name': 'Arabic (Tunisia)'},
    'ar-ye': {'name': 'Arabic (Yemen)'},
    'bn-bd': {'name': 'Bengali (Bangladesh)'},
    'bn-in': {'name': 'Bengali (India)'},
    'bn-sg': {'name': 'Bengali (Singapore)'},
    'ch-g': {'name': 'Chamorro (Guam)'},
    'ch-mp': {'name': 'Chamorro (Northern Mariana Islands)'},
    'cs-cz': {'name': 'Czech (Czech republic)',
              'native': 'Čeština (Česká republika)'},
    'da-dk': {'name': 'Danish (Denmark)'},
    'da-gl': {'name': 'Danish (Greenland)'},
    'de-at': {'name': 'German (Austria)',
              'native': 'Deutsch (Österreich)'},
    'de-be': {'name': 'German (Belgium)'},
    'de-ch': {'name': 'German (Switzerland)'},
    'de-de': {'name': 'German (Germany)'},
    'de-dk': {'name': 'German (Denmark)'},
    'de-li': {'name': 'German (Liechtenstein)'},
    'de-l': {'name': 'German (Luxembourg)'},
    'el-cy': {'name': 'Greek (Cyprus)'},
    'el-gr': {'name': 'Greek (Greece)'},
    'en-ag': {'name': 'English (Antigua and Barbuda)'},
    'en-ai': {'name': 'English (Anguilla)'},
    'en-as': {'name': 'English (American Samoa)'},
    'en-a': {'name': 'English (Australia)'},
    'en-bb': {'name': 'English (Barbados)'},
    'en-bm': {'name': 'English (Bermuda)'},
    'en-bn': {'name': 'English (Brunei)'},
    'en-bs': {'name': 'English (Bahamas)'},
    'en-bw': {'name': 'English (Botswana)'},
    'en-bz': {'name': 'English (Belize)'},
    'en-ca': {'name': 'English (Canada)'},
    'en-ck': {'name': 'English (Cook Islands)'},
    'en-cm': {'name': 'English (Cameroon)'},
    'en-dm': {'name': 'English (Dominica)'},
    'en-er': {'name': 'English (Eritrea)'},
    'en-et': {'name': 'English (Ethiopia)'},
    'en-fj': {'name': 'English (Fiji)'},
    'en-fk': {'name': 'English (Falkland Islands)'},
    'en-fm': {'name': 'English (Micronesia)'},
    'en-gb': {'name': 'English (United Kingdom)'},
    'en-gd': {'name': 'English (Grenada)'},
    'en-gh': {'name': 'English (Ghana)'},
    'en-gi': {'name': 'English (Gibraltar)'},
    'en-gm': {'name': 'English (Gambia)'},
    'en-g': {'name': 'English (Guam)'},
    'en-gy': {'name': 'English (Guyana)'},
    'en-ie': {'name': 'English (Ireland)'},
    'en-il': {'name': 'English (Israel)'},
    'en-io': {'name': 'English (British Indian Ocean Territory)'},
    'en-jm': {'name': 'English (Jamaica)'},
    'en-ke': {'name': 'English (Kenya)'},
    'en-ki': {'name': 'English (Kiribati)'},
    'en-kn': {'name': 'English (St. Kitts-Nevis)'},
    'en-ky': {'name': 'English (Cayman Islands)'},
    'en-lc': {'name': 'English (St. Lucia)'},
    'en-lr': {'name': 'English (Liberia)'},
    'en-ls': {'name': 'English (Lesotho)'},
    'en-mp': {'name': 'English (Northern Mariana Islands)'},
    'en-ms': {'name': 'English (Montserrat)'},
    'en-mt': {'name': 'English (Malta)'},
    'en-m': {'name': 'English (Mauritius)'},
    'en-mw': {'name': 'English (Malawi)'},
    'en-na': {'name': 'English (Namibia)'},
    'en-nf': {'name': 'English (Norfolk Island)'},
    'en-ng': {'name': 'English (Nigeria)'},
    'en-nr': {'name': 'English (Nauru)'},
    'en-n': {'name': 'English (Niue)'},
    'en-nz': {'name': 'English (New Zealand)'},
    'en-pg': {'name': 'English (Papua New Guinea)'},
    'en-ph': {'name': 'English (Philippines)'},
    'en-pk': {'name': 'English (Pakistan)'},
    'en-pn': {'name': 'English (Pitcairn)'},
    'en-pr': {'name': 'English (Puerto Rico)'},
    'en-pw': {'name': 'English (Palau)'},
    'en-rw': {'name': 'English (Rwanda)'},
    'en-sb': {'name': 'English (Solomon Islands)'},
    'en-sc': {'name': 'English (Seychelles)'},
    'en-sg': {'name': 'English (Singapore)'},
    'en-sh': {'name': 'English (St. Helena)'},
    'en-sl': {'name': 'English (Sierra Leone)'},
    'en-so': {'name': 'English (Somalia)'},
    'en-sz': {'name': 'English (Swaziland)'},
    'en-tc': {'name': 'English (Turks and Caicos Islands)'},
    'en-tk': {'name': 'English (Tokelau)'},
    'en-to': {'name': 'English (Tonga)'},
    'en-tt': {'name': 'English (Trinidad and Tobago)'},
    'en-ug': {'name': 'English (Uganda)'},
    'en-us': {'name': 'English (USA)'},
    'en-vc': {'name': 'English (St. Vincent and the Grenadi)'},
    'en-vg': {'name': 'English (British Virgin Islands)'},
    'en-vi': {'name': 'English (U.S. Virgin Islands)'},
    'en-v': {'name': 'English (Vanuatu)'},
    'en-ws': {'name': 'English (Western Samoa)'},
    'en-za': {'name': 'English (South Africa)'},
    'en-zm': {'name': 'English (Zambia)'},
    'en-zw': {'name': 'English (Zimbabwe)'},
    'es-ar': {'name': 'Spanish (Argentina)'},
    'es-bo': {'name': 'Spanish (Bolivia)'},
    'es-cl': {'name': 'Spanish (Chile)'},
    'es-co': {'name': 'Spanish (Colombia)'},
    'es-cr': {'name': 'Spanish (Costa Rica)'},
    'es-c': {'name': 'Spanish (Cuba)'},
    'es-do': {'name': 'Spanish (Dominican Republic)'},
    'es-ec': {'name': 'Spanish (Ecuador)'},
    'es-es': {'name': 'Spanish (Spain)'},
    'es-gq': {'name': 'Spanish (Equatorial Guinea)'},
    'es-gt': {'name': 'Spanish (Guatemala)'},
    'es-hn': {'name': 'Spanish (Honduras)'},
    'es-mx': {'name': 'Spanish (Mexico)'},
    'es-ni': {'name': 'Spanish (Nicaragua)'},
    'es-pa': {'name': 'Spanish (Panama)'},
    'es-pe': {'name': 'Spanish (Peru)'},
    'es-pr': {'name': 'Spanish (Puerto Rico)'},
    'es-py': {'name': 'Spanish (Paraguay)'},
    'es-sv': {'name': 'Spanish (El Salvador)'},
    'es-us': {'name': 'Spanish (USA)'},
    'es-uy': {'name': 'Spanish (Uruguay)'},
    'es-ve': {'name': 'Spanish (Venezuela)'},
    'fr-ad': {'name': 'French (Andorra)'},
    'fr-be': {'name': 'French (Belgium)'},
    'fr-bf': {'name': 'French (Burkina Faso)'},
    'fr-bi': {'name': 'French (Burundi)'},
    'fr-bj': {'name': 'French (Benin)'},
    'fr-ca': {'name': 'French (Canada)'},
    'fr-cd': {'name': 'French (Democratic Republic of Congo)'},
    'fr-cf': {'name': 'French (Central African Republic)'},
    'fr-cg': {'name': 'French (Congo)'},
    'fr-ch': {'name': 'French (Switzerland)'},
    'fr-ci': {'name': 'French (Cote d\'Ivoire)'},
    'fr-cm': {'name': 'French (Cameroon)'},
    'fr-dj': {'name': 'French (Djibouti)'},
    'fr-fr': {'name': 'French (France)'},
    'fr-ga': {'name': 'French (Gabon)'},
    'fr-gb': {'name': 'French (United Kingdom)'},
    'fr-gf': {'name': 'French (French Guiana)'},
    'fr-gn': {'name': 'French (Guinea)'},
    'fr-ht': {'name': 'French (Haiti)'},
    'fr-it': {'name': 'French (Italy)'},
    'fr-km': {'name': 'French (Comoros Islands)'},
    'fr-lb': {'name': 'French (Lebanon)'},
    'fr-l': {'name': 'French (Luxembourg)'},
    'fr-mc': {'name': 'French (Monaco)'},
    'fr-mg': {'name': 'French (Madagascar)'},
    'fr-ml': {'name': 'French (Mali)'},
    'fr-mq': {'name': 'French (Martinique)'},
    'fr-nc': {'name': 'French (New Caledonia)'},
    'fr-pf': {'name': 'French (French Polynesia)'},
    'fr-pm': {'name': 'French (St. Pierre and Miquelon)'},
    'fr-rw': {'name': 'French (Rwanda)'},
    'fr-sc': {'name': 'French (Seychelles)'},
    'fr-td': {'name': 'French (Chad)'},
    'fr-tg': {'name': 'French (Togo)'},
    'fr-v': {'name': 'French (Vanuatu)'},
    'fr-wf': {'name': 'French (Wallis and Futuna)'},
    'fr-yt': {'name': 'French (Mayotte)'},
    'hr-ba': {'name': 'Croatian (Bosnia-Herzegovina)'},
    'hr-hr': {'name': 'Croatian (Croatia)'},
    'hu-h': {'name': 'Hungarian (Hungary)'},
    'hu-si': {'name': 'Hungarian (Slovenia)'},
    'it-ch': {'name': 'Italian (Switzerland)'},
    'it-hr': {'name': 'Italian (Croatia)'},
    'it-it': {'name': 'Italian (Italy)'},
    'it-si': {'name': 'Italian (Slovenia)'},
    'it-sm': {'name': 'Italian (San Marino)'},
    'ko-kp': {'name': 'Korean (Korea), North)'},
    'ko-kr': {'name': 'Korean (Korea), South)'},
    'ln-cd': {'name': 'Lingala (Democratic Republic of Congo)'},
    'ln-cg': {'name': 'Lingala (Congo)'},
    'ms-bn': {'name': 'Malay (Brunei)'},
    'ms-my': {'name': 'Malay (Malaysia)'},
    'ms-sg': {'name': 'Malay (Singapore)'},
    'nl-an': {'name': 'Dutch (Netherlands Antilles)'},
    'nl-aw': {'name': 'Dutch (Aruba)'},
    'nl-be': {'name': 'Dutch (Belgium)'},
    'nl-nl': {'name': 'Dutch (Netherlands)'},
    'nl-sr': {'name': 'Dutch (Suriname)'},
    'pt-ao': {'name': 'Portuguese (Angola)',
              'native': 'Português (Angola)'},
    'pt-br': {'name': 'Portuguese (Brazil)',
              'native': 'Português (Brasil)'},
    'pt-cv': {'name': 'Portuguese (Ilhas Cabo Verde)',
              'native': 'Português (Cabo Verde)'},
    'pt-gw': {'name': 'Portuguese (Guiné-Bissau)',
              'native': 'Português (Guiné-Bissau)'},
    'pt-mz': {'name': 'Portuguese (Moçambique)',
              'native': 'Português (Moçambique)'},
    'pt-pt': {'name': 'Portuguese (Portugal)',
              'native': 'Português (Portugal)'},
    'pt-st': {'name': 'Portuguese (São Tomé e Príncipe)',
              'native': 'Português (São Tomé e Príncipe)'},
    'sd-in': {'name': 'Sindhi (India)'},
    'sd-pk': {'name': 'Sindhi (Pakistan)'},
    'sr-ba': {'name': 'Serbian (Bosnia-Herzegovina)'},
    'ss-sz': {'name': 'Swati (Swaziland)'},
    'ss-za': {'name': 'Swati (South Africa)'},
    'sv-fi': {'name': 'Swedish (Finland)'},
    'sv-se': {'name': 'Swedish (Sweden)'},
    'sw-ke': {'name': 'Swahili (Kenya)'},
    'sw-tz': {'name': 'Swahili (Tanzania)'},
    'ta-in': {'name': 'Tamil (India)'},
    'ta-sg': {'name': 'Tamil (Singapore)'},
    'tn-bw': {'name': 'Tswana (Botswana)'},
    'tn-za': {'name': 'Tswana (South Africa)'},
    'tr-bg': {'name': 'Turkish (Bulgaria)'},
    'tr-cy': {'name': 'Turkish (Cyprus)'},
    'tr-tr': {'name': 'Turkish (Turkey)'},
    'ur-in': {'name': 'Urdu (India)'},
    'ur-pk': {'name': 'Urdu (Pakistan)'},
    'zh-cn': {'name': 'Chinese (China)',
              'native': '简体中文(中国)'},
    'zh-hk': {'name': 'Chinese (Hongkong)',
              'native': '繁體中文(香港)'},
    'zh-sg': {'name': 'Chinese (Singapore)',
              'native': '简体中文(新加坡)'},
    'zh-tw': {'name': 'Chinese (Taiwan)',
              'native': '繁體中文(臺灣)'},
}
