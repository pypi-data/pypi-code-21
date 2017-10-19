from hwt.synthesizer.exceptions import IntfLvlConfErr
from hwt.synthesizer.interfaceLevel.interfaceUtils.utils import walkParams
from hwt.synthesizer.interfaceLevel.mainBases import UnitBase
from hwt.synthesizer.interfaceLevel.propDeclrCollector import PropDeclrCollector
from hwt.synthesizer.interfaceLevel.unitImplHelpers import UnitImplHelpers
from hwt.synthesizer.rtlLevel.netlist import RtlNetlist


class Unit(UnitBase, PropDeclrCollector, UnitImplHelpers):
    """
    Container of the netlist with interfaces and internal hierarchical structure

    :cvar _serializeDecision: function to decide if Hdl object derived from
        this unit should be serialized or not, if None all is always serialized
    :ivar _interfaces: all interfaces
    :ivar _units: all units defined on this obj
    :ivar _params: all params defined on this obj
    :ivar _parent: parent object (Unit instance)
    :ivar _lazyLoaded: container of rtl object which were lazy loaded in implementation phase
        (this object has to be returned from _toRtl of parent before it it's own objects)
    """

    _serializeDecision = None

    def __init__(self):
        self._parent = None
        self._lazyLoaded = []
        self._cntx = RtlNetlist(self)

        self._loadConfig()

    def _toRtl(self):
        """
        synthesize all subunits, make connections between them, build entity and component for this unit
        """
        assert not self._wasSynthetised()
        if not hasattr(self, "_name"):
            self._name = self._getDefaultName()
        self._cntx.params = self._buildParams()
        self._externInterf = []

        # prepare subunits
        for u in self._units:
            yield from u._toRtl()

        for u in self._units:
            subUnitName = u._name
            u._signalsForMyEntity(self._cntx, "sig_" + subUnitName)

        # prepare signals for interfaces
        for i in self._interfaces:
            signals = i._signalsForInterface(self._cntx)
            if i._isExtern:
                self._externInterf.extend(signals)

        self._loadMyImplementations()
        yield from self._lazyLoaded

        if not self._externInterf:
            raise Exception(("Can not find any external interface for unit %s"
                             "- there is no such a thing as unit without interfaces") % self._name)

        yield from self._synthetiseContext(self._externInterf)
        self._checkArchCompInstances()
        for intf in self._interfaces:
            intf._setDirLock(True)

    def _wasSynthetised(self):
        return self._cntx.synthesised

    def _synthetiseContext(self, externInterf):
        # synthesize signal level context
        s = self._cntx.synthesize(self._name, externInterf)
        self._entity = s[0]
        self._entity.__doc__ = self.__doc__
        self._entity.origin = self

        self._architecture = s[1]

        for intf in self._interfaces:
            if intf._isExtern:
                intf._resolveDirections()
                # reverse because other components looks at this one from outside
                intf._reverseDirection()

        # connect results of synthesized context to interfaces of this unit
        self._boundInterfacesToEntity(self._interfaces)
        yield from s

        # after synthesis clean up interface so unit can be used elsewhere
        self._cleanAsSubunit()

    def _loadInterface(self, i, isExtern):
        i._loadDeclarations()
        i._setAsExtern(isExtern)

    def _loadDeclarations(self):
        """
        Load all declarations from _decl() method, recursively for all interfaces/units.
        """
        if not hasattr(self, "_interfaces"):
            self._interfaces = []
        if not hasattr(self, "_units"):
            self._units = []
        self._setAttrListener = self._declrCollector
        self._declr()
        self._setAttrListener = None
        for i in self._interfaces:
            self._loadInterface(i, True)

        # if I am a unit load subunits
        for u in self._units:
            u._loadDeclarations()
        for p in self._params:
            p.setReadOnly()

    def _registerIntfInImpl(self, iName, intf):
        """
        Register interface in implementation phase
        """
        self._registerInterface(iName, intf)
        self._loadInterface(intf, False)
        intf._signalsForInterface(self._cntx)

    @classmethod
    def _build(cls, multithread=True):
        """
        This Unit implementation does not require any preprocessing
        """
        pass

    def _buildParams(self):
        # construct params for entity (generics)
        globalNames = {}

        def addP(n, p):
            p.name = n
            if n in globalNames:
                raise IntfLvlConfErr("Redefinition of generic '%s' while synthesis old:%r, new:%r" % 
                                     (n, globalNames[n], p))
            globalNames[n] = p

        def nameForNestedParam(p):
            n = ""
            node = p
            while node is not self:
                if n == "":
                    n = node._name
                else:
                    n = node._name + "_" + n
                node = node._parent

            return n

        discoveredParams = set()
        for p in self._params:
            discoveredParams.add(p)
            addP(p.name, p)

        for intf in self._interfaces:
            for p in walkParams(intf, discoveredParams):
                n = nameForNestedParam(p)
                addP(n, p)

        return globalNames

    def _getDefaultName(self):
        return self.__class__.__name__

    def _checkArchCompInstances(self):
        cInstances = len(self._architecture.componentInstances)
        units = len(self._units)
        if cInstances != units:
            inRtl = set(map(lambda x: x.name, self._architecture.componentInstances))
            inIntf = set(map(lambda x: x._name + "_inst", self._units))
            if cInstances > units:
                raise IntfLvlConfErr("_toRtl unit(s) %s were found in rtl but were not registered at %s" % 
                                     (str(inRtl - inIntf), self._name))
            elif cInstances < units:
                raise IntfLvlConfErr("_toRtl of %s: unit(s) %s were lost" % 
                                     (self._name, str(inIntf - inRtl)))
