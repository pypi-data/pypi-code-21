"""
project : pySAXS
description : functions for opening detectors data file
authors : Olivier Tache
Last changes :
    08-03-2007 OT : port to pySAXS library
    lsqkjdqlskdjlqksd

"""
from numpy import *
from pySAXS.LS import rap
from pySAXS.tools.filetools import *


# FICHIERS D'IMAGE DETECTEUR-------------------------------------------------------------------#
def OpenFileMP(fname,progressbar=None):
    """
    open gas detector MP file
    FASTCOM format
    """
    begin=clock()
    print "Open MPA File : "+fname
    f=open(fname,"rb")
    #Trouve la taille de l'entete
    #recherche le 2eme octet 26
    tailleHeader=0
    n_octet_temps=0
    octet_date_debut=0
    octet_date_fin=0
    octet_temps_debut=0
    octet_temps_fin=0
    trouve=0
    octet=0
    while trouve<2:
        #lecture
        tailleHeader=tailleHeader+1
        f.seek(tailleHeader)
        octet=f.read(1)
        #print str(tailleHeader)+" : "+str(octet)+ " -> "+str(ord(octet))+ " -> "+str(hex(ord(octet)))
        if ord(octet)==10:
            if n_octet_temps==3:
                octet_date_debut=tailleHeader
            if n_octet_temps==4:
                octet_date_fin=tailleHeader
                f.seek(octet_date_debut+1)
                temps=f.read(octet_date_fin-octet_date_debut-2)
                print "DATE = "+str(temps)
            if n_octet_temps==10:
                octet_temps_debut=tailleHeader
            if n_octet_temps==11:
                octet_temps_fin=tailleHeader
                f.seek(octet_temps_debut+1)
                temps=f.read(octet_temps_fin-octet_temps_debut-2)
                print "TEMPS = "+str(temps)
            n_octet_temps=n_octet_temps+1
        if ord(octet)==26:
            trouve=trouve+1

    #print "Taille Header = "+str(tailleHeader)
    # fin lecture entete
    #f.close()
    #utilisation d'un tableau
    image=zeros([512,512])
    Image_Size=range(0,512)
    Image_test=range(0,512)
    max=0
    Taille_Ligne=512
    Char_TypeLong='L'
    Taille_TypeLong=4
    Header=tailleHeader+1
    #for y in Image_Size:
    if progressbar<>None:
        progressbar.initialize(512)
    for x in Image_Size:
        if progressbar<>None:
            progressbar.progress(x)
        f.seek(Header+x*Taille_TypeLong*Taille_Ligne)
        ligne_hexa=f.read(Taille_TypeLong*Taille_Ligne)
        ligne=unpack(Char_TypeLong*Taille_Ligne,ligne_hexa)
        ligne_tab=asarray(ligne)
        image[x]=ligne_tab
    if progressbar<>None:
        progressbar.progress(512)
    #image=asarray(image)
    f.close
    print "readed in %s s" % (clock()-begin)
    return image
    #------------------ FIN -------------------

def OpenFileMPA3_DAT(fname,progressbar=None):
    """
    open gas detector MP3 file
    Binary datas
    FASTCOM format
    """
    begin=clock()
    print "Open MPA-3 DAT binary File : "+fname
    f=open(fname,"rb")
    #Trouve la taille de l'entete
    #la taille de l'image doit etre 512x512

     #utilisation d'un tableau
    image=zeros([512,512])
    Image_Size=range(0,512)
    Image_test=range(0,512)
    max=0
    Taille_Ligne=512
    Char_TypeLong='L'
    Taille_TypeLong=4
    Header=0
    #for y in Image_Size:
    if progressbar<>None:
        progressbar.initialize(512)
    for x in Image_Size:
        if progressbar<>None:
            progressbar.progress(x)
        f.seek(Header+x*Taille_TypeLong*Taille_Ligne)
        ligne_hexa=f.read(Taille_TypeLong*Taille_Ligne)
        ligne=unpack(Char_TypeLong*Taille_Ligne,ligne_hexa)
        ligne_tab=asarray(ligne)
        image[x]=ligne_tab
    if progressbar<>None:
        progressbar.progress(512)
    #image=asarray(image)
    f.close
    print "readed in %s s" % (clock()-begin)
    return image
    #------------------ FIN -------------------



