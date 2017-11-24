"""
project : pySAXS
description : class for radial average parameters
authors : Olivier Tache
Last changes :
08-03-2007 OT : port to pySAXS library

"""
from numpy import *

class RAP:
    """ - Radial Average Parameters -

    beam_x : x beam position
    beam_y : y beam position
    roi_xmin,  roi_ymin,   roi_xmax,  roi_ymax :    #les points a masquer
    masks_list=[] : un tableau de roi
    geom_corr_x ,  geom_corr_y   :correction geometrique
    wave_length=1.542
    detector_to_sample=1
    pixel_size=1
    q_by_pixel=-1
    exposition_time=1
    backgd_by_s=0 #par seconde
    backgd_by_pix=0 #par pixel
    comment=""
    transmission=-1
    thickness=-1
    K=1
    monitor=1
        """
    def __init__(self):
        self.beam_x=1
        self.beam_y=1
        self.roi_xmin=1
        self.roi_ymin=1
        self.roi_xmax=1
        self.roi_ymax=1
        #les points a masquer
        # un tableau de roi
        self.masks_list=[]
        #correction geometrique
        self.geom_corr_x=1
        self.geom_corr_y=1
        self.wave_length=1.542
        self.detector_to_sample=1
        self.pixel_size=1
        self.q_by_pixel=-1
        self.exposition_time=1
        self.backgd_by_s=0 #par seconde
        self.backgd_by_pix=0 #par pixel
        self.comment=""
        self.transmission=-1
        self.thickness=-1
        self.K=1
        self.monitor=1

    def __repr__(self):
        chaine=""
        t=[]
        for var,value in self.__dict__.items():
            t.append(var)
        t.sort()
        for i in range(len(t)):
            chaine+=str(t[i])+" = "+str(self.__dict__[t[i]])+"\n"
        return chaine


    def mask_add(self,polygon):
        "ajoute un masque dans la liste des masques"
        #mask=[xmin,ymin,xmax,ymax]
        self.masks_list.append(polygon)

    def mask_remove(self,i):
        "retire de la liste des masques l'element i"
        self.masks_list.pop(i)

    def mask_delete_all(self):
        "efface la liste des masques"
        self.masks_list=[]

    def Set_BeamXY(self,x,y):
        self.beam_x=x
        self.beam_y=y

    def Set_ROI(self,xmin,ymin,xmax,ymax):
        self.roi_xmin=xmin
        self.roi_ymin=ymin
        self.roi_xmax=xmax
        self.roi_ymax=ymax

    def save_printable(self,file_name):
        #enregistre dans un fichier
        f=open(file_name,mode='w')
        chaine=""
        t=[]
        for var,value in self.__dict__.items():
            t.append(var)
        t.sort()
        for i in range(len(t)):
            #chaine+=str(t[i])+" = "+str(self.__dict__[t[i]])+"\n"
            f.write(str(t[i])+" = "+str(self.__dict__[t[i]])+"\n")
        f.close()
        print file_name," saved"

    def save(self,file_name):
        import pickle
        f=open(file_name,mode='w')
        pickle.dump(self,f)

    def load(self,file_name):
        import pickle
        p=RAP()
        f=open(file_name,mode='r')
        p=pickle.load(f)
        return p

    def calculate_q_by_pix(self):
        """
        calculate q by pix in A-1 from parameters (RAP)
        """
        self.q_by_pixel=calculate_q(1,self)

def calculate_q(q,par):
    """
    calculate q in A-1 from parameters (RAP)
    """
    return ((4*pi)/par.wave_length)*sin(arctan((par.pixel_size*q)/par.detector_to_sample)/2)

def Rad_Save(p,q,n,iq,filename):
    """
    Save the averaged data in a rgr file wich can be opened by MS excel
    """

    f=open(filename,'w')
    f.write("# fichier = \t%s\n" %(filename))
    f.write("# zone regroupement : xmin=\t%s\t xmax=\t%s ymin=\t%s ymax=%s\n" % (p.roi_xmin,p.roi_xmax,p.roi_ymin,p.roi_ymax))
    f.write("# centre regroupement : x=\t%s\t y=%s \t masques :%s\n" % (p.beam_x,p.beam_y,p.masks_list))
    if p.backgd_by_s<>0:
        f.write("# taille pixel = \t%s \t Bruit fond= \t=$B$8*$G$4\t (par pixel) \t par seconde=\t%s\n" % (p.pixel_size,p.backgd_by_s))
    else:
        f.write("# taille pixel =\t %s \t Bruit fond= \t%s \t (par pixel)\n" % (p.pixel_size,p.backgd_by_pix))
    f.write("# distance ech detecteur =\t %s\n" % (p.detector_to_sample))
    f.write("# lambda=\t %s\n" % (p.wave_length))
    p.q_by_pixel=calculate_q(1,p)
    f.write("# q by pix =\t %s \t  valeur excel : \t=((4*PI())/$B$6)*SIN(ATAN($B$4/$B$5)/2)\n" % (p.q_by_pixel))
    f.write("# temps= \t%s\n" %(p.exposition_time))
    delta_omega=(p.pixel_size/p.detector_to_sample)**2
    f.write("# delta omega=\t=($B$4/$B$5)^2\t  valeur calculee :\t%s\n"% (delta_omega))
    f.write("# transmission= \t%s\n" % (p.transmission))
    f.write("# epaisseur= \t %s\n" % (p.thickness))
    f.write("# moniteur= \t %s \n" % (p.monitor))
    flux=(p.monitor/p.transmission)*p.K
    f.write("# K = \t %s \t ->Flux \t=($B$12/$B$10)*$B$13 \t ph/s\t  valeur calculee :\t%s\n" %(p.K,flux))
    f.write("# qraw\t q \tq calc \t nombre de points \t I raw \t I (cm-1)\t I (cm-1)Excel\n")
    q=calculate_q(q,p)
    ligne = -1
    for i in range(len(q)):
        if n[i] > 0:
            ligne = ligne + 1
            icm=(iq[i]-p.backgd_by_pix)/(delta_omega*p.exposition_time*p.transmission*p.thickness*flux)
            f.write("%s\t%s\t=A%s*$D$7 \t %s \t %s \t %s \t=(E%s-$D$4)/$B$9/$B$8/$B$10/$B$11/$D$13\n"% (i,q[i],ligne+15,n[i],iq[i],icm,ligne + 15))
    f.close()

def Rad_Read(filename):
    """
    Open the averaged data from a rgr file
    return qraw,q,iraw,i,n
    """
    f=open(filename,'r')
    lignes=f.readlines() #lecture de tout le fichier en une fois
    f.close
    qraw=[]
    q=[]
    iraw=[]
    i=[]
    n=[]
    for j in range(len(lignes)):
        if lignes[j][0]<>'#':
            datas=lignes[j].split('\t')
            qraw.append(int(datas[0]))
            q.append(float(datas[1]))
            n.append(float(datas[3]))
            iraw.append(float(datas[4]))
            i.append(float(datas[5]))
    #print qraw,q,iraw,i,n
    return qraw,q,n,iraw,i
