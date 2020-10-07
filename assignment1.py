# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
from math import log
import treeNode
import time


file = open('adult1.data.txt')
data = [[]]
for line in file:
    line = line.strip("/r/n")
    data.append(line.split())

data.remove([])
attributeList=data[0]
instances = data[1:]
classIndex = attributeList.index('Class')
availAttr=attributeList[:-2]
#print(attributeList)
#print(instances[0])
#print(classIndex)
#print(instances[1][classIndex])

#entropy calculation
def calEnt(dataset):
    if dataset==[]:
        return 1
    size=len(dataset)
    c1=0    #<=50K
    for item in dataset:
        if item[classIndex] == "<=50K":
            c1+=1
    p=c1/size
    #print(c1,size,p)
    if c1==size or c1==0:
        return 0
    result = -p*log(p,2)-(1-p)*log((1-p),2)
    return result

#entropy calculation for split based on input attribute, to find the next split
def entGain(attribute,dataset):
    attrIndex=attributeList.index(attribute)
    instanceCount=len(dataset)
    labelSet={}
    entropy=0
    for item in dataset:
        if item[attrIndex] not in labelSet.keys():
            labelSet[item[attrIndex]]=[]   #create subset for label
        labelSet[item[attrIndex]].append(item)
    for label in labelSet:
        labelSize=len(labelSet[label])
        ent=labelSize/instanceCount*calEnt(labelSet[label]) #entropy for each subset
        entropy+=ent
    return entropy
#print(calEnt(instances))
#for item in attributeList: 
#    print(item)
#    print(entGain(item,instances))

#split the dataset by input attribute
def dataSplit(attribute,dataset):
    attrIndex=attributeList.index(attribute)
    labelSet={}
    for item in dataset:
        if item[attrIndex] == '?':      #skip unknown label for training
            continue
        if item[attrIndex] not in labelSet.keys():
            labelSet[item[attrIndex]]=[]    #create subset for label
        labelSet[item[attrIndex]].append(item)
    return labelSet

#find majority class
def findMajority(dataset):
    lowCount=0
    highCount=0
    for item in dataset:
        if item[classIndex] == '<=50K':
            lowCount+=1
        else:
            highCount+=1
    if lowCount>=highCount:             #find majority and define node class
        return '<=50K'
    else:
        return '>50K'

#iterative building nodes based on split entropy gain
def iterBuild(unusedAttr,node,dataset):     #build decision tree nodes iteratively
    if unusedAttr == [] or len(dataset)<50:                    #stop naturally
        node.setClass(findMajority(dataset))
        #print('stop due to attr used up', unusedAttr)
        return
    currentEnt=calEnt(dataset)              #calculate current entropy
    maxGain=0
    for attribute in unusedAttr:
        gain=currentEnt - entGain(attribute,dataset)    #find next attribute
        if gain>maxGain:
            maxGain=gain
            nextAttr=attribute
    if maxGain>0:
        splitSet=dataSplit(nextAttr,dataset)
    else:                                   #stopping if no gain
        node.setClass(findMajority(dataset))
        #print('stop due to no gain')
        return
    children=[]
    remainingAttr=unusedAttr[:]
    remainingAttr.remove(nextAttr)
    for label in splitSet:
        newNode=treeNode.Node(nextAttr,label,node,[],splitSet[label])
        children.append(newNode)
        iterBuild(remainingAttr, newNode, splitSet[label])
    node.setChildren(children)
    

#decision tree building
def buildTree(attributeList,dataset):
    root=treeNode.Node(None,None,None,[],dataset)
    iterBuild(attributeList, root, dataset)
    return root
    
"""

#to find split point of continuous attribute (3 splits)

def findSplit(attribute,dataset):       #find splitting point for continuous attribute
    attrIndex=attributeList.index(attribute)
    minEnt=1
    split1=0
    split2=0
    for i in range(17,90):
        for j in range(17,90):
            cliff1=i+0.5
            cliff2=j+0.5
            set1=[]
            set2=[]
            set3=[]
            for item in dataset:
                if int(item[attrIndex])<cliff1:
                    set1.append(item)
                elif int(item[attrIndex])<cliff2 and int(item[attrIndex])>cliff1:
                    set2.append(item)
                else:
                    set3.append(item)
            entropy=len(set1)/len(dataset)*calEnt(set1)+len(set2)/len(dataset)*calEnt(set2)+len(set3)/len(dataset)*calEnt(set3)
            if entropy<minEnt:
                split1=cliff1
                split2=cliff2
                minEnt=entropy
            #print(cliff,entropy,len(set1),len(set2),len(dataset),calEnt(set1),calEnt(set2))
    return split1,split2,minEnt
    
"""


