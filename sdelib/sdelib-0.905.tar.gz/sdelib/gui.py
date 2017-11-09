#!/usr/bin/env python
"""main.py runs the GUI of sdelib, run this file to run the program.
main.py communicates with a bunch of scripts created from .ui files from
qt designer. So the customization and communcation within the GUI is all created
here. main.py then communicates with SDEspec, SDEprob, SDEint and SDEanalysis
where the actual numerics are done."""

import numpy as np#For numerics.
import logging#for print statements
import dill as pickle#for opening files
import importlib.util
#import sip#for deleting layouts

#For using qt through pyqt5.
from PyQt5 import QtCore, QtGui, QtWidgets

#For importing each GUI-window from subfolder GUI.
from GUI import newSpec, mainWin, newSpec,chooseSolvers, newReal
from GUI import probRealActions, solPlot, calcSolver, newFunc

#Importing the central classes of sdelib
import SDEspecification, SDEproblem, SDEint, SDEanalysis

def clearObjects():
    '''Sets spec, prob and states to None-state'''
    global spec, prob, states
    spec, prob = None, None #Central SDE-objects.
    states = ["None-object" for entry in states]

    updateObjectStates()

def createFolder():
    '''For creating a folder when creating a problem.'''
    global probDir
    defaultName = cnpUi.leName.text()
    directory = str(QtWidgets.QFileDialog.getExistingDirectory(None, "Select Directory"))
    if directory != None:
        probDir = directory

def testFGPrerequisites():
    '''Tests whether requirements for creating f and g are satisfied.'''
    dimDx, numWien = getDimensionsNew()
    if probDir == None:
        openMessageBox('Subfolder to store functions must be selected first')
        return False
    if dimDx == None:
        openMessageBox('Dimension of dX must contain a positive integer.')
        return False
    if numWien == None:
        openMessageBox('Number of Wiener processes must contain a positive integer')
        return False
    return True

def openFunc():
    '''Opens up chosen function if it exists in chosen folder.'''
    if not testFGPrerequisites():
        return
    func = cnpUi.cbFunction.currentText()
    fileName = probDir+"\\"+func+".py"
    try:
        with open(fileName,'r') as file:
            fileString = file.read()
        openNewFunc(fileString = fileString)
    except FileNotFoundError:
        string = func + ".py doesn't exist in "+probDir+"."
        openMessageBox(string)
        return

def openNewFunc(fileString = None):
    '''Create a new function (f or g) from default that user can edit.'''
    if not testFGPrerequisites():
        return
    func = cnpUi.cbFunction.currentText()
    if func == 'f':
        Fnew(fileString=fileString)
    elif func == 'g':
        Gnew(fileString=fileString)
    elif func == 'g1':
        G1new(fileString=fileString)
    elif func == 'True solution':
        TrueNew(fileString=fileString)
    elif func == 'Expected value of solution':
        ExpNew(fileString=fileString)
    else:
        print("Something has gone horribly wrong in OpenNewFunc")

def validateFunc():
    '''Validate current function you are working on.'''
    func = cnpUi.cbFunction.currentText()
    if func == 'f':
        validateF()
    elif func == 'g':
        validateG()
    elif func == 'g1':
        validateG1()
    elif func == 'True solution':
        validateTrueSol()
    elif func == 'Expected value of solution':
        validateExpSol()


