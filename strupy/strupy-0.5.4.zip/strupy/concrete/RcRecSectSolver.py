'''
--------------------------------------------------------------------------
Copyright (C) 2015 Lukasz Laba <lukaszlab@o2.pl>

File version 0.6 date 2016-08-30

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
- resist functions optimized
File version 0.3 changes:
- resist_forcetomoment functions optimized
File version 0.4 changes:
- in reinforce() method fas() arguments corected
File version 0.5 changes:
- fas_fastmode used to speed improve
File version 0.6 changes:
- fas() sect.rysAp, sect.rysAn arguments order corected
'''

import strupy.units as u

from RcRecSect import RcRecSect
from SectLoad import SectLoad

import math

class RcRecSectSolver():

    import fas_fastmode as fas

    def __init__(self):
        print "RcRecSecSolver"
     
    def paraminfo(self):
        self.fas.paraminfo()

    def reinforce(self, sect, load):
        sect.An=0*u.m2
        sect.Ap=0*u.m2
        sect.comment=''
        casecalculated=[]
        caseAn=None
        caseAp=None
        for i in xrange(0, len(load.caseactiv)):
            if load.caseactiv[i]:
                tmp=self.fas.calc(load.Nsd[i], load.Msd[i], sect.h, sect.b, sect.ap, sect.an, sect.fip, sect.fin, sect.rysAp, sect.rysAn, sect.wlimp, sect.wlimn, sect.fcd, sect.fctm, sect.fyd)
                if sect.An<tmp['An']:
                    sect.An=tmp['An']
                    caseAn=i
                if sect.Ap<tmp['Ap']:
                    sect.Ap=tmp['Ap']
                    caseAp=i
                casecalculated.append(i)
        sect.comment+='case calculated - '+ str(casecalculated)+' case for Ap -'+ str(caseAp)+' case for An -'+ str(caseAn)
        return None

    def resist(self, sect, directionN=-1*u.kN, directionM=0*u.kNm, startN=0*u.kN, startM=500*u.kNm):
        directionN = (directionN/u.kN).asNumber()
        directionM = (directionM/u.kNm).asNumber()
        directionMN = pow(directionN**2 + directionM**2, 0.5)
        def Nd(MN):
            return MN / directionMN * directionN *u.kN + startN
        def Md(MN):
            return MN / directionMN * directionM *u.kNm + startM
        precision=0.02
        MNmagnitude= 600
        MNdelta=MNmagnitude
        MNmin = 1
        Apreq=0*u.m2
        Anreq=0*u.m2
        alpha=1.0
        while (abs(MNdelta / MNmagnitude) > precision) and (abs(MNmagnitude) > MNmin or abs(MNdelta) > MNmin) :
            tmp=self.fas.calc(Nd(MNmagnitude), Md(MNmagnitude), sect.h, sect.b, sect.ap, sect.an, sect.fip, sect.fin, sect.rysAp, sect.rysAn, sect.wlimp, sect.wlimn, sect.fcd, sect.fctm, sect.fyd)
            Apreq=tmp['Ap']
            Anreq=tmp['An']
            if Apreq<=sect.Ap and Anreq<=sect.An:
                nextalpha=1.0
            else:
                nextalpha=-1.0
            if MNmagnitude<0:
                MNmagnitude=0
                nextalpha=-alpha
            if nextalpha*alpha==-1.0 :
                MNdelta = 0.6*MNdelta
            else:
                 MNdelta = 1*MNdelta
            alpha=nextalpha
            MNmagnitude=MNmagnitude+MNdelta*alpha
        if MNmagnitude < MNmin:
            MNmagnitude = 0
        return [Nd(MNmagnitude), Md(MNmagnitude)]

    def resist_moment(self, sect):
        Mrdmax = self.resist(sect, 0*u.kN, 1*u.kNm, 0*u.kN, 0*u.kNm)[1]
        Mrdmin = self.resist(sect, 0*u.kN, -1*u.kNm, 0*u.kN, 0*u.kNm)[1]
        sect.resist_moment={'Mrdmax':Mrdmax, 'Mrdmin':Mrdmin}
        return None

    def resist_force(self, sect):  
        Nrdmax = self.resist(sect, 1*u.kN, 0*u.kNm, 0*u.kN, 0*u.kNm)[0]
        Nrdmin = self.resist(sect, -1*u.kN, 0*u.kNm, 0*u.kN, 0*u.kNm)[0]
        sect.resist_force={'Nrdmax':Nrdmax, 'Nrdmin':Nrdmin}
        return None

    def resist_forcetomoment(self, sect, dividenumber=10, progress=None):
        Nrdi=[]
        Mrdi=[]
        Nrdi_withcrackcontrol=[]
        Mrdi_withcrackcontrol=[]
        #----
        Nmax = self.resist(sect, 1*u.kN, 0*u.kNm, 0*u.kN, 0*u.kNm)[0]
        Nmin = self.resist(sect, -1*u.kN, 0*u.kNm, 0*u.kN, 0*u.kNm)[0]
        Mmax = self.resist(sect, 0*u.kN, 1*u.kNm, (Nmax + Nmin)/2, 0*u.kNm)[1]
        Mmin = self.resist(sect, 0*u.kN, -1*u.kNm, (Nmax + Nmin)/2, 0*u.kNm)[1]
        #----
        rangeN = abs(Nmax-Nmin)
        rangeM = abs(Mmax-Mmin)
        kappa = (rangeN / u.kN) / (rangeM / u.kNm)
        #----
        start_N = (Nmax + Nmin) / 2
        start_M = 0*u.kNm
        #----
        rysAp = sect.rysAp
        rysAn = sect.rysAn
        loop = 0
        for i in xrange (0, dividenumber+1):
            beta=(2.0*math.pi)*i/dividenumber
            dNsdi=math.cos(beta)*10*u.kN*kappa
            dMsdi=math.sin(beta)*10*u.kNm
            sect.rysAp = 0
            sect.rysAn = 0
            tmp = self.resist(sect, dNsdi, dMsdi, start_N, start_M)
            Nrdi.append(tmp[0])
            Mrdi.append(tmp[1])
            sect.rysAp = rysAp
            sect.rysAn = rysAn
            if sect.rysAn or sect.rysAp:
                tmp = self.resist(sect, dNsdi, dMsdi, start_N, start_M)
                Nrdi_withcrackcontrol.append(tmp[0])
                Mrdi_withcrackcontrol.append(tmp[1])
            loop += 1
            if progress:
                progress.setValue(100 * loop / (dividenumber+1))
        sect.resist_forcetomoment={'Nrdi':Nrdi, 'Mrdi':Mrdi}
        sect.resist_forcetomoment_withcrackcontrol={'Nrdi':Nrdi_withcrackcontrol, 'Mrdi':Mrdi_withcrackcontrol}
        if progress:
            progress.setValue(0)
        return None

    def As_as_forcefunction(self, sect, fromNsd=0*u.N, toNsd=10000000*u.N, dividenumber=30, acompMsd=0*u.Nm):
        Nsdrange=[None]*dividenumber
        for i in xrange(0, len(Nsdrange)):
            Nsdrange[i]=fromNsd+(1.0*toNsd-fromNsd)/(len(Nsdrange)-1)*i
        Ap=[None]*dividenumber
        An=[None]*dividenumber
        for i in xrange(0, len(Nsdrange)):
            tmp=self.fas.calc(Nsdrange[i], acompMsd, sect.h, sect.b, sect.ap, sect.an, sect.fip, sect.fin, sect.rysAp, sect.rysAn, sect.wlimp, sect.wlimn, sect.fcd, sect.fctm, sect.fyd)
            An[i]=tmp['An']
            Ap[i]=tmp['Ap']
        sect.As_as_forcefunction={'An':An, 'Ap':Ap, 'Nsdrange':Nsdrange, 'failurecode':[None]*dividenumber, 'acompMsd':acompMsd}
        return None
    
    def As_as_momentfunction(self, sect, fromMsd=-2000000*u.Nm, toMsd=2000000*u.Nm, dividenumber=100, acompNsd=0*u.N):
        Msdrange=[None]*dividenumber
        for i in xrange(0, len(Msdrange)):
            Msdrange[i]=fromMsd+(1.0*toMsd-fromMsd)/(len(Msdrange)-1)*i     
        Ap=[None]*dividenumber
        An=[None]*dividenumber
        for i in xrange(0, len(Msdrange)):
            tmp=self.fas.calc(acompNsd, Msdrange[i], sect.h, sect.b, sect.ap, sect.an, sect.fip, sect.fin, sect.rysAp, sect.rysAn, sect.wlimp, sect.wlimn, sect.fcd, sect.fctm, sect.fyd)
            Ap[i]=tmp['Ap']
            An[i]=tmp['An']
        sect.As_as_momentfunction={'An':An, 'Ap':Ap, 'Msdrange':Msdrange, 'failurecode':[None]*dividenumber, 'acompNsd':acompNsd}
        return None
    
    def As_as_forcetomomentfunction(self, sect, fromNsd=-1000000*u.N, toNsd=9000000*u.N, dividenumberNsd=10, fromMsd=-1000000*u.Nm, toMsd=1000000*u.Nm, dividenumberMsd=10, progress=None):
        deltaNsd=(1.0*toNsd-fromNsd)/dividenumberMsd
        deltaMsd=(1.0*toMsd-fromMsd)/dividenumberNsd  
        Nsd=[[0]*(dividenumberMsd+1)]
        Msd=[[0]*(dividenumberMsd+1)]
        Ap=[[0]*(dividenumberMsd+1)]
        An=[[0]*(dividenumberMsd+1)]   
        for i in xrange(0, dividenumberNsd):
            Nsd.append([0]*(dividenumberMsd+1))
            Msd.append([0]*(dividenumberMsd+1))
            Ap.append([0]*(dividenumberMsd+1))
            An.append([0]*(dividenumberMsd+1))
        for i in xrange(0, dividenumberNsd+1):
            for j in xrange(0, dividenumberMsd+1):
                Nsd[i][j]=fromNsd+(1.0*toNsd-fromNsd)/dividenumberNsd*i
                Msd[i][j]=fromMsd+(1.0*toMsd-fromMsd)/dividenumberMsd*j
        loop = 0
        pointnumber = (dividenumberNsd+1) * (dividenumberMsd+1)
        for i in xrange(0, dividenumberNsd+1):
            for j in xrange(0, dividenumberMsd+1):
                tmp=self.fas.calc(Nsd[i][j], Msd[i][j], sect.h, sect.b, sect.ap, sect.an, sect.fip, sect.fin, sect.rysAp, sect.rysAn, sect.wlimp, sect.wlimn, sect.fcd, sect.fctm, sect.fyd)
                Ap[i][j]=tmp['Ap']
                An[i][j]=tmp['An']
                loop += 1
                if progress:
                    progress.setValue(100 * loop / pointnumber)
        sect.As_as_forcetomomentfunction={'An':An, 'Ap':Ap, 'Nsd':Nsd, 'Msd':Msd}
        if progress:
            progress.setValue(0)
        return None
    