def OpenFileMPA3(fname,progressbar=None):
    """
    open gas detector MP3 file
    ascii files
    FASTCOM format
    """
    begin=clock()
    print "Open MPA-3 File : "+fname
    f=open(fname,"r")
    #Trouve la taille de l'entete
    #recherche le 2eme octet 26
    tailleHeader=0
    n_octet_temps=0
    octet_date_debut=0
    octet_date_fin=0
    octet_temps_debut=0
    octet_temps_fin=0
    trouve=0
    octet=0
    while trouve<2:
        #lecture
        tailleHeader=tailleHeader+1
        ligne=f.readline()
        #print ligne
        #print str(tailleHeader)+" : "+str(octet)+ " -> "+str(ord(octet))+ " -> "+str(hex(ord(octet)))
        #if ligne.find("ltpreset")<>-1:
        #    print ligne
        if ligne.find("[CDAT0")<>-1:
            print ligne
            trouve=2
    #print "Taille Header = "+str(tailleHeader)
    # fin lecture entete
    #f.close()
    #utilisation d'un tableau
    image=zeros([512,512])
    Image_Size=range(0,512)
    #Image_test=range(0,512)
    #max=0
    #Taille_Ligne=512
    #Char_TypeLong='L'
    #Taille_TypeLong=4
    #Header=tailleHeader+1
    #
    if progressbar<>None:
        progressbar.initialize(512)
    for x in Image_Size:
        if progressbar<>None:
            progressbar.progress(x)
        for y in Image_Size:
            pixel=f.readline()
            image[x,y]=int(pixel)
        #f.seek(Header+x*Taille_TypeLong*Taille_Ligne)
        #ligne_hexa=f.read(Taille_TypeLong*Taille_Ligne)
        #ligne=unpack(Char_TypeLong*Taille_Ligne,ligne_hexa)
    #    ligne_tab=asarray(ligne)
    #    image[x]=ligne_tab
    #if progressbar<>None:
    #    progressbar.progress(512)
    #image=asarray(image)
    f.close
    print "readed in %s s" % (clock()-begin)
    return image
    #------------------ FIN -------------------

def OpenFileSPE(fname,progressbar=None):
    """
    open SPE Winview data file
    Ropper Scientific
    """
    begin=clock()
    print "Open SPE File : "+fname
    f=open(fname,"rb")
    # HEADER -> INFOS SUR LES TAILLES
    # x_dim
    f.seek(42)
    temp=f.read(2)
    temp=unpack('h',temp)
    x_dim=temp[0]
    print "taille x :",x_dim
    # y_dim
    f.seek(656)
    temp=f.read(2)
    temp=unpack('h',temp)
    y_dim=temp[0]
    print "taille y :",y_dim
    # datatype
    f.seek(108)
    temp=f.read(2)
    temp=unpack('h',temp)
    Datatype=temp[0]
    #0 =   FLOATING POINT
    #1 =   LONG INTEGER
    #2 =   INTEGER
    #3 =   UNSIGNED INTEGER
    if Datatype==0:
        # float
        Char_Datatype="f"
        Taille_Datatype=4
    elif Datatype==1:
        # long
        Char_Datatype="L"
        Taille_Datatype=4
    elif Datatype==2:
        # integer
        Char_Datatype="h"
        Taille_Datatype=2
    elif Datatype==3:
        # unsigned int
        Char_Datatype="H"
        Taille_Datatype=2
    else:
        print "Data type error !"
        return
    print "DataType=",Datatype
    #print "Number of frames : ",ReadAndPrint(f,'l',1446)
    #print "Header version :",ReadAndPrint(f,'f',1992)
    #print "Winview  :",ReadAndPrint(f,'L',2996)
    #print "Number of accum : ",ReadAndPrint(f,'l',668)
    #print "Number of of scans (Early WinX):",ReadAndPrint(f,'l',664)
    imge=array(zeros([y_dim,x_dim]),typecode=Float)
    #print "taille imge : %s x %s",%(shape(imge)[0],shape(imge)[1])
    X_Size=range(0,y_dim)
    #Taille_Ligne=512
    Header=4100
    if progressbar<>None:
        progressbar.initialize(y_dim)
    for i in X_Size:
        if progressbar<>None:
            progressbar.progress(i)
        f.seek(Header+i*Taille_Datatype*x_dim)
        ligne_hexa=f.read(Taille_Datatype*x_dim)
        ligne=unpack(Char_Datatype*x_dim,ligne_hexa)
        ligne_tab=asarray(ligne)
        #print "taille ligne_tab :",ligne_tab.getshape()
        imge[i]=asarray(ligne)
    if progressbar<>None:
        progressbar.progress=y_dim
    #image=asarray(image)
    f.close
    print "\nreaded in %s s" % (clock()-begin)
    return imge
    #------------------ FIN -------------------