def Fnew(fileString=None):
    '''Creates new f function from default that user can edit.'''
    fDesciption = (
"Create f(X,t) by altering the function below. f is the function from the SDE"
+"dX = f(X,t)dt + sum_k g[k](X,t)dW_k. The Validate button then checks whether "
+"f(X,t) is valid by checking the shape of the output. ")
    nfUi.tbDescription.setText(fDesciption)
    dimDx, numWien = getDimensionsNew()
    # if dimDx > 1:
    diagStr = ["1," for x in range(dimDx)]
    diagStr = ''.join(diagStr)
    diagStr = "["+diagStr[:-1]+"]"
    # elif dimDx == 1:
    #     diagStr = "1"
    # else:
    #     print("Something has gone horribly wrong.")
    #     return
    # matStr = ""
    # for i in range(dimDx):

    #     for j in range(dimDx):
    #         if i = j:
    matStr = np.identity(dimDx)
    matStr = str(matStr)
    matStr = matStr.replace("\n ",",\n\t#")
    matStr = matStr.replace("  "," ")
    matStr = matStr.replace(" ",",")
    matStr = matStr.replace("\t","    ")

    methodStr = (
"import numpy as np\n"
+"def f(X,t):\n"
+"    #Includes 2 common approaches for f below, first is uncommented,\n"
+"    #second is commented.\n"
+"    #Approach 1, f(X,t) = I@X(t). Multiply each element of X with a\n"
+"    #coefficient. No cross-terms, equivalent to multiplying X with\n"
+"    #diagonal matrix F.\n"
+"    return 2*X#Simple multiplicative, works for many dimensions\n\n"
+"    #Approach 2, f(X,t) = F@X(t), specify full matrix that you multiply\n"
+"    #with:\n"
+"    #F = np.array(("+matStr+"))\n"
+"    #out np.reshape(np.dot(F,X),("+str(dimDx)+",))#reshape (3,1)->(3,)\n\n"
+"    #Approach 3, specify function performed on each element of X:\n"
+"    #out =(np.array( [np.dot(i,X[i]) for i in range("+str(dimDx)+")] ))\n\n"
+"    return np.reshape(out,("+str(dimDx)+",))#np.reshape makes f slower,\n"
+"    #but guarantees shape consistent with sdelib. If you require a faster f,\n"
+'    #create a function that returns shape (d,), but "premature\n'
+'    #optimization is the root of all evil" as Guido says.')
    if fileString != None:
        methodStr = fileString
    nfUi.funcEdit.setText(methodStr)
    nf.show()

def validateF():
    '''Tests whether output of f is consistent with dimDx.'''
    global f, fExists
    dimDx, numWien = getDimensionsNew()
    tmpPath = probDir + '/tmp.py'
    with open(tmpPath,'w+') as fileWriter:
        fileWriter.write(nfUi.funcEdit.toPlainText())
    spec = importlib.util.spec_from_file_location("tmp", tmpPath)
    fMod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(fMod)
    X = np.ones(dimDx)
    fOut = fMod.f(X,0)
    fShape = fOut.shape
    string = ("Input X.shape is " + str(X.shape) +
        ", while output f(X,0).shape is " + str(fShape) + ". X = " + str(X) +
        " and f(X,0) is " + str(fOut) + ".")
    if X.shape != fShape:
        openMessageBox(string)
        return
    else:
        print("f-function accepted.")
        fExists = True
        path = probDir + '/f.py'
        with open(path,'w+') as fileWriter:
            fileWriter.write(nfUi.funcEdit.toPlainText())
        spec = importlib.util.spec_from_file_location("f", path)
        fMod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(fMod)
        f = fMod.f
        nf.close()

