# -*- coding: utf-8 -*-
"""
Created on Sat Oct  3 22:34:59 2020

@author: franc
"""

class Node:
    def __init__(self,attribute,split,parent,children,subset):
        self.attribute=attribute
        self.split=split
        self.parent=parent
        self.children=children
        self.subset=subset
    
    def setChildren(self,children):
        self.children=children
    
    def setClass(self,end):
        self.end=end