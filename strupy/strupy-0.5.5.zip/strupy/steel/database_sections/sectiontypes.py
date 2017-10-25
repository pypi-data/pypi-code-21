'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.2 date 2017-03-06

This file is part of StruPy.
StruPy is a structural engineering design Python package.
http://strupy.org/

StruPy is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

StruPy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Foobar; if not, write to the Free Software
Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
--------------------------------------------------------------------------
File version 0.2 changes:
- python3 tested
'''

import math

import strupy.units as u

#Groups in families definition
sectiongroups = {}
#I-beams 10-19
sectiongroups[10] = 'Single I-beam'
sectiongroups[11] = 'Double I-beam'

#Channels 20-29
sectiongroups[20] = 'Single channel'
sectiongroups[21] = 'Double channel flanges to flanges'
sectiongroups[22] = 'Double channel back to back'
#Angels 30-29
sectiongroups[30] = 'Single Angel'
sectiongroups[31] = 'Double angles in cruciform-like shape'
sectiongroups[32] = 'Double angles legs back to back'
#Solid bars 40-49
sectiongroups[40] = 'Rectangular bar'
sectiongroups[41] = 'Round bar'
#Flat bars 50-59
sectiongroups[50] = 'Flat bar'
#Tubes 60-69
sectiongroups[60] = 'Round hollow tube'
sectiongroups[61] = 'Hexagonal hollow tube'
sectiongroups[62] = 'Rectangular hollow tube'
#Tee
sectiongroups[70] = 'Structural tee'
sectiongroups[71] = 'Tee cut from I-beam'


#Dict with figure for each groups init
figuregrouplist = {}
figuregrouplist[10] = set()
figuregrouplist[11] = set()
#----
figuregrouplist[20] = set()
figuregrouplist[21] = set()
figuregrouplist[22] = set()
#----
figuregrouplist[30] = set()
figuregrouplist[31] = set()
figuregrouplist[32] = set()
#----
figuregrouplist[40] = set()
figuregrouplist[41] = set()
#----
figuregrouplist[50] = set()
#----
figuregrouplist[60] = set()
figuregrouplist[61] = set()
figuregrouplist[62] = set()
#----
figuregrouplist[70] = set()
figuregrouplist[71] = set()

#sectionbase_EuropeanSectionDatabase.xml figures in each groups definition 
figuregrouplist[10].update({'HEA', 'HEAA', 'HEB', 'HEC', 'HEM', 'HER', 'IPE', 'IPEA', 'IPEO', 'IPER', 'IPEV', 'IPN', 'PRS'}) #I-beam
figuregrouplist[11].update  ({'IIPE', 'HHEM', 'HHEB', 'HHEA'}) #Double I-beam
#----
figuregrouplist[20].update   ({'UAP', 'UAPP', 'UPAF', 'UPE', 'UPN', 'UUAP', 'UUPN'}) # Single channel
figuregrouplist[21].update   ({'UAPP'}) #Double channel flanges to flanges
figuregrouplist[22].update   ({'UUAP', 'UUPN'}) #Double channel back to back
#----
figuregrouplist[30].update   ({'CAE', 'CAEP', 'CAI', 'CAIP'}) #Single angel
figuregrouplist[31].update   ({'DCEC', 'DCEP'}) #Double angles in cruciform-like shape
figuregrouplist[32].update   ({'DCED', 'DCIG', 'DCIP'}) #Double angles legs back to back
#----
figuregrouplist[40].update   ({'CARR'}) #Rectangular bar
figuregrouplist[41].update   ({'ROND'}) #Round bar
#----
figuregrouplist[50].update   ({'PLAT'}) #Flat bar
#----
figuregrouplist[60].update   ({'TRON'}) #Round hollow tube
figuregrouplist[61].update   ({'THEX'}) #Hexagonal hollow tube
figuregrouplist[62].update   ({'TCAR', 'TREC'}) #Rectangular hollow tube
#----
figuregrouplist[70].update   ({'TEAE', 'TEAI'}) #Structural tee
figuregrouplist[71].update   ({'MIPE', 'MHEM', 'MHEB', 'MHEA'})#Tee cut from I-beam


#function definition
def FigureGroupId (figure = 'MHEM'):
    typeid = 0
    for i in figuregrouplist:
        if figure in figuregrouplist[i]:
            typeid = i
    return typeid
    
def FigureGroupName (figure = 'MHEM'):
    try:
        return sectiongroups[FigureGroupId(figure)]
    except KeyError:
        return 'Unknown_type'
    
def _pointscoordinate(deltapoints):
    result = []
    for i in range(len(deltapoints)):
        tmp=[0*u.cm, 0*u.cm]
        for j in range(i+1):
            tmp[0] += deltapoints[j][0]
            tmp[1] += deltapoints[j][1]
        result.append(tmp)
    return result

def sectioncontourpoints(figure, h, b, ea, es, ra, rs, gap, vz, vpz, vy, vpy, gamma):
    zero = 0 * u.cm
    #----default contourpoints
    contourpoints =  []
    #----I-beam
    if FigureGroupId(figure) == 10:
        deltapoints = [ [-vpy, vz], [b, zero], [zero, -es], [-(b/2-ea/2), zero], 
                        [zero, -(h-2*es)], [(b/2-ea/2), zero], [zero, -es], 
                        [-b, zero], [zero, es], [(b/2-ea/2), zero], [zero, (h-2*es)], 
                        [-(b/2-ea/2), zero], [zero, es]]
        contourpoints = _pointscoordinate(deltapoints)
    #----Double I-beam'
    if FigureGroupId(figure) == 11: 
        deltapoints = [ [zero, vz], [zero, -es], [-(b/4-ea/2), zero], 
                        [zero, -(h-2*es)], [(b/4-ea/2), zero], [zero, -es], 
                        [-b/2, zero], [zero, es], [(b/4-ea/2), zero], [zero, (h-2*es)], 
                        [-(b/4-ea/2), zero], [zero, es], [b/2, zero], 
                        [b/2, zero],[zero, -es], [-(b/4-ea/2), zero], 
                        [zero, -(h-2*es)], [(b/4-ea/2), zero], [zero, -es], 
                        [-b/2, zero], [zero, es], [(b/4-ea/2), zero], [zero, (h-2*es)], 
                        [-(b/4-ea/2), zero], [zero, es]]
        contourpoints = _pointscoordinate(deltapoints)
    #----Channel
    if FigureGroupId(figure) == 20:
        deltapoints = [ [-vpy, vz], [b, zero], [zero, -es], [-(b-ea), zero], 
                        [zero, -(h-2*es)], [(b-ea), zero], [zero, -es], 
                        [-b, zero], [zero, h]]
        contourpoints = _pointscoordinate(deltapoints)
    #----Double channel flanges to flanges
    if FigureGroupId(figure) == 21:
        deltapoints = [ [zero, vz], [zero, -es], [-(b/2-ea), zero], 
                        [zero, -(h-2*es)], [b/2-ea, zero], [zero, -es], 
                        [-b/2, zero], [zero, h], [b/2, zero], 
                        [b/2, zero], [zero, -h], [-b/2, zero], [zero, es],
                        [b/2-ea, zero], [zero, h-2*es],[-(b/2-ea), zero]]
        contourpoints = _pointscoordinate(deltapoints)   
    #----Double channel back to back
    if FigureGroupId(figure) == 22:
        deltapoints = [ [zero, vz], [-b/2, zero], [zero, -es], [b/2-ea, zero], 
                        [zero, -(h-2*es)], [-(b/2-ea), zero], [zero, -es], 
                        [b/2, zero], [zero, h],
                        [b/2, zero], [zero, -es], [-(b/2-ea), zero], [zero, -(h-2*es)],
                        [b/2-ea, zero], [zero, -es], [-b/2, zero]]
        contourpoints = _pointscoordinate(deltapoints)        
    #----Angel
    if FigureGroupId(figure) == 30:
        deltapoints = [[-vpy, vz], [ea, zero], [zero, -(h-es)], [b-ea, zero], [zero, -es], [-b, zero], [zero, h]]
        contourpoints = _pointscoordinate(deltapoints)
    #----#Double  angles in cruciform-like shape
    if FigureGroupId(figure) == 31:
        deltapoints = [ [-vpy, zero], [zero, es], [b/2-ea, zero], [zero, h/2-es], [ea, zero], [zero, -h/2],
                        [zero, -h/2], [ea, zero], [zero, h/2-es], [b/2-ea, zero],[zero, es]]
        contourpoints = _pointscoordinate(deltapoints)
    #----Double angles legs back to back
    if FigureGroupId(figure) == 32:
        deltapoints = [ [zero, vz], [-b/2, zero], [zero, -es], [b/2-ea, zero], [zero, -(h-es)], [ea, zero], [zero, h],
                        [b/2, zero], [zero, -es], [-(b/2-ea), zero],[zero, -(h-es)], [-ea, zero]]
        contourpoints = _pointscoordinate(deltapoints)        
    #----Rectangular bar
    if FigureGroupId(figure) == 40:
        deltapoints = [[-vpy, vz], [b, zero], [zero, -h], [-b, zero], [zero, h]]
        contourpoints = _pointscoordinate(deltapoints)
    #----Round bar
    if FigureGroupId(figure) == 41:
        pi = math.pi
        pt_num = 12
        radius = b/2
        contourpoints = [[radius*math.cos(i/float(pt_num)*2*pi), radius*math.sin(i/float(pt_num)*2*pi)] for i in range(0, pt_num+1)]
    #----Flat bar
    if FigureGroupId(figure) == 50:
        deltapoints = [[-vpy, vz], [b, zero], [zero, -h], [-b, zero], [zero, h]]
        contourpoints = _pointscoordinate(deltapoints)
    #----Round hollow tube
    if FigureGroupId(figure) == 60:
        pi = math.pi
        pt_num = 12
        radius = b/2
        contourpoints = [[radius*math.cos(i/float(pt_num)*2*pi), radius*math.sin(i/float(pt_num)*2*pi)] for i in range(0, pt_num+1)]
        radius = h/2 - ea
        contourpoints += [[radius*math.cos(i/float(pt_num)*2*pi), radius*math.sin(i/float(pt_num)*2*pi)] for i in range(0, pt_num+1)]
    #----Hexagonal hollow tube
    if FigureGroupId(figure) == 61:
        pi = math.pi
        side_num = 6
        radius = b/2
        contourpoints = [[radius*math.cos(i/float(side_num)*2*pi), radius*math.sin(i/float(side_num)*2*pi)] for i in range(0, side_num+1)]
        radius = b/2 - ea
        contourpoints += [[radius*math.cos(i/float(side_num)*2*pi), radius*math.sin(i/float(side_num)*2*pi)] for i in range(0, side_num+1)]
    #----Rectangular hollow tube
    if FigureGroupId(figure) == 62:
        deltapoints = [ [-vpy, vz], [b, zero], [zero, -h], [-b, zero], [zero, h],
                        [ea, -es], [b-2*ea, zero], [zero, -(h-2*es)], [-(b-2*ea), zero], [zero, h-2*es]]
        contourpoints = _pointscoordinate(deltapoints)
    #----Structural tee
    if FigureGroupId(figure) == 70:
        deltapoints = [ [-vpy, -vpz], [b, zero], [zero, es], [-(b/2-ea/2), zero], 
                        [zero, h-es], [-ea, zero], 
                        [zero, -(h-es)], 
                        [-(b/2-ea/2), zero], [zero, -es]]
        contourpoints = _pointscoordinate(deltapoints)
    #----Tee cut from I-beam
    if FigureGroupId(figure) == 71:
        deltapoints = [ [-vpy, vz], [b, zero], [zero, -es], [-(b/2-ea/2), zero], 
                        [zero, -(h-es)], [-ea, zero], 
                        [zero, (h-es)], 
                        [-(b/2-ea/2), zero], [zero, es]]
        contourpoints = _pointscoordinate(deltapoints)
    return contourpoints
    
def draw_geometry(SomeGeometryObiect, figure, sectname, h, b, ea, es, ra, rs, gap, vz, vpz, vy, vpy, gamma, annotation=1):
    #----
    contourpoints = sectioncontourpoints(figure, h, b, ea, es, ra, rs, gap, vz, vpz, vy, vpy, gamma)     
    #----
    if not contourpoints == []:
        #----external size of section
        y_max = max([contourpoints[i][0] for i in range(len(contourpoints))])
        y_min = min([contourpoints[i][0] for i in range(len(contourpoints))])
        z_max = max([contourpoints[i][1] for i in range(len(contourpoints))])
        z_min = min([contourpoints[i][1] for i in range(len(contourpoints))]) 
        #----x and y axis draw
        offset = 1.2
        SomeGeometryObiect.addLine([y_min * offset, 0*u.mm], [y_max * offset, 0*u.mm])
        SomeGeometryObiect.addLine([0*u.mm, z_max * offset], [0*u.mm, z_min * offset])
        if annotation:
            SomeGeometryObiect.addText('y', [y_max * offset, 0*u.mm])
            SomeGeometryObiect.addText('z', [0*u.mm, z_max * offset])
        #----section contour draw
        for i in range(len(contourpoints)-1):
            SomeGeometryObiect.addLine(contourpoints[i], contourpoints[i+1])
        #----section name draw
        if annotation:
            SomeGeometryObiect.addText(sectname, [0.6 * y_max, z_min])
    #---if no contourpoints defined 
    if contourpoints == []:
        SomeGeometryObiect.addText('No contourpoints defined' , [0 * u.cm, 0 * u.cm])
    #---- 
    return None
        
# Test if main
if __name__ == '__main__':
    print ('test sectiontypes')
    print (sectiongroups)
    print (FigureGroupId())
    print (FigureGroupName())
    print (FigureGroupId('HEB'))
    print (FigureGroupName('HEB'))