def Gnew(fileString=None):
    '''Create new g function from default that user can edit.'''
    gDesciption = (
"Create g(X,t) by altering the function below. g is the function from the SDE"
+"dX = f(X,t)dt + sum_k g[k](X,t)dW_k. The Validate button then checks whether "
+"g(X,t) is valid by checking the shape of the output. ")
    nfUi.tbDescription.setText(gDesciption)
    dimDx, numWien = getDimensionsNew()
    # if dimDx > 1:
    diagStr = ["1," for x in range(dimDx)]
    diagStr = ''.join(diagStr)
    diagStr = "["+diagStr[:-1]+"]"
    zeroStr = ["0," for x in range(dimDx)]
    zeroStr = ''.join(zeroStr)
    zeroStr = "["+zeroStr[:-1]+"]"
    # elif dimDx == 1:
    #     diagStr = "1"
    # else:
    #     print("Something has gone horribly wrong.")
    #     return

    scaleDivide = (numWien+1)*numWien/2
    methodStr = (
"#g is a list of functions, so that g_k(X,t) is g[k](X,t).\n"
+"#For dX(t) = f(X,t)dt + sum_k G_k(X,t)dW_k(t), here you write G_k(X,t).\n"
+"import numpy as np\n"
+"g = []\n"
+"#3 approaches are included in all g[k], comment/uncomment to choose.\n"
+"#Approach 1, G(X,t) = G, additive noise, simplest case:\n"
+"#Approach 2, G_k = I_k, different additive noise for each dimension:\n"
+"#Approach 3, G(X,t) = IX, multiplicative noise. G is identity matrix and is\n"
+"#multiplied by X.\n")
    for k in range(numWien):
        #if dimDx > 1:
        if k < dimDx:
            tmp = (
"def g"+str(k)+"(X,t):\n"
+"    #return np.array("+diagStr+")\n"
+"    #return np.identity("+str(dimDx)+")["+str(k)+"]\n"
+"    return X#Simple multiplicative, works for many dimensions\n"
+"    #return np.reshape(out, ("+str(dimDx)+",))#reshape makes g slower,\n"
+"    #but guarantees correct shape. Optimize if you need to.\n"
+"g.append(g"+str(k)+")\n")
        else:
            tmp = (
"def g"+str(k)+"(X,t):\n"
+"    #out = np.array("+diagStr+")\n"
+"    #out = np.array("+zeroStr+")\n"
+"    out = np.dot(np.identity("+str(dimDx)+"),X)\n"
+"    return np.reshape(out, ("+str(dimDx)+",))#reshape makes g slower,\n"
+"    #but guarantees correct shape. Optimize if you need to.\n"
+"g.append(g"+str(k)+")\n")
        methodStr = methodStr + tmp
        # elif dimDx == 1:
        #     tmp = (
        #         "def g"+str(k)+"(X,t):\n"
        #         +"    #return np.array("+diagStr+")\n"
        #         +"    return np.array("+str(dimDx)+")\n"
        #         +"    #return(np.squeeze(np.identity("+str(dimDx)+")*X))\n"
        #         +"g.append(g"+str(k)+")\n")
        #     methodStr = methodStr + tmp
    if fileString != None:
        methodStr = fileString
    nfUi.funcEdit.setText(methodStr)
    nf.show()

def validateG():
    '''Test whether output of g is consistent with dimDx and numOfWien. '''
    global g, gExists
    dimDx, numWien = getDimensionsNew()
    tmpPath = probDir + '/tmp.py'
    with open(tmpPath,'w+') as fileWriter2:
        fileWriter2.write(nfUi.funcEdit.toPlainText())
    spec = importlib.util.spec_from_file_location("g", tmpPath)
    tmpMod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tmpMod)
    X = np.ones(dimDx)
    for k in range(numWien):
        gOut = tmpMod.g[k](X,0)
        gShape = gOut.shape
        string = ("Input X.shape is " + str(X.shape) + ", while output g[" 
            + str(k) + "](X,0).shape is " + str(gShape) + ". X = " + str(X)
            + " and g(X,0) is " + str(gOut) + ".")
        if X.shape != gShape:
            openMessageBox(string)
            return
    print("g function accepted.")
    path = probDir + '/g.py'
    with open(path,'w+') as fileWriter:
        fileWriter.write(nfUi.funcEdit.toPlainText())
    spec = importlib.util.spec_from_file_location("g", path)
    gMod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gMod)
    gExists = True
    g = gMod.g
    nf.close()

