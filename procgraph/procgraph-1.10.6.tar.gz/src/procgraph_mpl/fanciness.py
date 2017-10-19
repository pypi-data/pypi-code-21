
# str -> function f(pyplot)
fancy_styles = {}


def style(f):
    fancy_styles[f.__name__] = f
    return f


@style
def dickinsonA(pylab):
    set_spines_look_A(pylab)


def remove_spine(pylab, which):
    ax = pylab.gca()
    ax.spines[which].set_color('none')


@style
def notopaxis(pylab):
    remove_spine(pylab, 'top')


@style
def nobottomaxis(pylab):
    remove_spine(pylab, 'bottom')


@style
def noxticks(pylab):
    pylab.xticks([], [])


@style
def noyticks(pylab):
    pylab.yticks([], [])


@style
def turn_off_right(pylab):
    ax = pylab.gca()
    for loc, spine in ax.spines.iteritems():
        if loc in ['right']:
            spine.set_color('none')  # don't draw spine 
    ax.yaxis.set_ticks_position('left')


@style
def turn_off_left_right(pylab):
    ax = pylab.gca()
    for loc, spine in ax.spines.iteritems():
        if loc in ['right', 'left']:
            spine.set_color('none')  # don't draw spine 
    ax.yaxis.set_ticks_position('none')


@style
def turn_off_top(pylab):
    ax = pylab.gca()
    for loc, spine in ax.spines.iteritems():
        if loc in ['top']:
            spine.set_color('none')  # don't draw spine 
    ax.xaxis.set_ticks_position('bottom')


@style
def spines_outward(pylab, offset=10):
    ax = pylab.gca()
    for loc, spine in ax.spines.iteritems():
        if loc in ['left', 'bottom', 'top', 'right']:
            spine.set_position(('outward', offset))

@style
def turn_off_all_axes(pylab):
    turn_off_bottom_and_top(pylab)
    turn_off_left_right(pylab)

@style
def turn_off_bottom_and_top(pylab):
    ax = pylab.gca()
    for loc, spine in ax.spines.iteritems():
        if loc in ['bottom', 'top']:
            spine.set_color('none')  # don't draw spine
            
    pylab.xticks([], [])



def set_spines_outward(pylab, outward_offset=10):
    ax = pylab.gca()
    for loc, spine in ax.spines.iteritems():
        if loc in ['left', 'bottom']:
            spine.set_position(('outward', outward_offset))
        elif loc in ['right', 'top']:
            spine.set_color('none')  # don't draw spine
        else:
            raise ValueError('unknown spine location: %s' % loc)

    # turn off ticks where there is no spine
    ax.xaxis.set_ticks_position('bottom')
    ax.yaxis.set_ticks_position('left')

    
def set_spines_look_A(pylab, outward_offset=10,
                      linewidth=2, markersize=3, markeredgewidth=1):
    ''' 
        Taken from 
        http://matplotlib.sourceforge.net/examples/pylab_examples
        /spine_placement_demo.html
    '''
    set_spines_outward(pylab, outward_offset=outward_offset)
    ax = pylab.gca()

    for l in ax.get_xticklines() + ax.get_yticklines():
        l.set_markersize(markersize)
        l.set_markeredgewidth(markeredgewidth)

    try:
        ax.get_frame().set_linewidth(linewidth)
    except BaseException as e:
        print('set_linewidth() not working in matplotlib 1.3.1')
        print(e)



@style
def dottedzero(pylab):
    pass
#     a = pylab.axis()
#     pylab.plot([a[0], a[1]], [0, 0], '--')


