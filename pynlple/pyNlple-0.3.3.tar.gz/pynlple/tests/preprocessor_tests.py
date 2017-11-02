# -*- coding: utf-8 -*-
import unittest

from pynlple.processing.preprocessor import *

class HtmlEntitiesReplacerTest(unittest.TestCase):

    def test_should_not_malform_input(self):
        input_string = 'this is some input, that does not contain html-escaped entities. this should be left untouched!'
        replacer = HtmlEntitiesEscaper()
        result = replacer.preprocess(input_string)
        expected = 'this is some input, that does not contain html-escaped entities. this should be left untouched!'
        self.assertEqual(expected, result)

    def test_should_replace_symbols_with_html_entities(self):
        input_string = 'this\'s input with "escaped" entities & some other sheet'
        replacer = HtmlEntitiesEscaper()
        result = replacer.preprocess(input_string)
        expected = 'this&#x27;s input with &quot;escaped&quot; entities &amp; some other sheet'
        self.assertEqual(expected, result)

    def test_should_replace_html_entities_with_symbols(self):
        input_string = 'this&#x27;s input with &quot;escaped&quot; entities &amp; some other sheet'
        replacer = HtmlEntitiesUnescaper()
        result = replacer.preprocess(input_string)
        expected = 'this\'s input with "escaped" entities & some other sheet'
        self.assertEqual(expected, result)


class VKMentionReplacerTest(unittest.TestCase):

    def test_should_replace_with_default(self):
        input_string = 'Здесь в тексте есть ссылка[id254351532|Олололя] как в вконтакте.'
        replacer = VKMentionReplacer()
        result = replacer.preprocess(input_string)
        expected = 'Здесь в тексте есть ссылка как в вконтакте.'
        self.assertEqual(expected, result)

    def test_should_replace_with_tag(self):
        input_string = 'Здесь в тексте есть ссылка[id254351532|Олололя] как в вконтакте.'
        replacer = VKMentionReplacer('tag')
        result = replacer.preprocess(input_string)
        expected = 'Здесь в тексте есть ссылкаtag как в вконтакте.'
        self.assertEqual(expected, result)

    def test_should_replace_hard_case(self):
        input_string = 'Здесь в тексте есть ссылка[id254351532:bp-16297716_231892|Coca-Cola] как в вконтакте.'
        replacer = VKMentionReplacer('tag')
        result = replacer.preprocess(input_string)
        expected = 'Здесь в тексте есть ссылкаtag как в вконтакте.'
        self.assertEqual(expected, result)