def G1new(fileString = None):
    '''Create new Jacobian of g function from default that user can edit. '''
    g1Desciption = (
"Create g1[i][j](X,t) by altering the function below. g1 is the derivative of g"
+"in dX = f(X,t)dt + sum_k g[k](X,t)dW_k. The Validate button then checks "
+"whether g[i][j](X,t) is valid by checking the shape of the output. ")
    nfUi.tbDescription.setText(g1Desciption)
    dimDx, numWien = getDimensionsNew()
    diagStr = ["1," for x in range(dimDx)]
    diagStr = ''.join(diagStr)
    diagStr = "["+diagStr[:-1]+"]"
    zeroStr = ["0," for x in range(dimDx)]
    zeroStr = ''.join(zeroStr)
    zeroStr = "["+zeroStr[:-1]+"]"

    scaleDivide = (numWien+1)*numWien/2
    methodStr = (
"#g1 is a list of list of functions, where g1[i][j](X,t) = dg^i/dx^j\n"
+"import numpy as np\n"
+"g1 = []\n")
    for i in range(dimDx):
        methodStr += "g"+str(i)+" = []\n"
        for j in range(dimDx):
            methodStr += (
"def g"+str(i)+str(j)+"(X,t):\n"
+"    return np.array("+diagStr+")\n"
"g"+str(i)+".append(g"+str(i)+str(j)+")\n")
        methodStr += "g1.append(g"+str(i)+")\n"
    if fileString != None:
        methodStr = fileString
    nfUi.funcEdit.setText(methodStr)
    nf.show()

def validateG1(fileString = None):
    '''Test whether output of g1 has dimensions consistent with d and m.'''
    global g1
    dimDx, numWien = getDimensionsNew()
    tmpPath = probDir + '/tmp.py'
    with open(tmpPath,'w+') as fileWriter2:
        fileWriter2.write(nfUi.funcEdit.toPlainText())
    spec = importlib.util.spec_from_file_location("tmp", tmpPath)
    tmpMod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tmpMod)
    X = np.ones(dimDx)
    for i in range(dimDx):
        for j in range(dimDx):
            g1Out = tmpMod.g1[i][j](X,0)
            g1Shape = g1Out.shape
            string = ("Input X.shape is " + str(X.shape) + ", while output g[" 
                + str(i) + "]["+str(j)+"](X,0).shape is " + str(g1Shape) +
                ". X = " + str(X) + " and g(X,0) is " + str(g1Out) + ".")
            if X.shape != g1Shape:
                openMessageBox(string)
                return
    print("g1 function accepted.")
    path = probDir + '/g1.py'
    with open(path,'w+') as fileWriter:
        fileWriter.write(nfUi.funcEdit.toPlainText())
    spec = importlib.util.spec_from_file_location("g1", path)
    g1Mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(g1Mod)
    g1 = g1Mod.g1
    nf.close()

def TrueNew(fileString = None):
    '''Create a trueSol-function, included for completeness. Does nothing.'''
    methodStr = (
"#Merely an empty shell that returns a sequence of correct length. For \n"
+"#autonomous and multiplicative checked, trueSol is included in SDEspec.\n"
+"#Included in case user wants to add a different true solution.\n"
+"def trueSol(p):\n"
+"    return np.zeros(p.d)\n")
    if fileString != None:
        methodStr = fileString
    nfUi.funcEdit.setText(methodStr)
    nf.show()

def validateTrueSol(fileString = None):
    '''Supposed to validate trueSol.Included for completeness, does nothing.'''
    global trueSol
    message = (
"No validation used for true solution since it is not a mandatory part of "
+"creating SDE objects. Correct method assumed.")
    openMessageBox(message)

    path = probDir + '/trueSol.py'
    with open(path,'w+') as fileWriter:
        fileWriter.write(nfUi.funcEdit.toPlainText())
    spec = importlib.util.spec_from_file_location("trueSol", path)
    trueSolMod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(trueSolMod)
    trueSol = trueSolMod.trueSol
    print("True solution accepted.")
    nf.close()

def ExpNew(fileString = None):
    '''Default function for expecation. Only handles scalar additive SDE now'''
    methodStr = (
"#First method below is for scalar additive noise: dX= Xdt+sum_k g_k(t)*dW_k\n"
+"#Commented out method is multiplicative noise."
+"import numpy as np\n"
+"def expSol(X0,t):\n"
+"    const = 1#Replace this to set the correct constant.\n"
+"    X = np.zeros((len(t),len(X0)))\n"
+"    X[:,0] = X0*np.exp(const*t)\n"
+"    return X")
#ExpSol takes an initial value X0 and time series t and returns a time series
#X of the values at times t. X0 is assumed to be at t=0 and t is assumed
#homogenously spaced in [0,T].
    if fileString != None:
        methodStr = fileString
    nfUi.funcEdit.setText(methodStr)
    nf.show()

