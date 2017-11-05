from semantics import *
from language import *

class Principle(object):
    """
    Common super class
    for all principles.
    """
    def __init__(self, model):
        self.model = model
        self.formulae = []
        self.result = []

    def _check(self):
        pass

    def permissible(self):
        pass

    def explain(self):
        pd = self.permissible()
        result = ""
        if pd == "Not Applicable":
            result = "The "+self.label+" is not applicable to this instance!"
        elif pd == True:
            result = "According to the "+str(self.label)+", the action "+str(self.action)+" is permissible!"
        else:
            result = result + "According to the "+str(self.label)+" principle, the action "+str(self.action)+" is not permissible!\n"
            result = result + "Because the following does not hold: \n"
            for i in range(len(self.result)):
                if not self.result[i]:
                    result = result + self.formulae[i]+"\n"
        return result


class DoubleEffectPrinciple(Principle):
    """
    An Implementation of
    the formalization of the
    double effect principle
    according to section 4.
    """
    def __init__(self, model):
        super(DoubleEffectPrinciple, self).__init__(model)
        self.label = "Double Effect Principle"

    # Condition 1 - The Act Itself Must Be Morally Good or Indifferent
    def _condition1(self):
        return GEq(U(self.model.action), 0)

    # Condition 2 - The Positive Consequence Must Be Intended ...
    def _condition2a(self):
        f = None
        for c in self.cons:
            f = Impl(I(c), GEq(U(c), 0)) if f is None else And(f, Impl(I(c), GEq(U(c), 0)))
        return f

    # Condition 2b - ... and the Negative Consequence May not Be Intended
    def _condition2b(self):
        f = None
        for c in self.cons:
            f = And(I(c), Gt(U(c), 0)) if f is None else Or(f, And(I(c), Gt(U(c), 0)))
        return f

    # Condition 3 - The Negative Consequence May Not Be a Means to Obtain the Positive Consequence
    def _condition3(self):
        f = None
        for cj in self.cons:
            for ck in self.cons:
                f = Not(And(Causes(cj, ck), And(Gt(0, U(cj)), Gt(U(ck), 0)))) if f is None else And(f, Not(And(Causes(cj, ck), And(Gt(0, U(cj)), Gt(U(ck), 0)))))
        return f

    # Condition 4 - There Must Be Proportionally Grave Reasons to Prefer the Positive Consequence While Permitting the Negative Consequence
    def _condition4(self):
        f = None
        for c in self.cons:
            f = c if f is None else And(f, c)
        return Gt(U(f), 0)

    def _check(self):
        self.cons = self.model.getDirectConsequences()
        self.formulae = [self._condition1(), self._condition2a(), self._condition2b(), self._condition3(), self._condition4()]
        if None in self.formulae:
            self.result = "Not Applicable"
            return self.result
        self.result = [self.model.models(f) for f in self.formulae]
        return self.result

    def permissible(self):
        self._check()
        return self.result if self.result == "Not Applicable" else self.result == [True, True, True, True, True]


class UtilitarianPrinciple(Principle):
    """
    This principle compares
    some world to its
    alternatives. According
    to the utilitarian principle,
    a world is permissible
    iff it is among the worlds
    with highest utility.
    """
    def __init__(self, model):
        super(UtilitarianPrinciple, self).__init__(model)
        self.label = "Utilitarianism"

    def _check(self):
        u = U(Formula.makeConjunction(self.model.getAllConsequences()))
        v = []
        for w in self.model.alternatives:
            if self.model != w:
                v.append(U(Formula.makeConjunction(w.getAllConsequences())))
        f = None
        for w in v:
            f = GEq(u, w) if f is None else And(f, GEq(u, w))
        self.formulae = [f]
        self.result = [self.model.models(f)]
        return self.result

    def permissible(self):
        self._check()
        return self.result == [True]


class DoNoHarmPrinciple(Principle):
    """
    This principle permits an action
    iff it has no bad consequence.
    """
    def __init__(self, model):
        super(DoNoHarmPrinciple, self).__init__(model)
        self.label = "Do No Harm"

    def _check(self):
        cons = self.model.getDirectConsequences()+[self.model.action]
        f = None
        for c in cons:
            if f is None:
                f = GEq(U(c), 0)
            else:
                f = And(f, GEq(U(c), 0))
        if f is None:
            self.result = [True]
        else:
            self.formulae = [f]
            self.result = [self.model.models(f)]
        return self.result

    def permissible(self):
        self._check()
        return self.result == [True]
        

class ParetoPrinciple(Principle):
    """ This principle permits an action
    iff it is not dominated by any other action.
    """
    def __init__(self, model):
        super(ParetoPrinciple, self).__init__(model)
        self.label = "Pareto"

    def _dominates(self, w0, w1):
        cons_good_w1 = []
        cons_bar_good_w1 = []
        cons_bad_w1 = []
        cons = w1.getAllConsequences()
        for c in cons:
            if w1.models(Gt(U(c), 0)):
                cons_good_w1.append(c)
            elif w1.models(Gt(0, U(c))):
                cons_bad_w1.append(c)
            if w1.models(Gt(U(Not(c)), 0)):
                cons_bar_good_w1.append(c)
        
        cons = w0.getAllConsequences()
        cons_bad_w0 = []
        for c in cons:
            if w0.models(Gt(0, U(c))):
                cons_bad_w0.append(c)

        # Condition 1
        f1 = Formula.makeConjunction(cons_good_w1)
        if f1 == None:
            cond1 = True
        else:
            cond1 = w0.models(f1)
        if cond1 == False:
            return False

        # Condition 2
        f2a = Formula.makeDisjunction(cons_bar_good_w1)
        f2b = Not(Formula.makeConjunction(cons_bad_w1))
        
        if f2a == None:
            cond2a = False
        else:
            cond2a = w0.models(f2a)
        if f2b == None:
            cond2b = False
        else:
            cond2b = w0.models(f2b)
        if cond2a == False and cond2b == False:
            return False

        # Condition 3
        f3 = Formula.makeConjunction(cons_bad_w0)

        if f3 == None:
            cond3 = True
        else:
            cond3 = w1.models(f3)

        return cond3            

    def _check(self):
        self.result = [True]
        for w in self.model.alternatives:
            if w != self.model:
                if self._dominates(w, self.model):
                    self.result = [False]
                    break

    def permissible(self):
        self._check()
        return self.result == [True]
