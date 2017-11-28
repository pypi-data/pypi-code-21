from typing import List, cast

from mhelper import reflection_helper, array_helper


__default_editorium = None
__pending_editors = [ ]  # type: List


def default_editorium():
    """
    Obtains the default editorium, creating it if it doesn't already exist.
    :return: An object of class `Editorium`.
    :rtype: Editorium  
    """
    global __default_editorium, __pending_editors
    
    if __default_editorium is None:
        from editorium.editorium_qt import EditorBase, Editorium, Editor_Bool, Editor_Enum, Editor_Flags, Editor_Float, Editor_Int, Editor_Filename, Editor_String, Editor_GenericList, Editor_Nullable, Editor_Fallback, Editor_ReadOnly, Editor_Annotation
        
        __default_editorium = Editorium()
        __default_editorium.editors.append( Editor_ReadOnly )  # must be first
        __default_editorium.editors.append( Editor_Filename )
        __default_editorium.editors.append( Editor_Annotation )
        __default_editorium.editors.append( Editor_Bool )
        __default_editorium.editors.append( Editor_Enum )
        __default_editorium.editors.append( Editor_Flags )
        __default_editorium.editors.append( Editor_Float )
        __default_editorium.editors.append( Editor_Int )
        __default_editorium.editors.append( Editor_String )
        __default_editorium.editors.append( Editor_GenericList )
        __default_editorium.editors.append( Editor_Nullable )
        __default_editorium.editors.append( Editor_Fallback )  # must be last
        
        for editor_or_function in __pending_editors:
            for editor in array_helper.as_iter( reflection_helper.dedelegate( editor_or_function, EditorBase ) ):
                __default_editorium.register( editor )
        
        __pending_editors = cast( List, None )
    
    return __default_editorium


def register( editor_or_function ) -> None:
    """
    Deferred registration for an editor or editors with the default editorium.
    
    If the default editorium is not yet created, the registration will be deferred until it is created.
    This allows the programmer to register editors at software start, but only load Qt if the editors will actually be used.
    
    If the editor-type also requires Qt to be loaded, a function can be provided that will be called instead.
    
    :param editor_or_function: Either:
                                    * An editor (EditorBase-derived class. The class, not an instance.)
                                    * A collection of editors (must be `list` or `tuple`)
                                    * A function returning an editor
                                    * A function returning a list of editors
                                    * Nb. A list of functions is not accepted 
    """
    if __default_editorium is not None:
        from editorium.editorium_qt import EditorBase
        for editor in array_helper.as_iter( reflection_helper.dedelegate( editor_or_function, EditorBase ) ):
            __default_editorium.register( editor )
    else:
        __pending_editors.append( editor_or_function )
