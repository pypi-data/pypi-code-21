# This is based on Anoop Kunchukuttan's Indic NLP Library
#
# Indic NLP Library is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Only Bangla Normalizer is present here which is heavily modified. Bangla digit normalizer is added
# Letters with NUKTA (dot under certain letters) is also normalized

import sys
import codecs
import re
import unicodedata


class NormalizerI(object):
    """
    The normalizer classes do the following:

    * Some characters have multiple Unicode codepoints. The normalizer chooses a single standard representation
    * Some control characters are deleted
    * While typing using the Latin keyboard, certain typical mistakes occur which are corrected by the module

    Base class for normalizer. Performs some common normalization, which includes:

    * Byte order mark, word joiner, etc. removal
    * ZERO_WIDTH_NON_JOINER and ZERO_WIDTH_JOINER removal
    * ZERO_WIDTH_SPACE and NO_BREAK_SPACE replaced by spaces

    Script specific normalizers should derive from this class and override the normalize() method.
    They can call the super class 'normalize() method to avail of the common normalization

    """

    BYTE_ORDER_MARK = u'\uFEFF'
    BYTE_ORDER_MARK_2 = u'\uFFFE'
    WORD_JOINER = u'\u2060'
    SOFT_HYPHEN = u'\u00AD'

    ZERO_WIDTH_SPACE = u'\u200B'
    NO_BREAK_SPACE = u'\u00A0'

    ZERO_WIDTH_NON_JOINER = u'\u200C'
    ZERO_WIDTH_JOINER = u'\u200D'

    def normalize(self, text):
        """
        Method to be implemented for normalization for each script
        """
        text = text.replace(NormalizerI.BYTE_ORDER_MARK, '')
        text = text.replace(NormalizerI.BYTE_ORDER_MARK_2, '')
        text = text.replace(NormalizerI.WORD_JOINER, '')
        text = text.replace(NormalizerI.SOFT_HYPHEN, '')

        text = text.replace(NormalizerI.ZERO_WIDTH_SPACE, ' ')  # ??
        text = text.replace(NormalizerI.NO_BREAK_SPACE, ' ')

        text = text.replace(NormalizerI.ZERO_WIDTH_NON_JOINER, '')
        text = text.replace(NormalizerI.ZERO_WIDTH_JOINER, '')

        return text

    def get_char_stats(self, text):
        print(len(re.findall(NormalizerI.BYTE_ORDER_MARK, text)))
        print(len(re.findall(NormalizerI.BYTE_ORDER_MARK_2, text)))
        print(len(re.findall(NormalizerI.WORD_JOINER, text)))
        print(len(re.findall(NormalizerI.SOFT_HYPHEN, text)))

        print(len(re.findall(NormalizerI.ZERO_WIDTH_SPACE, text)))
        print(len(re.findall(NormalizerI.NO_BREAK_SPACE, text)))

        print(len(re.findall(NormalizerI.ZERO_WIDTH_NON_JOINER, text)))
        print(len(re.findall(NormalizerI.ZERO_WIDTH_JOINER, text)))

        # for mobj in re.finditer(NormalizerI.ZERO_WIDTH_NON_JOINER,text):
        #    print text[mobj.start()-10:mobj.end()+10].replace('\n', ' ').replace(NormalizerI.ZERO_WIDTH_NON_JOINER,'').encode('utf-8')
        # print hex(ord(text[mobj.end():mobj.end()+1]))

    def correct_visarga(self, text, visarga_char, char_range):
        text = re.sub(r'([\u0900-\u097f]):', u'\\1\u0903', text)


