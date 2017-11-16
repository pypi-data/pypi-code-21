from enum import Enum as _Enum

from .tecutil.constant import *

TECUTIL_BAD_ID = 0


class Color(_Enum):
    Black = 0
    Red = 1
    Green = 2
    Blue = 3
    Cyan = 4
    Yellow = 5
    Purple = 6
    White = 7

    Custom1 = 8
    Custom2 = 9
    Custom3 = 10
    Custom4 = 11
    Custom5 = 12
    Custom6 = 13
    Custom7 = 14
    Custom8 = 15
    Custom9 = 16
    Custom10 = 17
    Custom11 = 18
    Custom12 = 19
    Custom13 = 20
    Custom14 = 21
    Custom15 = 22
    Custom16 = 23
    Custom17 = 24
    Custom18 = 25
    Custom19 = 26
    Custom20 = 27
    Custom21 = 28
    Custom22 = 29
    Custom23 = 30
    Custom24 = 31
    Custom25 = 32
    Custom26 = 33
    Custom27 = 34
    Custom28 = 35
    Custom29 = 36
    Custom30 = 37
    Custom31 = 38
    Custom32 = 39
    Custom33 = 40
    Custom34 = 41
    Custom35 = 42
    Custom36 = 43
    Custom37 = 44
    Custom38 = 45
    Custom39 = 46
    Custom40 = 47
    Custom41 = 48
    Custom42 = 49
    Custom43 = 50
    Custom44 = 51
    Custom45 = 52
    Custom46 = 53
    Custom47 = 54
    Custom48 = 55
    Custom49 = 56
    Custom50 = 57
    Custom51 = 58
    Custom52 = 59
    Custom53 = 60
    Custom54 = 61
    Custom55 = 62
    Custom56 = 63

    MultiColor = -1
    NoColor = -2
    MultiColor2 = -3
    MultiColor3 = -4
    MultiColor4 = -5

    RGBColor = -6

    MultiColor5 = -7
    MultiColor6 = -8
    MultiColor7 = -9
    MultiColor8 = -10

    InvalidColor = -255

    # These names are close, though not always
    # the mathematically closest, to the XKCD colors
    Grey = Custom1
    LightGrey = Custom2
    Orange = Custom3
    LimeGreen = Custom4
    AquaGreen = Custom5
    BrightBlue = Custom6
    Violet = Custom7
    HotPink = Custom8
    Mahogany = Custom9
    LightSalmon = Custom10
    LightOrange = Custom11
    LightGreen = Custom12
    SeaGreen = Custom13
    WarmBlue = Custom14
    LightPurple = Custom15
    Coral = Custom16
    Olive = Custom17
    Creme = Custom18
    Lemon = Custom19
    Spearmint = Custom20
    BrightCyan = Custom21
    BluePurple = Custom22
    LightMagenta = Custom23
    RedOrange = Custom24
    Forest = Custom25
    LightMintGreen = Custom26
    YellowGreen = Custom27
    Emerald = Custom28
    SkyBlue = Custom29
    Indigo = Custom30
    BubbleGum = Custom31
    Cinnamon = Custom32
    DarkTurquoise = Custom33
    LightCyan = Custom34
    LemonGreen = Custom35
    Chartreuse = Custom36
    Azure = Custom37
    RoyalBlue = Custom38
    BrightPink = Custom39
    DeepRed = Custom40
    DarkBlue = Custom41
    LightBlue = Custom42
    MustardGreen = Custom43
    LeafGreen = Custom44
    Turquoise = Custom45
    OceanBlue = Custom46
    Magenta = Custom47
    Raspberry = Custom48
    DeepViolet = Custom49
    Lilac = Custom50
    Khaki = Custom51
    Fern = Custom52
    GreyTeal = Custom53
    DuskyBlue = Custom54
    MediumPurple = Custom55
    LightMaroon = Custom56


class Alignment(_Enum):
    Left = 0  # horizonal
    Right = 1
    Middle = 2
    Top = 3
    Bottom = 4


class AxisLine3DAssignment(_Enum):
    Automatic = 0

    YMinZMin = 1  # x-axis
    YMaxZMin = 2
    YMinZMax = 3
    YMaxZMax = 4

    ZMinXMin = YMinZMin  # y-axis
    ZMaxXMin = YMaxZMin
    ZMinXMax = YMinZMax
    ZMaxXMax = YMaxZMax

    XMinYMin = YMinZMin  # z-axis
    XMaxYMin = YMaxZMin
    XMinYMax = YMinZMax
    XMaxYMax = YMaxZMax


class AuxDataType(_Enum):
    String = 0


class AuxDataObjectType(_Enum):
    Dataset = 0
    Frame = 1
    Layout = 2
    Linemap = 3
    Page = 4
    Variable = 5
    Zone = 6


class SymbolType(_Enum):
    Text = 0
    Geometry = 1


class TileMode(_Enum):
    Grid = 'TILEFRAMESSQUARE'
    Wrap = 'TILEFRAMESWRAP'
    Rows = 'TILEFRAMESVERT'
    Columns = 'TILEFRAMESHORIZ'


class RemoteConnectionMethod(_Enum):
    Tunneled = 'Tunneled'
    Direct = 'Direct'
    Manual = 'Manual'


class BinaryFileVersion(_Enum):
    Tecplot2006 = 0
    Tecplot2008 = 1
    Tecplot2009 = 2
    Current = 3


class IJKLines(_Enum):
    I = 0
    J = 1
    K = 2


class StreamtraceType(_Enum):
    Line = 0
    Rod = 1
    Ribbon = 2


class StreamtraceLocation(_Enum):
    Surface = 0
    Volume = 1


# Alias enumeration values
StepMode = SkipMode

_FunctionDependency = FunctionDependency


class FunctionDependency(_Enum):
    XIndependent = _FunctionDependency.XIndependent.value
    YIndependent = _FunctionDependency.YIndependent.value

    RIndependent = _FunctionDependency.YIndependent.value
    ThetaIndependent = _FunctionDependency.XIndependent.value


_PlotType = PlotType


class PlotType(_Enum):
    Automatic = _PlotType.Automatic.value
    Cartesian3D = _PlotType.Cartesian3D.value
    Cartesian2D = _PlotType.Cartesian2D.value
    XYLine = _PlotType.XYLine.value
    Sketch = _PlotType.Sketch.value
    PolarLine = _PlotType.PolarLine.value

    # Note that we use "Active" here to indicate "None",
    # where we have decided that "None" is not a good name
    # for the default because it implies "No plot".
    Active = _PlotType.Automatic.value


class ReadDataOption(_Enum):
    ReplaceInActiveFrame = 0
    Append = 1
    Replace = 2

class SliceSurface(_Enum):
    XPlanes = 0
    YPlanes = 1
    ZPlanes = 2
    IPlanes = 3
    JPlanes = 4
    KPlanes = 5
    # CVar = 6  (Internal SDK use only)
    Arbitrary = 7