# Test if main
if __name__ == '__main__':
    print ('test RcRecSectSolver')
    sec=RcRecSect()
    solv=RcRecSectSolver()
    load=SectLoad()
    load.add_loadcase()
    sec.Ap=10*u.cm2
    sec.An=20*u.cm2
    print ('--------------------reinforce(self, sect, load)--------------------')
    #print sec.get_sectinfo()
    #solv.paraminfo()
    #print load.get_loadcases()
    #load.edit_loadcase(0, {"Name": 'ULS_changed', "Msd": 1200*u.Nm, "MTsd": 2*u.Nm, "Nsd": 0*u.N, "Vsd": 9*u.N})
    #load.add_loadcase({"Name": 'ULS_new', "Msd": 800*u.kNm, "MTsd": 2*u.Nm, "Nsd": 0*u.N, "Vsd": 9*u.N})
    #print load.get_loadcases()
    #print ('-----------------1-----------------------')
    #solv.reinforce(sec,load)
    #print ('-----------------2-----------------------')
    #print sec.get_sectinfo()
    #print ('-----------------solv.resist_moment(sec)-----------------------')
    #solv.resist_moment(sec)
    #print sec.resist_moment
    #print ('-----------------solv.resist_force(sec)-----------------------')
    #solv.resist_force(sec)
    #print sec.resist_force
    #print ('-----------------solv.As_as_forcefunction(sec)-----------------------')
    #solv.As_as_forcefunction(sec)
    #print sec.As_as_forcefunction
    #sec.plot_As_as_forcefunction()
    #print ('-----------------solv.As_as_momentfunction(sec)-----------------------')
    #solv.As_as_momentfunction(sec)
    #print sec.As_as_momentfunction
    #sec.plot_As_as_momentfunction()
    #print ('-----------------solv.As_as_forcetomomentfunction(sec)-----------------------')
    #sec.rysAn=1
    #sec.rysAn=1
    #solv.As_as_forcetomomentfunction(sec)
    #print sec.As_as_forcetomomentfunction['Nsd']
    #print sec.As_as_forcetomomentfunction['Msd']
    #print sec.As_as_forcetomomentfunction['Ap']
    #print sec.As_as_forcetomomentfunction['An']
    #sec.plot_As_as_forcetomomentfunction()
    #print ('-----------------resist_forcetomoment(sect, dividenumber=10))-----------------------')
    #solv.resist_forcetomoment(sec, 20)
    #print sec.resist_forcetomoment
    #print sec.Ap
    #print sec.An
    #sec.plot_resist_forcetomoment(load)