#to find split point of continuous attribute (2 splits)
def findSplit(attribute,dataset):       #find splitting point for continuous attribute
    attrIndex=attributeList.index(attribute)
    minEnt=1
    split=0
    for i in range(-50,100):
        cliff=i+0.5
        set1=[]
        set2=[]
        for item in dataset:
            if int(item[attrIndex])<cliff:
                set1.append(item)
            else:
                set2.append(item)
        entropy=len(set1)/len(dataset)*calEnt(set1)+len(set2)/len(dataset)*calEnt(set2)
        if entropy<minEnt:
            split=cliff
            minEnt=entropy
        print(cliff,entropy,len(set1),len(set2),len(dataset),calEnt(set1),calEnt(set2))
    return split,minEnt

#tree visualization
def printTree(node,level=0):
    totalNode.append(1)
    print("\t"*level,node.attribute,node.split,'\n')
    #return
    if node.children==[]:
        print(node.end)
        if node.end == '<=50K':
            lowNode.append(1)
        else:
            highNode.append(1)
        return
    else:
        for child in node.children:
            printTree(child,level+1)

#find parent of leaf nodes
def findBranch(node,lastBranch):
    if node.children==[] and node.parent not in lastBranch:
        lastBranch.append(node.parent)
        return
    else:
        for child in node.children:
            findBranch(child,lastBranch)

#as is
def nodeError(node):
    count = 0
    majority = findMajority(node.subset)
    for item in node.subset:
        if item[classIndex]!=majority:
            count+=1
    return count

#post prune based on pessimistic error
def postPrune(node):
    lastBranch=[]
    findBranch(node,lastBranch)
    #print("last branch",str(len(lastBranch)))
    #print(lastBranch[0].children[1].children)
    for branch in lastBranch:
        set1=[]
        set2=[]
        for item in branch.subset:
            if item[classIndex] == "<=50K":
                set1.append(1)
            else:
                set2.append(1)
        branchError = min(len(set1),len(set2))
        splitError = 0
        for child in branch.children:
            splitError += nodeError(child)
        if splitError + 0.5*len(node.children) > branchError:
            #print(splitError, 0.5*len(node.children),branchError)
            branch.setChildren([])
            branch.setClass(findMajority(node.subset))
            postPrune(node)
        else:
            return
    
totalNode=[]
lowNode=[]
highNode=[]
start = time.time()
#print(classIndex)

#build the decision tree
builtTree=buildTree(availAttr, instances)
#comment out if post prune is not needed
postPrune(builtTree)

#some tree visualization, doesnt quite work if you expect more than 100 nodes
#printTree(builtTree)
print(len(lowNode),len(highNode),len(totalNode))
end = time.time()
print('building time', str(end - start))

file = open('adult.test.txt')
testset = [[]]
for line in file:
    line = line.strip("/r/n")
    testset.append(line.split())

testset.remove([])
testset = testset[1:]

#iterative test
def runTest(node,item):
    if node.children == []:
        #print("stopping", node.end, item[classIndex], str(node.end == item[classIndex]))
        if node.end == item[classIndex]:
            correct.append(1)
            return
        else:
            wrong.append(1)
            return
    else:
        for child in node.children:
            if item[attributeList.index(child.attribute)]=="?":
                maxLen=0
                for i in node.children:
                    if len(i.subset)>maxLen:
                        maxLen=len(i.subset)
                        majorNode=i
                runTest(majorNode,item)
                break
            elif child.split == item[attributeList.index(child.attribute)]:
                runTest(child,item)
                break
start = time.time()
correct=[]
wrong=[]
for item in testset:
    runTest(builtTree,item)

end = time.time()
print('testing time', str(end - start))
print(len(testset),len(correct),len(wrong))

                



#start = time.time()

#
#print(findSplit('hours-per-week',instances))
#end = time.time()
#print(end - start)
    
    
    
    
    
    
    
    