def validateExpSol():
    '''There for completeness, doesn't do anything.'''
    global expSol
    message = (
"No validation used for expected solution since it is not a mandatory part of "
+"creating SDE objects. Correct method assumed.")
    openMessageBox(message)

    path = probDir + '/expSol.py'
    with open(path,'w+') as fileWriter:
        fileWriter.write(nfUi.funcEdit.toPlainText())
    spec = importlib.util.spec_from_file_location("expSol", path)
    expSolMod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(expSolMod)
    expSol = expSolMod.expSol
    print("Expected solution accepted.")
    nf.close()

def enableTrueName():
    '''For including true solution from SDEspec object. May be pointless. '''
    if cnpUi.checkTrue.checkState():
        cnpUi.cbTrue.setEnabled(True)
    else:
        cnpUi.cbTrue.setEnabled(False)

def saveObject(obj):
    """Saves an SDE object to file."""
    name = QtWidgets.QFileDialog.getSaveFileName(mw,'Save File','New SDE.sde',
        'SDE-file *.sde')
    name = name[0]
    name = name.split('/')[-1]
    print("Save, name: ",name)
    with open(name,'wb') as output:
        pickle.dump(obj, output, -1)

def fOpenObject():
    """Opens an SDE object from file and loads up global objects from that."""
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
        print("Problem realization realization object")
        fOpenProb(openedObj)
    elif SDEtype == "SDEspec":
        print("Problem specification object.")
        fOpenSpec(openedObj)
    else:
        print("Else SDEtype: ",SDEtype)


def fOpenProb(object):
    """Opens problem-object from sent object."""
    global prob 
    prob = object
    states[1]= (
        "Size of Wiener matrix (time x Wiener x simulation) = "
        + str(prob.W.shape) + ", T = " + str(prob.t[-1]) + ", n = " + str(prob.n) + ".")
    # if prob.numOfSol > 0:
    #     states[1] = (
    #     "Problem realization is solved. The solution dictonary in the problem "
    #     "realization has solutions from " + str(prob.numOfSol) + " solvers.")
    fOpenSpec(prob.spec)

def fOpenSpec(object):
    """Opens specification-object from sent object."""
    global spec 
    spec = object
    states[0] = (spec.name + ", dim = " + str(spec.d) +
        ", nr. of Wiener processes = " + str(spec.m)+".")
    updateObjectStates()

def getDimensionsNew():
    dimDx, numWien = cnpUi.leDimdX.text(), cnpUi.leNumWien.text()
    if dimDx.isdigit():
        dimDx = int(dimDx)
    else:
        dimDx = None
    if numWien.isdigit():
        numWien = int(numWien)
    else:
        numWien = None
    return dimDx,numWien

def openMessageBox(message,title="Message",icon="Information",query = False):
    '''Displays string message in QMessageBox. '''
    box = QtWidgets.QMessageBox()
    if icon == "Information":
        box.setIcon(QtWidgets.QMessageBox.Information)
    elif icon == "Question":
        box.setIcon(QtWidgets.QMessageBox.Question)
    box.setWindowTitle(title)
    if query == True:
        box.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
    box.setText(message)
    box.exec_()

def openProbSpecActions():
    """Opens problem realization window."""
    global spec, states, nFineOn
    if not (fExists and gExists):
        openMessageBox(("f and g must be created first. fExists = "
            +str(fExists)+", gExists = " + str(gExists) + "."))
        return
    else:
        cnp.close()

    dimdX, numWien = getDimensionsNew()
    checkTrue = cnpUi.checkTrue.checkState()
    prUi.leNFine.setEnabled(True)
    checkTest = cnpUi.checkTest.checkState()
    trueName = cnpUi.cbTrue.currentText()
    if cnpUi.leName.text() != '':
        example = cnpUi.leName.text()
    else:
        example = None
    spec = SDEspecification.SDEspec(name=example,f=f, g=g, g1=g1,
        d=dimdX, m=numWien,checkTrue = checkTrue, checkTest = checkTest,
        trueName = trueName,trueSol=trueSol,expSol=expSol)
    states[0] = ("Name: "+example+", dim = "+str(dimdX)+", nr. of Wiener "
        +"processes = " + str(numWien))
    states[1] = "None-object"
    print("Problem specification created: ",states[0])
    updateObjectStates()
    pr.show()

