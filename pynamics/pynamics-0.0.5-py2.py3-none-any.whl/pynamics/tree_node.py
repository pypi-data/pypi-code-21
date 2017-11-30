# -*- coding: utf-8 -*-

"""
Written by Daniel M. Aukes
Email: danaukes<at>gmail.com
Please see LICENSE for full license.
"""


class TreeNode(object):
    def __init__(self):
        self.parent = None
        self.children = []
        self.decendents = []
        self.ancestors = []

    def _set_parent(self,parent):
        self.parent = parent

    def _add_children(self,children):
        self.children.extend(children)
        self.children = list(set(self.children))

    def _add_decendents(self,decendents,recursive = True):
        self.decendents.extend(decendents)
        self.decendents = list(set(self.decendents))
        if recursive:
            if self.parent!=None:
                self.parent._add_decendents(decendents,recursive)

    def _add_ancestors(self,ancestors):
        self.ancestors.extend(ancestors)
        self.ancestors = list(set(self.ancestors))

    def top(self):
        if self.parent==None:
            return self
        else:
            return self.parent.top()
            
    def path_to_top(self,path_in=None):
        if path_in == None:
            path_in = []
        path_in = path_in+[self]
        if self.parent==None:
            return path_in
        else:
            return self.parent.path_to_top(path_in)

    def build_topology(self,ancestors=None,parent = None):
        if ancestors == None:
            ancestors = []
        self._set_parent(parent)
        self._add_ancestors(ancestors)

        for child in self.children:
            child.build_topology(ancestors+[self],self)
        self._add_decendents(self.children)

    def path_to(self,other):
        a = self.path_to_top()[::-1]
        b = other.path_to_top()[::-1]
        if a[0]!=b[0]:
            raise(Exception("Frames don't share a common parent"))
        for ii,(item1,item2) in enumerate(zip(a,b)):
            if item1!=item2:
                ii-=1
                break
        return a[:ii:-1]+b[ii:]

    def is_connected(self,other):
        return self.top()==other.top()
    
    def add_branch(self,child):
        self._add_children([child])
        child.build_topology(self.ancestors+[self],self)
        self._add_decendents([child]+child.decendents)
    
    def leaves(self):
        top = self.top()
        leaves = [item for item in top.decendents if not item.children]
        return leaves
        
if __name__=='__main__':
    A = TreeNode()
    B = TreeNode()
    C = TreeNode()
    D = TreeNode()    
    E = TreeNode()    
    F = TreeNode()    
    
    connections = [[E,F],[A,B],[B,C],[A,D],[D,E]]
    for parent, child in connections:
        parent.add_branch(child)
        