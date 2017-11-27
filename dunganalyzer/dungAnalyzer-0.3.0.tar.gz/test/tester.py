from dungAnalyzer import *


def bn_analyzer(words):
    analyzer = BanglaAnalyzer()
    words = analyzer.analyze(words)
    print("Analyzed: {}".format(words))
    return words


def en_analyzer(words):
    snow_analyzer = EnglishAnalyzer('en_snowball')
    porter_analyzer = EnglishAnalyzer('en_porter')
    snow_words = snow_analyzer.analyze(words)
    porter_words = porter_analyzer.analyze(words)
    print('Snow Analyzed: {}'.format(snow_words))
    print('Porter Analyzed: {}'.format(porter_words))
    return words


if __name__ == '__main__':
    # txt = 'ব্রাহ্মণবাড়িয়া'
    # # with open('./test_input.txt', 'r', encoding='utf-8') as inp:
    # #     txt = inp.read()
    #
    # print(txt)
    # txt = bn_analyzer(txt)
    # with open('./output.txt', 'w', encoding='utf-8') as f:
    #     f.write(txt)

    txt = "grows leaves fairly running having generously"

    print(txt)
    txt = en_analyzer(txt)
    with open('./output.txt', 'w', encoding='utf-8') as f:
        f.write(txt)