def defaultValues():
    '''Sets default values in New Problem realization window.'''
    if prUi.cbDefault.checkState():
        prUi.leNumOfSim.setText("1")
        prUi.leEndTime.setText("1")
        prUi.leNumOfSamp.setText("1024")
        prUi.leNFine.setText("4096")
        X0String = ""
        for i in range(0,spec.d):
            X0String += "1,"
        prUi.leX0.setText(X0String)


def openProbRealActions():
    """Opens window for generating problem realization."""
    global prob, states
    numOfSim, T = prUi.leNumOfSim.text(), prUi.leEndTime.text(),
    n, X0 = prUi.leNumOfSamp.text(), prUi.leX0.text()

    nFine = prUi.leNFine.text()
    printTrue = prUi.checkPrint.checkState()
    logging.debug("T: %s",T)
    logging.debug("n: %s",n)
    logging.debug("numOfSim: %s",numOfSim)
    try:
        t = np.linspace(0,float(T),float(n)+1)
        X0 = np.fromstring(X0,sep=",")
        X0 = np.reshape(X0,(len(X0),))
        numOfSim = int(numOfSim)
    except ValueError:
        openMessageBox(("T, n and number of simulations must be numbers."
            +" X0 is a vector of d values seperated by comma."))
        return
    try:
        nFine = int(nFine)
    except ValueError:
        nFine = None
        print("int(nFine) threw ValueError, nFine set to None")
    try:
        prob = SDEproblem.SDEprob(spec=spec,t=t,m=spec.m,X0=X0,
            totSimNum=numOfSim,nFine=nFine,printTrue=printTrue)
    except MemoryError:
        print("Memory-error raised, SDE object not created.")
        return

    if prob.completed == False:
        openMessageBox("SDEprob object did not complete for some reason.")
        return
    states[1]= (
        "Size of Wiener matrix (time x Wiener x simulation) = "
        + str(prob.W.shape) + ", T = " + T + ", n = " + n + ".")
    print("Problem realization state: ",states[1])
    updateObjectStates()
    pr.close()
    pra.show()

def openChooseSolvers():
    """Opens Choose solver."""
    global prob, solvers
    txtAction = "Action: "+praUi.cbAction.currentText()
    csUi.txtAction.setText(txtAction)
    newSolvers = SDEint.availableSolvers(problem=prob)
    if set(newSolvers) != set(solvers):
        solvers = newSolvers
        for i in range(len(solvers)):
            if csUi.checkBoxes[i] == None:
                csUi.checkBoxes[i] = QtWidgets.QCheckBox(solvers[i],csUi.groupBox)
                csUi.checkBoxes[i].move(5,25*(i+1))
            elif type(csUi.checkBoxes[i]) is QtWidgets.QCheckBox:
                csUi.checkBoxes[i].setText(solvers[i])
                csUi.checkBoxes[i].setChecked(False)
            else:
                raise NotImplementedError("Something weird happened.")
    cs.show()

def solverDict2List(sDict):
    '''Returns list of chosen solvers based on values in dict of bools.'''
    sList = []
    for key, value in sDict.items():
        if value:
            sList.append(key)
    return sList

def acceptSolvers():
    '''Set global solverDict to chosen solvers during Solution actions.'''
    global solverDict
    solverDict = {}
    solvers = SDEint.availableSolvers(problem=prob)
    for i in range(len(csUi.checkBoxes)):
        if csUi.checkBoxes[i] == None:
            break
        solver = csUi.checkBoxes[i].text()
        #print("i, csUi, solver: ",i, csUi.checkBoxes[i],solver)
        solverDict[solver] = csUi.checkBoxes[i].checkState()
    cs.close()