class RegexReplacerTest(unittest.TestCase):

    TEST_REGEX = 'a+'
    TEST_TARGET = 'b'
    TEST_STRING = 'cCaaAAaACc'

    TEST_GROUP_REGEX = '(a+)'
    TEST_GROUP_TARGET = '\\1b\\1'

    TEST_W_REGEX = '\\w'
    TEST_W_TARGET = 'w'
    TEST_W_STRING = 't+tЫ+ЫІ+Іj+j'

    TEST_W_RARE_STRING = '\u263A+⛇+ۑ+Ҝ+Θ+ᰔ+⃣a+ꋘ'

    def test_should_perform_case_insensitive_replacement(self):
        replacer = RegexReplacer(RegexReplacerTest.TEST_REGEX, RegexReplacerTest.TEST_TARGET, False, False, False)
        result = replacer.preprocess(RegexReplacerTest.TEST_STRING)
        expected = 'cCbCc'
        self.assertEqual(expected, result)

    def test_should_perform_case_sensitive_replacement(self):
        replacer = RegexReplacer(RegexReplacerTest.TEST_REGEX, RegexReplacerTest.TEST_TARGET, True, False, False)
        result = replacer.preprocess(RegexReplacerTest.TEST_STRING)
        expected = 'cCbAAbACc'
        self.assertEqual(expected, result)

    def test_should_perform_w_replacement_without_unicode_symbols(self):
        replacer = RegexReplacer(RegexReplacerTest.TEST_W_REGEX,
                                 RegexReplacerTest.TEST_W_TARGET,
                                 False, False, True)
        result = replacer.preprocess(RegexReplacerTest.TEST_W_STRING)
        expected = 'w+wЫ+ЫІ+Іw+w'
        self.assertEqual(expected, result)

    def test_should_perform_w_replacement_with_unicode_symbols(self):
        replacer = RegexReplacer(RegexReplacerTest.TEST_W_REGEX,
                                 RegexReplacerTest.TEST_W_TARGET,
                                 False, False, False)
        result = replacer.preprocess(RegexReplacerTest.TEST_W_STRING)
        expected = 'w+ww+ww+ww+w'
        self.assertEqual(expected, result)

    def test_should_perform_w_replacement_with_unicode_rare_symbols(self):
        replacer = RegexReplacer(RegexReplacerTest.TEST_W_REGEX,
                                 RegexReplacerTest.TEST_W_TARGET,
                                 False, False, False)
        result = replacer.preprocess(RegexReplacerTest.TEST_W_RARE_STRING)
        expected = '\u263A+⛇+w+w+w+w+⃣w+w'
        self.assertEqual(expected, result)

    def test_should_replace_rare_double_quotes_in_stack_with_single_quote_replacer(self):
        replacer_1 = QuotesReplacer()
        replacer_2 = DoubleQuotesReplacer()

        replacer = StackingPreprocessor([replacer_1, replacer_2])

        # First symbol is a comma, second one - is a quote
        input_string = ',‚тестируем′ «Нестле» '
        output = replacer.preprocess(input_string)

        expected = ',\'тестируем\' \"Нестле\" '
        self.assertEqual(expected, output)

    def test_should_remove_all_except_words_and_numbers(self):
        punct_string = '!!!1.word.\' \'2.word-with-hypen 3.word\'s here! ' \
                       '4.6 12:60 12,000!? -no way-^_^'
        replacer = NonWordOrNumberOrWhitespaceAllUnicodeReplacer()
        result = replacer.preprocess(punct_string)
        expected = ' 1 word   2 word-with-hypen 3 word\'s here  ' \
                   '4.6 12:60 12,000   no way '
        self.assertEqual(expected, result)

    def test_should_reduce_multiple_punctuation_symbols(self):
        punct_string = ' ... !!...!?????asddf --a !!kek shlak&&**&&&&'
        replacer = MultiPunctuationReplacer()
        result = replacer.preprocess(punct_string)
        expected = ' . !.!?asddf -a !kek shlak&*&'
        self.assertEqual(expected, result)

    def test_should_replace_email(self):
        email_string = 'Hi, guys! I had email@yahoo.com, I didn\'t use @ at yahoo.com. Here\'s my new e-mail: my_email+test@mail.yahoo.com. '\
                       'Can you please validate it?'
        replacer = EmailReplacer(' emailTag ')
        result = replacer.preprocess(email_string)
        expected = 'Hi, guys! I had  emailTag , I didn\'t use @ at yahoo.com. Here\'s my new e-mail:  emailTag . '\
                   'Can you please validate it?'
        self.assertEqual(expected, result)

    def test_should_replace_bold_tag(self):
        punct_string = '#<b>лотерея</b> #<b>выигрыш</b> #<b>лото</b> #<b>тираж</b> #<b>Спортлото</b>'
        replacer = BoldTagReplacer()
        result = replacer.preprocess(punct_string)
        expected = '#лотерея #выигрыш #лото #тираж #Спортлото'
        self.assertEqual(expected, result)