def WriteFileSPE(fname,data,progressbar=None):
    """
    write SPE Winview data file
    Ropper Scientific
    """
    begin=clock()
    print "Write SPE File : "+fname
    f=open(fname,"w+b")
    # HEADER -> INFOS SUR LES TAILLES
    data=transpose(data)
    x_dim=shape(data)[1]
    y_dim=shape(data)[0]
    vide=pack('b',0) #caractere vide

    f.write(vide*42)
    f.write(pack('h',x_dim))#42 x-dim

    f.write(vide*(108-44))#pos 44  #-> pos 108
    f.write(pack('h',0))#108  0 =   FLOATING POINT

    f.write(vide*(656-110))
    f.write(pack('h',y_dim))#656  y dimension of raw data.

    f.write(vide*(664-658))
    f.write(pack('l',-1))#664  Number of scans (Early WinX)

    f.write(pack('l',0))#668  Number of Accumulations

    f.write(vide*(1446-672))
    f.write(pack('L',1))#1446 num frames

    f.write(vide*(1992-1450))
    f.write(pack('f',2.1))#1992 HEADER VERSION

    f.write(vide*(2996-1996))
    f.write(pack('L',19088743))#2996  == 0x01234567L if file created by WinX

    f.write(vide*(4100-3000))
    #The data follows the header beginning at offset 4100
    if progressbar<>None:
        progressbar.initialize(x_dim)
    for x in range(x_dim):
        if progressbar<>None:
            progressbar.progress(x)
        chaine=""
        for y in range(y_dim):
            chaine+=pack('f',data[y,x])

        #chaine=pack('f'*y_dim,data[x])
        f.write(chaine)
    f.close
    if progressbar<>None:
        progressbar.progress(x_dim)
    print "saved in %s s" % (clock()-begin)
    #------------------ FIN -------------------




def OpenFile(filename,progressbar=None):
    """
    ouvre le fichier image filename et retourne un tableau
    """
    #est-ce que le fichier existe ?
    print filename
    if not(FileReadOK(filename)):
        #le fichier n'existe pas ou pas lisible
        print "File not found"
        return
    else:
        #quelle est l'extension ?
        ext=extension(filename)
        if ext=="dat":
            return OpenFileMPA3_DAT(filename,progressbar)
        elif ext=="spe":
            return OpenFileSPE(filename,progressbar)
        elif ext=="gel":
            return OpenFileGEL(filename,progressbar)
        elif ext=="mpa":
            return OpenFileMPA3(filename,progressbar)
        else:
            print "not yet implemented"
            return