def executeAction():
    '''Executes chosen in action in Solution action prompt. '''
    action = praUi.cbAction.currentText()
    if solverDict == None:
        openMessageBox("You need to choose one or more solvers first.")
        return
    solverList = solverDict2List(solverDict)
    if action == 'Solve and plot a single sample path':
        for solvString in solverList:
            solver = SDEint.getSolver(prob,solverString=solvString)
            solver.solve()
        pra.close()
        spUi.checkSamp.setChecked(True)
        spUi.checkTrue.setChecked(True)
        spUi.checkMean.setChecked(False)
        spUi.checkMean.setChecked(False)
        sp.show()
    elif action == 'Solve and plot average of all sample paths':
        for solvString in solverList:
            solver = SDEint.getSolver(prob,solverString=solvString)
            solver.solve()
        pra.close()
        spUi.checkSamp.setChecked(False)
        spUi.checkTrue.setChecked(False)
        spUi.checkMean.setChecked(True)
        spUi.checkMean.setChecked(True)
        sp.show()
    elif action == 'Estimate strong order of convergence':
        SDEanalysis.calcStrongCon(prob,solverList)
    elif action == 'Estimate weak order of convergence':
        SDEanalysis.calcWeakCon(prob,solverList)
    elif action == 'Show contour plot of stability function(s)':
        SDEanalysis.calcStability(prob,solverList)
    else:
        openMessageBox("Something went horribly wrong in gui.executeAction()")

def openSolActions():
    """Closes former window since done and opens Solution actions."""
    cs.close()
    sa.show()    

def checkSamp():
    """Updates whether line-edit of sample nr is turned on if Plot sample on"""
    if spUi.checkSamp.checkState():
        spUi.leSampNr.setEnabled(True)
    else:
        spUi.leSampNr.setEnabled(False)

def plotSol():
    """Plots solution"""
    plotSamp = spUi.checkSamp.checkState()
    plotTrue = spUi.checkTrue.checkState()
    plotMean = spUi.checkMean.checkState()
    plotTrueMean = spUi.checkTrueMean.checkState()
    try:
        simNum = int(spUi.leSampNr.text())
    except ValueError:
        openMessageBox("Simulation number must be an integer.")
        return
    print("Starting plot method: ")
    prob.plotSolutions(plotTrue=plotTrue, plotMean=plotMean,
        plotTrueMean=plotTrueMean, plotSamp=plotSamp,simNum=simNum)

def updateObjectStates():
    """Updates descriptions of objects from states[] when called."""
    mwUi.txtProbSpec.setText(states[0])
    mwUi.txtProbReal.setText(states[1])
    if states[0] == "None-object":
        mwUi.txtProbSpec.setStyleSheet('background: red')
        mwUi.saveProbSpec.setEnabled(False)
        mwUi.btnSpecActions.setEnabled(False)
    else:
        mwUi.txtProbSpec.setStyleSheet('background: green')
        mwUi.saveProbSpec.setEnabled(True)
        mwUi.btnSpecActions.setEnabled(True)
    if states[1] == "None-object":
        mwUi.txtProbReal.setStyleSheet('background: red')
        mwUi.saveProbReal.setEnabled(False)
        mwUi.btnRealActions.setEnabled(False)
    else:
        mwUi.txtProbReal.setStyleSheet('background: green')
        mwUi.saveProbReal.setEnabled(True)
        mwUi.btnRealActions.setEnabled(True)

