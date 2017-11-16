import logging

from contextlib import contextmanager
from ctypes import c_size_t, c_int64

from ..tecutil import _tecutil
from ..constant import StateChange
from ..tecutil import ArgList, IndexSet, flatten_args, lock, sv


log = logging.getLogger(__name__)


@lock()
def state_changed(what, variables=None, zones=None, index=None, dataset=None,
                  uniqueid=None):
    if variables is not None and not hasattr(variables, '__iter__'):
        variables = [variables]
    if zones is not None and not hasattr(zones, '__iter__'):
        zones = [zones]

    if __debug__:
        if dataset is not None:
            if variables is not None:
                if any(v.dataset != dataset for v in variables):
                    msg = 'Variables are not members of the dataset specified.'
                    raise TecplotLogicError(msg)
            if zones is not None:
                if any(z.dataset != dataset for z in zones):
                    msg = 'Zones are not members of the dataset specified.'
                    raise TecplotLogicError(msg)
        if variables is not None:
            if zones is not None:
                for z in zones:
                    if any(v.dataset != z.dataset for v in variables):
                        msg = 'Zones and variables are not part of the same dataset.'
                        raise TecplotLogicError(msg)

    allocd = []
    try:
        with ArgList() as arglist:
            arglist[sv.STATECHANGE] = what

            if variables is not None:
                varlist = IndexSet(*variables)
                allocd.append(varlist)
                arglist[sv.VARLIST] = varlist

                if dataset is None:
                    arglist[sv.DATASETUNIQUEID] = variables[0].dataset.uid

            if zones is not None:
                zonelist = IndexSet(*zones)
                allocd.append(zonelist)
                arglist[sv.ZONELIST] = zonelist

                if (variables is None) and (dataset is None):
                    arglist[sv.DATASETUNIQUEID] = zones[0].dataset.uid

            if dataset is not None:
                arglist[sv.DATASETUNIQUEID] = c_size_t(dataset.uid)

            if index is not None:
                arglist[sv.INDEX] = index + 1

            if uniqueid is not None:
                arglist[sv.UNIQUEID] = c_size_t(uniqueid)

            if __debug__:
                strlist = ['{}: {}'.format(k,v) for k,v in arglist.items()]
                msg = 'State Changed:\n  '+'\n  '.join(strlist)
                log.debug(msg)

            _tecutil.StateChangedX(arglist)

    finally:
        for a in allocd:
            a.dealloc()


@contextmanager
def state_change(obj, **kwargs):
    obj._state_change_depth = getattr(obj, '_state_change_depth', 0) + 1
    if obj._state_change_depth > 1:
        obj._state_change_kw.update(**kwargs)
        yield obj._state_change_kw
    else:
        try:
            obj._state_change_kw = kwargs
            yield obj._state_change_kw
        finally:
            state_changed(**obj._state_change_kw)


@lock()
def zones_added(*zones):
    with IndexSet(*zones) as zoneset:
        with ArgList(STATECHANGE=StateChange.ZonesAdded) as arglist:
            arglist['ZONELIST'] = zoneset
            _tecutil.StateChangedX(arglist)


'''
class StateChange(Enum):
    VarsAltered               =  0
    VarsAdded                 =  1
    ZonesDeleted              =  2
    ZonesAdded                =  3
    NodeMapsAltered           =  4
    FrameDeleted              =  5
    #NewTopFrame              =  6  /* deprecated: use NewActiveFrame and/or FrameOrderChange */
    Style                     =  7
    DataSetReset              =  8
    NewLayout                 =  9
    #CompleteReset            = 10  /* deprecated: no longer broadcast */
    LineMapAssignment         = 11
    ContourLevels             = 12
    ModalDialogLaunch         = 13
    ModalDialogDismiss        = 14
    QuitTecplot               = 15
    ZoneName                  = 16
    VarName                   = 17
    LineMapName               = 18
    LineMapAddDeleteOrReorder = 19
    View                      = 20
    ColorMap                  = 21
    ContourVar                = 22
    Streamtrace               = 23
    NewAxisVariables          = 24
    MouseModeUpdate           = 25
    PickListCleared           = 26
    PickListGroupSelect       = 27
    PickListSingleSelect      = 28
    PickListStyle             = 29
    JournalReset              = 30
    UnsuspendInterface        = 31
    SuspendInterface          = 32
    DataSetLockOn             = 33
    DataSetLockOff            = 34
    Text                      = 35
    Geom                      = 36
    DataSetTitle              = 37
    DrawingInterrupted        = 38
    PrintPreviewLaunch        = 39
    PrintPreviewDismiss       = 40
    AuxDataAdded              = 41
    AuxDataDeleted            = 42
    AuxDataAltered            = 43
    VarsDeleted               = 44
    TecplotIsInitialized      = 45
    ImageExported             = 46
    VariableLockOn            = 47
    VariableLockOff           = 48
    PageDeleted               = 49
    NewTopPage                = 50
    NewActiveFrame            = 51
    FrameOrderChanged         = 52
    NewUndoState              = 53
    MacroFunctionListChanged  = 54
    AnimationStart            = 55
    AnimationEnd              = 56
    MacroRecordingStarted     = 57
    MacroRecordingEnded       = 58
    MacroRecordingCanceled    = 59
    ZoneSolutionTimeAltered   = 60
    LayoutAssociation         = 61
    CopyView                  = 62
    ColorMapDeleted           = 63
    OpenLayout                = 64
    MacroLoaded               = 65
    PerformingUndoBegin       = 66
    PerformingUndoEnd         = 67
'''
