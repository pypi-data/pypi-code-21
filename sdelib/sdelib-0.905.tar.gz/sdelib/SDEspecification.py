import numpy as np
from scipy import linalg

class Error(Exception):
    pass


class SDEValueError(Error):
    """Thrown if integration arguments fail some basic sanity checks"""
    pass


class SDEspec:
    """Class of problem specification.

    Used for ease of creating problems."""
    def __init__(self, d=None, m=None, name='Unspecified', trueSol=None,
        f=None, g=None, g1=None, checkTest = False, checkTrue = False,
        expSol = None, GUI = True, trueName="Autonomous and multiplicative"):

        #Setting variables.
        self.SDEtype, self.name, self.GUI = "SDEspec", name, GUI
        self.f, self.g, self.trueSol, self.d, self.m = f, g, trueSol, d, m
        self.checkTest, self.checkTrue = checkTest, checkTrue 

        #Only add if not None so that attribute-errors get thrown if 
        #methods are called when they don't exist.
        if g1 != None:
            self.g1 = g1
        if trueSol != None:
            self.trueSol = trueSol
        if expSol != None:
            self.expSol = expSol

        #Includes trueSol.
        if checkTrue:
            #Autonomous and multiplicative is the only trueSol available.
            if trueName == "Autonomous and multiplicative":
                self.trueName = 'Autonomous and multiplicative'
                if self.d == 1:
                    def trueSol(p):
                        a1 = p.f(np.array(1),0)
                        a2 = 0
                        for k in range(p.m):
                            a2 += p.g[k](np.array(1),0)**2
                        a3 = a1-0.5*a2
                        a = np.multiply(a3,p.tFine[1:])
                        b = np.zeros(p.WFine[:,0].shape)
                        for k in range(p.m):
                            b += np.squeeze(p.g[k](1,0))*p.WFine[:,k]
                        #Needs singleton dimension for consistency with sdelib.
                        c = np.zeros((len(p.tFine),p.d,p.totSimNum))
                        for sim in range(p.totSimNum):
                            d = np.squeeze(a)+np.squeeze(b[1:,sim])
                            e = np.exp(d)*p.X0
                            e = np.insert(e,0,p.X0,axis=0)
                            c[:,0,sim] = e
                        if p.printTrue:
                            print("Printing true solution:")
                            for sim in range(p.totSimNum):
                                print("Sample path nr ",sim)
                                print(np.squeeze(c[:,0,sim]))
                        return c
                else:
                    def trueSol(p):
                        F = getF(p.f,p.d)#For dX = (FX+f(X,t))dt, calculate F-matrix
                        G = []
                        for k in range(p.m):
                            Gk = getF(p.g[k],p.d)
                            G.append(Gk)
                        A = F - 0.5*sum([Gk*Gk for Gk in G])
                        trueX = np.zeros((len(p.tFine),p.d,p.totSimNum))
                        for sim in range(p.totSimNum):
                            trueX[0,:,sim] = p.X0
                            for i in range(1,p.nFine):
                                B = np.zeros(F.shape)
                                for k in range(p.m):
                                    B += G[k]*p.WFine[i,k,sim]
                                trueX[i,:,sim] = linalg.expm(A*p.tFine[i]+B)@p.X0
                            update_progress(sim/p.totSimNum)
                        if p.printTrue:
                            print("Printing true solution.")
                            for sim in range(p.totSimNum):
                                print("Sample path nr ",sim)
                                for d in range(p.d):
                                    print("Dimension nr ",d)
                                    print(trueX[:,d,sim])
                        return trueX
                print(" ")#For line shift after update progress.
                self.trueSol = trueSol

    def save(obj):
        """Saves self to file."""
        name = QtWidgets.QFileDialog.getSaveFileName(mw,'Save File',
            'New SDE.sde','SDE-file *.sde')
        name = name[0]
        name = name.split('/')[-1]
        print("Save, name: ",name)
        with open(name,'wb') as output:
            pickle.dump(obj, output, -1)

def openSDEobject():
    """Opens an SDE object from file."""
    name = QtWidgets.QFileDialog.getOpenFileName(mw,'Open SDE File','',"SDE files (*.sde)")
    name = name[0].split('/')[-1]
    if name != '':
        print("Open, name: ",name)
    try:
        with open(name,'rb') as input:
            openedObj = pickle.load(input)
        try:
            SDEtype = openedObj.SDEtype
            print("openedObj: ",openedObj)
        except AttributeError:
            print("That's not a SDE-object.")
            return
    except FileNotFoundError:
        return
    if SDEtype == "SDEprob":
        return openedObj
    else:
        print("File not SDEprob object, return none.")
        return None

"""Used for getting a constant matrix A out of a method. For example if 
f(X,t) = AX + a(t) and X in R^3, f is called with f(e_k,0) where e_k is one of 
the 3 basis vectors for R^3 for all k to recreate F. This assumes a(0) = 0.""" 
def getF(f,d):
    F = np.zeros((d,d))
    X = np.identity(d)
    for i in range(d):
        F[:,i] = f(X[:,i],0)
    return F

"""Used for having a line in the terminal displaying progress as a percentage
without having to reprint"""
def update_progress(progress):
    print("\rProgress for true solution: [{0:50s}] {1:.1f}%".format('#' *
        int(progress * 50),progress*100), end="", flush=True)