if __name__ == "__main__":
    """The GUI is run here.

    This is where everything in gui.py is tied together, and it can be hard to
    read. The actions done connected a menu is usually written in a code block,
    but since the menus interact, actions connected to one window are sometimes
    written in another window's block. There are also 2 types of blocks below.
    The blocks where a window is created from a PyQt script in the GUI folder,
    and blocks where button actions of the menu created above are established.
    """
    import sys
    
    #Global variables, the program assumes only 1 instance of the central
    #objects are needed, if more are needed, they can be stored. Since
    #different windows analyze a lot of the same values over again before the
    #objects are created, global variables are the simplest way to deal with
    #this.
    spec, prob = None, None#Central SDE-objects.
    f, trueSol, expSol = None, None, None#f, f', f'', f'''
    g, g1 = None, None#g, g', g'', g'''
    fExists, gExists = False, False
    probDir = None #Subfolder for new problem specification
    solverDict = None#For accept solvers.
    solvers = []#For choose solvers.
    
    #Start application and initialize state colors and text.
    app = QtWidgets.QApplication(sys.argv)
    mw = QtWidgets.QMainWindow()
    mwUi = mainWin.Ui_mainWin()
    mwUi.setupUi(mw)
    pixmap = QtGui.QPixmap('Operation.jpg')
    mwUi.pic.setPixmap(pixmap)
    mwUi.txtProbSpec.setStyleSheet('background: red')
    mwUi.txtProbReal.setStyleSheet('background: red')
    states = [mwUi.txtProbSpec.text(),mwUi.txtProbReal.text()]#Shows state of each object.

    #Establish actions of buttons and show main window.
    mw.show()
    mwUi.actionOpen.triggered.connect(lambda: fOpenObject())
    mwUi.saveProbSpec.clicked.connect(lambda: saveObject(spec))
    mwUi.saveProbReal.clicked.connect(lambda: saveObject(prob))
    mwUi.btnOpen.clicked.connect(lambda: fOpenObject())
    mwUi.btnClear.clicked.connect(lambda: clearObjects())
    mwUi.btnSpecActions.clicked.connect(lambda: pr.show())
    mwUi.btnRealActions.clicked.connect(lambda: pra.show())

    #Create window for Create New Problem
    cnp = QtWidgets.QWidget()
    cnpUi = newSpec.Ui_newSpec()
    cnpUi.setupUi(cnp)
    mwUi.btnNewProb.clicked.connect(lambda: cnp.show())

    #Button actions for Create New problem
    cnpUi.btnFolder.clicked.connect(lambda: createFolder())
    cnpUi.btnNewFunc.clicked.connect(lambda: openNewFunc())
    cnpUi.btnOpenFunc.clicked.connect(lambda: openFunc())
    cnpUi.checkTrue.stateChanged.connect(lambda: enableTrueName())

    #Create window for New F and set up button
    nf = QtWidgets.QWidget()
    nfUi = newFunc.Ui_newFunc()
    nfUi.setupUi(nf)
    nfUi.btnContinue.clicked.connect(lambda: validateFunc())

    #Create window for New Realization and set up actions.
    pr = QtWidgets.QWidget()
    prUi = newReal.Ui_newReal()
    prUi.setupUi(pr)
    cnpUi.btnCreate.clicked.connect(lambda: openProbSpecActions())#NewReal opens after
    #spec is created.
    prUi.cbDefault.stateChanged.connect(lambda: defaultValues())
    prUi.btnProbReal.clicked.connect(lambda: openProbRealActions())#Opens window with relevant parameters.

    #Create window for Problem Realization actions and set up actions.
    pra = QtWidgets.QWidget()
    praUi = probRealActions.Ui_probRealActions()
    praUi.setupUi(pra)
    praUi.btnSolver.clicked.connect(lambda: openChooseSolvers())
    praUi.btnExecute.clicked.connect(lambda: executeAction())
    
    #Create window for Choose Solvers.
    cs = QtWidgets.QWidget()
    csUi = chooseSolvers.Ui_chooseSolvers()
    csUi.setupUi(cs)
    csUi.checkBoxes = [None]*10
    csUi.btnProceed.clicked.connect(lambda: acceptSolvers())

    #Create window for Solution Plot.
    sp = QtWidgets.QWidget()
    spUi = solPlot.Ui_solPlot()
    spUi.setupUi(sp)

    #Setting up events for Solution Actions.
    spUi.checkSamp.stateChanged.connect(lambda: checkSamp())
    spUi.btnPlot.clicked.connect(lambda: plotSol())

    sys.exit(app.exec_())