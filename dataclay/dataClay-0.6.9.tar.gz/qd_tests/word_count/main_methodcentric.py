#!/usr/bin/python
# -*- coding: utf-8 -*-
import string

from WordCount import TextStats, TextCollection, Text

__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2017 Barcelona Supercomputing Center (BSC-CNS)'


if __name__ == "__main__":
    from pycompss.api.api import waitForAllTasks

    # Manual small text generation (just to test method calling)
    remove_punctuation_map = dict((ord(char), None) for char in string.punctuation)
    sanitize = lambda text: unicode(text.lower()).translate(remove_punctuation_map).split()
    all_texts = [
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vivamus a leo vitae arcu tempus malesuada. Maecenas egestas diam a urna ultricies facilisis. Cras egestas, erat eu tincidunt eleifend, velit leo auctor odio, et dignissim ligula sem quis augue. Aenean at neque non odio molestie dictum. Integer porttitor lorem molestie felis varius dictum. Donec pretium ligula ipsum, id interdum mi efficitur ac. Nulla semper, sapien in maximus vestibulum, sapien dui efficitur neque, eu pharetra risus ligula quis sem. Proin sit amet tincidunt tortor.',
        'Fusce sagittis odio nisi, in luctus enim scelerisque sollicitudin. Donec orci purus, maximus id ultricies at, vehicula in turpis. Morbi sit amet eros accumsan, hendrerit nisi in, dapibus magna. Nam convallis consectetur neque, in faucibus leo scelerisque nec. Cras mattis metus id porttitor egestas. Curabitur feugiat lobortis vulputate. Phasellus vel dignissim lectus, at gravida diam. Nam vel massa a ex hendrerit sodales. Vestibulum iaculis enim vel metus elementum cursus non quis ligula. Pellentesque ut eleifend diam.',
        'Vestibulum sit amet neque vel nisl consequat placerat. Cras id eros ut enim blandit ornare. Pellentesque elementum purus nisi. Maecenas vitae tincidunt leo. Phasellus nisl enim, volutpat non erat pharetra, rutrum euismod tellus. Sed felis felis, imperdiet in nisl et, pretium bibendum metus. Suspendisse a orci metus. Sed laoreet scelerisque rhoncus. Ut fringilla malesuada nibh non elementum. Duis aliquam tempor justo. Mauris risus lorem, eleifend vel nulla in, ultricies vehicula justo. Quisque cursus nisi eget ante pellentesque, at ultrices purus blandit. Pellentesque maximus massa felis, id pulvinar augue viverra at.',
        'Quisque sagittis nibh ex, ultrices pharetra lacus suscipit non. Donec aliquam massa sit amet laoreet blandit. Aenean ac ipsum ornare, eleifend risus a, malesuada est. Cras tempus pharetra accumsan. Nunc sed tortor pharetra, elementum sapien eget, semper augue. Suspendisse volutpat metus sem, ut aliquam erat maximus finibus. Etiam accumsan in tellus eget rhoncus. Integer quam augue, egestas non consequat nec, pretium non augue. Nulla nec rhoncus enim, at ornare ante. Nulla quis aliquet eros. Sed hendrerit ac orci sed imperdiet. Sed commodo augue diam, eget consequat ligula vestibulum quis. Maecenas dignissim nisi et ipsum elementum aliquam. Sed cursus justo id lectus ultricies, sit amet posuere nibh lobortis.',
        'Aliquam tempor augue sapien, et vestibulum turpis luctus vulputate. Curabitur tortor nibh, facilisis et mauris at, consequat faucibus leo. Morbi congue purus sit amet elit vehicula lobortis. In ultrices interdum iaculis. Pellentesque nulla tellus, consectetur eu nisi nec, facilisis rhoncus velit. Donec egestas sed mi et fermentum. Vestibulum tristique, ligula non dictum lobortis, felis tortor feugiat neque, sodales imperdiet est quam in odio. Praesent id elit laoreet, suscipit sem id, dignissim leo. Quisque vitae turpis tortor. Morbi suscipit euismod cursus. Ut lacinia egestas erat eget molestie. Donec iaculis, sem nec eleifend sodales, dolor nibh fringilla tortor, eget pretium nulla lectus a justo.',
    ]

    text_collection = TextCollection()

    for t in all_texts:
        new_text = Text()
        new_text.words.extend(sanitize(t))
        new_text.make_persistent()
        text_collection.add_text(new_text)

    text_collection.make_persistent()

    # Generation finished, starting wordcount

    result = TextStats(dict())
    result.make_persistent()

    for text in text_collection:
        partialResult = text.word_count()
        result.merge_with(partialResult)

    # Wait for result to end its reduction
    waitForAllTasks()

    print "Most used words in text:\n%s" % result.top_words(10)

    # BUG I should re-register, but ain't nobody got time for that
    # print "Words: %d" % result.get_total()