class TokenizerTest(unittest.TestCase):

    def test_should_tokenize_words(self):
        input_string = '!These words, un-like-ly said here(sic!), should be tokenized. ' \
                  'Ukrainska mova takoj z\'yavliaetsia tyt.'
        tokenizer = WordTokenizer()
        expected = '! These words , un-like-ly said here ( sic ! ) , should be tokenized . ' \
                   'Ukrainska mova takoj z\'yavliaetsia tyt .'

        result = tokenizer.preprocess(input_string)
        self.assertEqual(expected, result)

    def test_should_tokenize_words_w_cyrillics(self):
        input_string = 'за 2011 год). Вот полный список торговых марок от Nestle, которые можно найти в любом российском магазине: Nescafé, КитКат,'
        tokenizer = WordTokenizer()
        expected = 'за 2011 год ) . Вот полный список торговых марок от Nestle , которые можно найти в любом российском магазине : Nescafé , КитКат ,'

        result = tokenizer.preprocess(input_string)
        self.assertEqual(expected, result)

    def test_should_tokenize_digits_w_special_symbols(self):
        input_string = '0.0, 000 00-00 00- 00\' 0.00, 00.00, 00:00, 0000.00.00, 0000:00, 000,00, 00..00 :00 0'
        tokenizer = WordTokenizer()
        expected = '0.0 , 000 00 - 00 00 - 00 \' 0.00 , 00.00 , 00:00 , 0000.00.00 , 0000:00 , 000,00 , 00 .. 00 : 00 0'

        result = tokenizer.preprocess(input_string)
        self.assertEqual(expected, result)

    def test_should_tokenize_words_w_special_symbols(self):
        input_string = 'п\'ятого \'november\' з-під рову- merry-go-round'
        tokenizer = WordTokenizer()
        expected = 'п\'ятого \' november \' з-під рову - merry-go-round'

        result = tokenizer.preprocess(input_string)
        self.assertEqual(expected, result)

    def test_should_not_tokenize_words_w_dash(self):
        input_string = 'wi-fi'
        tokenizer = WordTokenizer()
        expected = 'wi-fi'

        result = tokenizer.preprocess(input_string)
        self.assertEqual(expected, result)

    def test_should_tokenize_words_w_digits_w_special_symbols(self):
        input_string = '25.двадцатьпять 15\'16-річний я 15\'ок \'солюшнз-'
        tokenizer = WordTokenizer()
        expected = '25 . двадцатьпять 15 \' 16-річний я 15\'ок \' солюшнз -'

        result = tokenizer.preprocess(input_string)
        self.assertEqual(expected, result)

    def test_should_tokenize_words_w_digits(self):
        input_string = '25двадцатьпять 15річний15'
        tokenizer = WordTokenizer()
        expected = '25 двадцатьпять 15 річний 15'

        result = tokenizer.preprocess(input_string)
        self.assertEqual(expected, result)

    def test_should_tokenize_words_and_not_multiple_dots(self):
        input_string = '...я ... не знаю... что и... сказать'
        tokenizer = WordTokenizer()
        expected = '... я ... не знаю ... что и ... сказать'

        result = tokenizer.preprocess(input_string)
        self.assertEqual(expected, result)

    def test_should_replace_urls_with_tags_isnide(self):
        replacement = 'LINK'
        input_string = 'this is the link http://dostavka-gaza-v-<b>dom</b>.<b>ru</b> we need to replace.'
        tokenizer = URLReplacer(replace_tag_with=replacement)
        expected = 'this is the link ' + replacement + ' we need to replace.'

        result = tokenizer.preprocess(input_string)
        self.assertEqual(expected, result)

    def test_should_replace_url(self):
        replacement = 'LINK'
        input_string = 'this is the link http://dostavka-gaza-v-dom.ru we need to replace.'
        tokenizer = URLReplacer(replace_tag_with=replacement)
        expected = 'this is the link ' + replacement + ' we need to replace.'
        result = tokenizer.preprocess(input_string)
        self.assertEqual(expected, result)

    def test_should_replace_url2(self):
        replacement = 'LINK'
        input_string = 'this is the link http://www.rbc.ru/rbcfreenews/58f5f3aa9a79477a6ddcc1d3#xtor=AL-[internal_traffic]--[rss.rbc.ru]-[top_stories_brief_news] we need to replace.'
        tokenizer = URLReplacer(replace_tag_with=replacement)
        expected = 'this is the link ' + replacement + ' we need to replace.'
        result = tokenizer.preprocess(input_string)
        self.assertEqual(expected, result)


    def test_should_replace_truncated_url(self):
        replacement = 'LINK'
        input_string = 'this is the link http://... we need to replace.'
        tokenizer = URLReplacer(replace_tag_with=replacement)
        expected = 'this is the link ' + replacement + ' we need to replace.'

        result = tokenizer.preprocess(input_string)
        self.assertEqual(expected, result)

    def test_should_replace_user_wrote_reply_sign_at_start(self):
        replacement = '<tag>'
        input_string = 'Perfect4a писал(а) 27 авг 2015, 18:01: This is test'
        tokenizer = UserWroteRuReplacer(replace_tag_with=replacement)
        expected = '' + replacement + ' This is test'

        result = tokenizer.preprocess(input_string)
        self.assertEqual(expected, result)

    def test_should_replace_user_wrote_reply_sign_in_middle(self):
        replacement = '<tag>'
        input_string = 'This is test Perfect4a писал(а) 27 авг 2015, 18:01: This is test'
        tokenizer = UserWroteRuReplacer(replace_tag_with=replacement)
        expected = 'This is test ' + replacement + ' This is test'

        result = tokenizer.preprocess(input_string)
        self.assertEqual(expected, result)

    def test_should_replace_user_wrote_reply_second_type_sign_at_start(self):
        replacement = '<tag>'
        input_string = 'mircurt (03.03.16 20:39) писал(а): This is test'
        tokenizer = UserWroteRuReplacer(replace_tag_with=replacement)
        expected = '' + replacement + ' This is test'

        result = tokenizer.preprocess(input_string)
        self.assertEqual(expected, result)

    def test_should_replace_user_wrote_reply_second_type_sign_in_middle(self):
        replacement = '<tag>'
        input_string = 'This is test mircurt (03.03.16 20:39) писал(а): This is test'
        tokenizer = UserWroteRuReplacer(replace_tag_with=replacement)
        expected = 'This is test ' + replacement + ' This is test'

        result = tokenizer.preprocess(input_string)
        self.assertEqual(expected, result)

    def test_should_replace_user_wrote_reply_mixed_type(self):
        replacement = '<tag>'
        input_string = 'mircurt (03.03.16 20:39) писал(a) Вчера: This is test'
        tokenizer = UserWroteRuReplacer(replace_tag_with=replacement)
        expected = '' + replacement + ' This is test'

        result = tokenizer.preprocess(input_string)
        self.assertEqual(expected, result)

    def test_should_replace_accent_mark_with_nonword_replacer(self):
        replacement = ''
        input_string = 'в ́этом предл́ожении в́ыставлены удар́ения'
        tokenizer = NonWhitespaceAlphaNumPuncSpecSymbolsAllUnicodeRemover(replace_tag_with=replacement)
        expected = 'в этом предложении выставлены ударения'
        result = tokenizer.preprocess(input_string)
        self.assertEqual(expected, result)