def OpenFileGEL(fname,progressbar=None):
    """
    open GEL ImageQuant data file
    Molecular Dynamics
    """
    class TifTag:
        def __init__(self):
            self.id=0#integer
            self.type=0#integer
            self.count=0# As Long
            self.offset=0# As Long

        def ReadEntry(self,f):
            #temp=f.read(calcsize,'i')
            self.id=unpack('h',f.read(calcsize('h')))[0]#integer
            self.type=unpack('h',f.read(calcsize('h')))[0]#integer
            self.count=unpack('i',f.read(calcsize('i')))[0]#integer
            self.offset=unpack('i',f.read(calcsize('i')))[0]#integer

    GelFrac=1./21025. #4.75624256837E-05 '(1/21025)
    #print "GelFrac %s"%(GelFrac)
    begin=clock()
    print "Open GEL File : "+fname
    f=open(fname,"rb")
    endian=unpack('H',f.read(calcsize('H')))[0]#integer
    #print endian
    if endian == 18761:
        codage = 'LITTLE'
    elif endian == 19789:
        codage = 'BIG'
    else:
        print "Erreur, sans doute pas TIFF "
         #sortie
    #identifiant TIFF*/
    temp=unpack('h',f.read(calcsize('h')))[0]#short   'fread(&temp,sizeof(short),(size_t)1,gel);
    #print "identifiant tiff :",temp
    #/*----------- position de l'entete*/
    #Get #f, , offset       'fread(&offset,sizeof(long),(size_t)1,gel);
    offset=unpack('L',f.read(calcsize('L')))[0]
    #print "offset=",offset
    #'/*on se place au debut de l'entete*/
    f.seek(offset)#    'Seek #f,  'fseek(gel,offset,SEEK_SET);
    NBentry=unpack('H',f.read(calcsize('H')))[0]#short NBentry 'fread(&nbentry,sizeof(short),1,gel);
    #print "nombre d'entree : " ,NBentry
    for i in range(NBentry):
        tag=TifTag()
        tag.ReadEntry(f)
        #print tag.id
        if tag.id==256:
            x_size = tag.offset
            print "largeur de l'image : ",x_size
        elif tag.id==257:
            y_size = tag.offset
            print "hauteur de l'image : " ,y_size
        elif tag.id==273:
            data_offset = tag.offset
            print "data offset : ",data_offset


    #'-----------------------------------------------
    #'fin de la lecture de l'entete
    imge=array(zeros([y_size,x_size]),typecode=Float)
    f.seek(data_offset)
    if progressbar<>None:
        progressbar.initialize(y_size)
    for i in range(y_size):
        if progressbar<>None:
            progressbar.progress(i)
        #f.seek(Header+i*Taille_Datatype*x_dim)
        #les donnees sont sur 2 octets
        type="h" #short ?
        ligne_hexa=f.read(calcsize(type)*x_size)
        ligne=unpack(type*x_size,ligne_hexa)
        ligne_tab=asarray(ligne)
        imge[i]=(ligne_tab**2)*GelFrac
    if progressbar<>None:
        progressbar.progress(y_size)
    #imge*=
    #imge=(imge**2)*GelFrac
    #imge*=GelFrac
    #imge=transpose(imge)
    print "\nreaded in %s s" % (clock()-begin)
    return imge #data(X, y) = (data(X, y) ^ 2) * GelFrac
#--------------fin


def ConvertToSpe(filenameIn,filenameOut,progressbar=None):
    """
    convert a data file into SPE file
    """
    ext=extension(filenameIn)
    if (ext=="dat") or (ext=="mpa"):
        img=OpenFile(filenameIn,progressbar)
        WriteFileSPE(filenameOut,img,progressbar)
    elif ext=="gel":
        img=OpenFile(filenameIn,progressbar)
        img=transpose(img) #transpose !
        WriteFileSPE(filenameOut,img,progressbar)
    else:
        print "not yet implemented"