class BanglaNormalizer(NormalizerI):
    """
    Normalizer for the Bengali script. In addition to basic normalization by the super class,

    * Replaces the composite characters containing nuktas by their decomposed form
    * Replace the reserved character for poorna virama (if used) with the recommended generic Indic scripts poorna virama
    * Canonicalize two part dependent vowels
    * replace pipe character '|' by poorna virama character
    * replace colon ':' by visarga if the colon follows a charcter in this script

    """

    NUKTA = u'\u09BC'

    def __init__(self, remove_nuktas=False):
        self.re_machine = re.compile(r'[ `~!@#$%^&*()\-_=+[{\]}\\|;:\'",<.>/?\n।\u200c‘’—]')
        self.remove_nuktas = remove_nuktas

    def normalize_doc(self, text):
        text = self.re_machine.split(text)
        text = [word.strip().lower() for word in text if len(word.strip()) > 0]
        return ' '.join([self.normalize(word) for word in text])

    def normalize(self, text):
        # common normalization for Indic scripts
        text = super(BanglaNormalizer, self).normalize(text)
        text = self.digit_normalize(text)

        # removing Nukta and building proper unicode characters
        # issue: https://phabricator.wikimedia.org/T7948
        text = text.replace(u'\u09ac' + BanglaNormalizer.NUKTA, u'\u09b0')
        text = text.replace(u'\u09a1' + BanglaNormalizer.NUKTA, u'\u09dc')
        text = text.replace(u'\u09a2' + BanglaNormalizer.NUKTA, u'\u09dd')
        text = text.replace(u'\u09af' + BanglaNormalizer.NUKTA, u'\u09df')

        if self.remove_nuktas:
            text = text.replace(BanglaNormalizer.NUKTA, '')

        # replace the poorna virama codes specific to script
        # with generic Indic script codes
        text = text.replace(u'\u09e4', u'\u0964')
        text = text.replace(u'\u09e5', u'\u0965')

        # replace pipe character for poorna virama
        text = text.replace(u'\u007c', u'\u0964')

        # two part dependent vowels
        text = text.replace(u'\u09c7\u09be', u'\u09cb')
        text = text.replace(u'\u09c7\u0bd7', u'\u0bcc')

        # correct visarge
        text = re.sub(r'([\u0980-\u09ff]):', u'\\1\u0983', text)

        text = self.lucene_normalize(text)

        return text

    def digit_normalize(self, text):
        ret = ""
        for i in range(len(text)):
            if str.isdecimal(text[i]):
                ret = ret + str(int(unicodedata.numeric(text[i])))
            else:
                ret = ret + text[i]
        return ret

    def lucene_normalize(self, text):
        ret = list(text)
        i = -1
        while i < (len(ret)-1):
            i += 1

            # delete Chandrabindu
            if ret[i] == '\u0981':
                ret[i] = ''
                continue

            # DirghoI kar -> RosshoI kar
            elif ret[i] == '\u09C0':
                ret[i] = '\u09BF'
                continue

            # DirghoU kar -> RosshoU kar
            elif ret[i] == '\u09C2':
                ret[i] = '\u09C1'
                continue

            # Khio (Ka + Hoshonto + Murdorno Sh)
            elif ret[i] == '\u0995':
                if (i+2 < len(ret)) and (ret[i+1] == '\u09CD') and (ret[i+2] == '\u09BF'):
                    if i == 0:
                        ret[i] = '\u0996'
                        ret[i+1] = ''
                        ret[i+2] = ''
                    else:
                        ret[i+1] = '\u0996'
                        ret[i+2] = ''
                continue

            # Nga to Anusvara
            elif ret[i] == '\u0999':
                ret[i] = '\u0982'
                continue

            # Ja Phala
            elif ret[i] == '\u09AF':
                if (i-2 == 0) and (ret[i-1] == '\u09CD'):
                    ret[i-1] = '\u09C7'
                    if (i+1 < len(ret)) and (ret[i+1] == '\u09BE'):
                        ret[i+1] = ''
                    ret[i] = ''
                elif (i-1 >= 0) and (ret[i-1] == '\u09CD'):
                    ret[i] = ''
                    ret[i-1] = ''
                continue

            # Ba Phalaa
            elif ret[i] == '\u09AC':
                if ((i >= 1) and (ret[i-1] != '\u09CD')) or (i == 0):
                    continue
                if i-2 == 0:
                    ret[i] = ''
                    ret[i-1] = ''
                elif (i-5 >= 0) and (ret[i-3] == '\u09CD'):
                    ret[i] = ''
                    ret[i-1] = ''
                elif (i-2 >= 0) and (ret[i-2] == '\u09B8'):
                    ret[i-1] = ret[i-2]
                    ret[i] = ''
                continue

            # Visarga
            elif ret[i] == '\u0983':
                if i == len(ret)-1:
                    if len(ret) <= 3:
                        ret[i] = '\u09B9'
                    else:
                        ret[i] = ''
                else:
                    ret[i] = ret[i+1]
                continue

            # All sh
            elif ret[i] in ('\u09B6', '\u09B7'):
                ret[i] = '\u09B8'
                continue

            # Check na
            elif ret[i] == '\u09A3':
                ret[i] = '\u09A8'
                continue

            # Check ra
            elif ret[i] in ('\u09DC', '\u09DD'):
                ret[i] = '\u09B0'
                continue

            elif ret[i] == '\u09CE':
                ret[i] = '\u09A4'
                continue

        # Hoshonto
        ret = [x for x in ret if x != '\u09CD']

        return ''.join(ret)


class IndicNormalizerFactory(object):
    """
    Factory class to create language specific normalizers.

    """

    def get_normalizer(self, language, remove_nuktas=False):
        """
            Call the get_normalizer function to get the language specific normalizer

            Paramters:
            |language: language code
            |remove_nuktas: boolean, should the normalizer remove nukta characters
        """
        normalizer = None
        if language in ['bn', 'as']:
            normalizer = BanglaNormalizer(remove_nuktas)
        else:
            normalizer = NormalizerI()

        return normalizer

    def is_language_supported(self, language):
        """
        Is the language supported?
        """
        if language in ['bn', 'as']:
            return True
        else:
            return False


if __name__ == '__main__':

    if len(sys.argv) < 4:
        print("Usage: python normalize.py <infile> <outfile> <language> [<replace_nukta(True,False>]")
        sys.exit(1)

    language = sys.argv[3]
    remove_nuktas = False
    if len(sys.argv) >= 5:
        remove_nuktas = bool(sys.argv[4])

    # create normalizer
    factory = IndicNormalizerFactory()
    normalizer = factory.get_normalizer(language, remove_nuktas)

    # DO normalization
    with codecs.open(sys.argv[1], 'r', 'utf-8') as ifile:
        with codecs.open(sys.argv[2], 'w', 'utf-8') as ofile:
            for line in ifile.readlines():
                normalized_line = normalizer.normalize(line)
                ofile.write(normalized_line)

                ## gather status about normalization
                # with codecs.open(sys.argv[1],'r','utf-8') as ifile:
                #    normalizer=DevanagariNormalizer()
                #    text=string.join(ifile.readlines(),sep='')
                #    normalizer.get_char_stats(text)