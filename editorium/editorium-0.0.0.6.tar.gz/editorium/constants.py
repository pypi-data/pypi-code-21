OPTION_ALIGN_LEFT = object()
"""
Controls Editor_Nullable and Editor_Boolean. 

Setting this to `True` will align the checkbox left, when the editor is hidden. Only useful when OPTION_HIDE is set.

Type: bool-like
"""

OPTION_VISUAL_TRISTATE = object()
"""Controls Editor_Nullable.

Setting this to `True` will toggle the checkbox between partial and full, instead of between off and full, useful for some custom stylesheets.

Type: bool-like
"""

OPTION_HIDE = object()
"""
Controls editor behaviour.

Setting this to a `True` value will hide, rather than disable, the editor. If this is not `True`, it specifies the text displayed when hidden.

Type: bool and string-like
"""

OPTION_BOOLEAN_RADIO = object()
"""
Controls Editor_Boolean.

Setting this to `True` will present radio buttons, rather than checkboxes. If OPTION_BOOLEAN_TEXTS is not specified, empty texts default to ('true','false','none')

Type: bool-like
"""

OPTION_BOOLEAN_TEXTS = object()
"""Controls Editor_Boolean.
 
Set this to a tuple of 3: yes text, no text, indeterminate text. This is ('','','').

Type: tuple of str, str, str 
"""

OPTION_ENUM_NONE = object()
"""
Sets the Editor_Enum 'none' text.

Type: str-like
"""