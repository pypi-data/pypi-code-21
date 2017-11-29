# -*- coding: latin-1 -*-


from .textmodel import texeltree
from .textmodel.textmodel import TextModel
from .textmodel.texeltree import NewLine, Group, Text, length
from .textmodel.styles import EMPTYSTYLE
from .wxtextview.testdevice import TESTDEVICE
from .wxtextview.builder import BuilderBase
from .wxtextview.boxes import TextBox, NewlineBox, TabulatorBox, EmptyTextBox, \
    EndBox, check_box, Box, calc_length



class Builder(BuilderBase):
    parstyle = EMPTYSTYLE

    def __init__(self, device=TESTDEVICE):
        self.device = device
        self.model = model
        self._maxw = maxw

        import weakref
        self.cache = weakref.WeakValueDictionary()
        BuilderBase.__init__(self, model, device)

    def get_device(self):
        return self.device

    def mk_style(self, style):
        # This can overriden e.g. to implement style sheets. The
        # default behaviour is to use the paragraph style and add the
        # text styles.
        r = self.parstyle.copy()
        r.update(style)
        return r

    def extended_texel(self):
        return self.model.get_xtexel()
        
    def set_maxw(self, maxw):
        if maxw != self._maxw:
            self._maxw = maxw
            self.rebuild()

    ### Factory methods
    def create_boxes(self, texel):
        try:
            return self.cache[texel]
        except KeyError:
            pass

        name = texel.__class__.__name__+'_handler'
        handler = getattr(self, name)
        #print "calling handler", name
        l = handler(texel)
        try:
            assert calc_length(l) == length(texel)
        except:
            print "handler=", handler
            raise
        r = tuple(l)
        self.cache[texel] = r
        return r

    def Group_handler(self, texel):
        # Handles group texels. Note that the list of childs is
        # traversed from right to left. This way the "Newline" which
        # ends a line is handled before the content in the line. This
        # is important because in order to build boxes for the line
        # elements, we need the paragraph style which is located in
        # the NewLine-Texel.
        create_boxes = self.create_boxes
        r = ()
        for j1, j2, child in reversed(list(texeltree.iter_childs(texel))):
            r = create_boxes(child)+r
        return r

    # XXX Remove this:
    _cache = dict()
    _cache_keys = []
    def Text_handler(self, texel):
        # cached version
        key = texel.text, id(texel.style), id(self.parstyle), self.device
        try:
            return self._cache[key]
        except: pass        
        r = [TextBox(texel.text, self.mk_style(texel.style), 
                     self.device)]
        self._cache_keys.insert(0, key)        
        if len(self._cache_keys) > 10000:
            _key = self._cache_keys.pop()
            del self._cache[_key]
        self._cache[key] = r
        return r

    def Text_handler(self, texel):
        # non caching version
        return [TextBox(texel.text, self.mk_style(texel.style), 
                self.device)]

    def NewLine_handler(self, texel):
        self.parstyle = texel.parstyle
        if texel.is_endmark:
            return [self.EndBox(self.mk_style(texel.style), self.device)]
        return [NewlineBox(self.mk_style(texel.style), self.device)] # XXX: Hmmmm

    def Tabulator_handler(self, texel):
        return [TabulatorBox(self.mk_style(texel.style), self.device)]

    def TextCell_handler(self, texel):
        textbox = self.create_parstack(Group(texel.childs[1:]))
        cell = TextCellBox(textbox, device=self.device)
        assert len(cell) == length(texel)
        return [cell]

    def ScriptingCell_handler(self, texel):
        #dump_range(texel, 0, length(texel))
        
        # XXX TODO: implement proper treatment of temp
        sep1, (j1, j2, inp), sep2, (k1, k2, outp), sep3 \
            = texeltree.iter_childs(texel)

        _inp = Group(cell.childs[1:3])
        client = self._clients.get_matching(cell)
        colorized = client.colorize(_inp)
        inbox = self.create_parstack(colorized)
        assert len(inbox) == length(_inp)
        
        outbox = self.create_parstack(_outp)
        cell = ScriptingCellBox(inbox, outbox, number=texel.number,
                                device=self.device)
        assert len(cell) == n
        return [cell]

    def Plot_handler(self, texel):
        return [PlotBox(device=self.device)]

    def Graphics_handler(self, texel):
        return [GraphicsBox(texel, device=self.device)]

    def BitmapRGB_handler(self, texel):
        w, h = texel.size
        bitmap = wx.BitmapFromBuffer(w, h, texel.data)
        return [BitmapBox(bitmap, device=self.device)]

    def BitmapRGBA_handler(self, texel):
        w, h = texel.size
        im = wx.ImageFromData(w, h, texel.data)
        im.SetAlphaBuffer(texel.alpha)
        bitmap = wx.BitmapFromImage(im)
        return [BitmapBox(bitmap, device=self.device)]

    ### Builder methods
    def create_paragraphs(self, texel):
        # Ich müsste jeden Paragraphen separat erzeugen!
        boxes = self.create_boxes(texel)
        if self._maxw:
            maxw = max(100, self._maxw-80)
        else:
            maxw = 0
        l = create_paragraphs(
            boxes, maxw = maxw,
            Paragraph = self.Paragraph,
            device = self.device)
        return l

    def create_parstack(self, texel):
        l = self.create_paragraphs(texel, 0, length(texel))
        return ParagraphStack(l, device=self.device)

    def rebuild(self):
        model = self.model
        boxes = self.create_boxes(model.texel)
        self._layout = VGroup(boxes, device=self.device)


    ### Signal handlers
    def properties_changed(self, i1, i2):
        self.rebuild()

    def inserted(self, i, n):
        self.rebuild()

    def removed(self, i, n):
        #print "removed", i, n
        self.rebuild()





def test_00():
    model = TextModel(u'for a in range(5):\n    print a')
    cell = ScriptingCell(tmp.texel, NULL_TEXEL)
    model.insert(len(model), mk_textmodel(cell))

    assert find_cell(model.texel, 1) == (0, cell)

    view = ns['view']
    view.index = 1
    layout = view.builder.get_layout()
    r1 = layout.get_rect(0, 0, 0)
    assert r1.x2-r1.x1 == sepwidth

    r2 = layout.get_cursorrect(0, 0, 0, {})
    r3 = layout.get_cursorrect(len(model), 0, 0, {})
    assert r3.x2-r3.x1 == sepwidth
    assert r3.y1 > r2.y1