def OpenFileTIF(fname,progressbar=None):
    """
    open tiff data file
    """
    class TifTag:
        def __init__(self):
            self.id=0#integer
            self.type=0#integer
            self.count=0# As Long
            self.offset=0# As Long

        def ReadEntry(self,f):
            #temp=f.read(calcsize,'i')
            self.id=unpack('h',f.read(calcsize('h')))[0]#integer
            self.type=unpack('h',f.read(calcsize('h')))[0]#integer
            self.count=unpack('i',f.read(calcsize('i')))[0]#integer
            self.offset=unpack('i',f.read(calcsize('i')))[0]#integer

    GelFrac=1./21025. #4.75624256837E-05 '(1/21025)
    #print "GelFrac %s"%(GelFrac)
    begin=clock()
    print "Open GEL File : "+fname
    f=open(fname,"rb")
    endian=unpack('H',f.read(calcsize('H')))[0]#integer
    #print endian
    if endian == 18761:
        codage = 'LITTLE'
    elif endian == 19789:
        codage = 'BIG'
    else:
        print "Erreur, sans doute pas TIFF "
         #sortie
    #identifiant TIFF*/
    temp=unpack('h',f.read(calcsize('h')))[0]#short   'fread(&temp,sizeof(short),(size_t)1,gel);
    #print "identifiant tiff :",temp
    #/*----------- position de l'entete*/
    #Get #f, , offset       'fread(&offset,sizeof(long),(size_t)1,gel);
    offset=unpack('L',f.read(calcsize('L')))[0]
    #print "offset=",offset
    #'/*on se place au debut de l'entete*/
    f.seek(offset)#    'Seek #f,  'fseek(gel,offset,SEEK_SET);
    NBentry=unpack('H',f.read(calcsize('H')))[0]#short NBentry 'fread(&nbentry,sizeof(short),1,gel);
    #print "nombre d'entree : " ,NBentry
    for i in range(NBentry):
        tag=TifTag()
        tag.ReadEntry(f)
        #print tag.id
        if tag.id==256:
            x_size = tag.offset
            print "largeur de l'image : ",x_size
        elif tag.id==257:
            y_size = tag.offset
            print "hauteur de l'image : " ,y_size
        elif tag.id==273:
            data_offset = tag.offset
            print "data offset : ",data_offset
        elif tag.id==258:
            bbp=tag.offset
            print "bit par pixel : ",bbp
        elif tag.id==259:
            if tag.offset!=1:
                print "erreur : image comprime\n"


    #'-----------------------------------------------
    #'fin de la lecture de l'entete
    imge=array(zeros([y_size,x_size]),typecode=Float)
    f.seek(data_offset)
    if progressbar<>None:
        progressbar.initialize(y_size)
    for i in range(y_size):
        if progressbar<>None:
            progressbar.progress(i)
        #f.seek(Header+i*Taille_Datatype*x_dim)
        #les donnees sont sur 2 octets
        type="s" #short ?
        #ligne_hexa=f.read(calcsize(type)*x_size)
        ligne_hexa=f.read(bbp*x_size)
        print "ligne hexa : "+str(len(ligne_hexa))
        print "longueur :" +str(len(type*len(ligne_hexa)))
        ligne=unpack(s,ligne_hexa[0])
        ligne_tab=asarray(ligne)
        imge[i]=ligne_tab
    if progressbar<>None:
        progressbar.progress(y_size)
    #imge*=
    #imge=(imge**2)*GelFrac
    #imge*=GelFrac
    #imge=transpose(imge)
    print "\nreaded in %s s" % (clock()-begin)
    return imge #data(X, y) = (data(X, y) ^ 2) * GelFrac
#--------------fin



def importFit2D(filename=""):
    """
    import Fit2D Chi file
    after radial averaging
    create a rgr file for excel (ascii format)
    """
    p=rap.RAP()
    p.K=151000
    p.detector_to_sample=120.25
    p.pixel_size=0.005
    if filename=="" :
        filename=raw_input("Fit2d filename ?")
    data=importArray(filename,5,'  ')
    n=ones((len(data[0])))
    filenameoutput=filename+".rgr"
    rap.Rad_Save(p,data[0],n,data[1],filenameoutput)
#the end

