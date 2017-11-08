""" Public interfaces
"""
# Browser layer
from eea.annotator.browser.interfaces import ILayer

# Control Panel
from eea.annotator.controlpanel.interfaces import ISettings

# Subtypes
from eea.annotator.subtypes.interfaces import IAnnotatorAware
from eea.annotator.subtypes.interfaces import IDexterityAnnotatorAware

# Storage
from eea.annotator.storage.interfaces import IAnnotatorStorage

__all__ = [
    ILayer.__name__,
    ISettings.__name__,
    IAnnotatorAware.__name__,
    IDexterityAnnotatorAware.__name__,
    IAnnotatorStorage.__name__,
]
