#! /usr/bin/python
# -*- coding: utf-8 -*-

from . import jvm


class Tagger:
  def pos(self, phrase):
    """POS tagger.
    :param flatten: If False, preserves eojeols."""

    result = self.daon.pos(phrase)

    morphemes = [(result.get(k).getWord(), result.get(k).getTag().toString())
                 for k in range(result.size())]

    return morphemes

  def morphs(self, phrase):
    """Parse phrase to morphemes."""

    return [s for s, t in self.pos(phrase)]

  def nouns(self, phrase):
    """Noun extractor."""

    return [s for s in self.daon.nouns(phrase)]

  def morphs(self, phrase):
    """Parse phrase to morphemes."""

    return [s for s, t in self.pos(phrase)]

  def __init__(self, model_path=None, url=None):
    jvm.init_jvm()

    self.daon = jvm.get_jvm().daon.core.Daon()

    if model_path:
      model = jvm.get_jvm().daon.core.util.ModelUtils.loadModelByFile(model_path)
      if model.isSuccess():
        jvm.get_jvm().daon.core.util.ModelUtils.setModel(model)
      else:
        print(model.getErrorMsg())
    elif url:
      model = jvm.get_jvm().daon.core.util.ModelUtils.loadModelByUrl(url)
      if model.isSuccess():
        jvm.get_jvm().daon.core.util.ModelUtils.setModel(model)
      else:
        print(model.getErrorMsg())