class StackingPreprocessorTest(unittest.TestCase):

    REGEX_1 = 'a'
    TARGET_1 = 'b'
    REGEX_2 = 'c'
    TARGET_2 = 'd'

    def test_should_replace_continuosly_without_collisions(self):
        replacer_1 = RegexReplacer(StackingPreprocessorTest.REGEX_1, StackingPreprocessorTest.TARGET_1, False, False, False)
        replacer_2 = RegexReplacer(StackingPreprocessorTest.REGEX_2, StackingPreprocessorTest.TARGET_2, False, False, False)

        stacking_replacer = StackingPreprocessor()
        stacking_replacer.append_preprocessor(replacer_1)
        stacking_replacer.append_preprocessor(replacer_2)

        input_string = 'acaca'
        output = stacking_replacer.preprocess(input_string)

        expected = 'bdbdb'
        self.assertEqual(expected, output)

    def test_should_replace_continuosly_with_chaining(self):
        replacer_1 = RegexReplacer(StackingPreprocessorTest.REGEX_1, StackingPreprocessorTest.TARGET_1, False, False, False)
        replacer_2 = RegexReplacer(StackingPreprocessorTest.TARGET_1, StackingPreprocessorTest.TARGET_2, False, False, False)

        stacking_replacer = StackingPreprocessor()

        stacking_replacer.append_preprocessor(replacer_1)
        stacking_replacer.append_preprocessor(replacer_2)

        input_string = 'acaca'
        output = stacking_replacer.preprocess(input_string)

        expected = 'dcdcd'
        self.assertEqual(expected, output)

    def test_should_replace_in_right_order_when_prepend(self):
        replacer_1 = RegexReplacer(StackingPreprocessorTest.TARGET_2, StackingPreprocessorTest.TARGET_1, False, False, False)
        replacer_2 = RegexReplacer(StackingPreprocessorTest.REGEX_2, StackingPreprocessorTest.TARGET_2, False, False, False)

        stacking_replacer = StackingPreprocessor()

        stacking_replacer.append_preprocessor(replacer_1)
        stacking_replacer.prepend_preprocessor(replacer_2)

        input_string = 'acaca'
        output = stacking_replacer.preprocess(input_string)

        expected = 'ababa'
        self.assertEqual(expected, output)

if __name__ == '__main__':
    unittest.main()
