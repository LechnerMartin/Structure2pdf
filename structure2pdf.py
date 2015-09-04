#! /usr/bin/env python3
import sys
import uuid
import re

import os
import pygraphviz
import networkx as nx



class GraphNode:
    def __init__(self, data):
        self.data = data
        self.children=[]
        
    def __str__(self):
        return str(id(self)) + " data:" + str(self.data) + " childs:" + str(len(self.children))


class Graph(object):
    def __init__(self):
        self.rootnode = GraphNode(None)
    
    def addpath(self, path):
        pathitems = path.split("/")[:-1]
        parent = self.rootnode
        for item in pathitems:
            child = self.get_children_containing_item(parent, item)
            if child == None :
                child = GraphNode(item)
                parent.children.append(child)
            parent = child

    def get_children_containing_item(self, node, item):
        for child in node.children :
            if child.data == item : return child
        return None
    
    @property
    def nodelist(self):
        return self.reduce_nodelist(None)

    def reduce_nodelist(self, levels):
        nodelist = []
        for child in self.rootnode.children:
            self.fill_nodelist(child, nodelist, levels)
        return nodelist


    def fill_nodelist(self, node, nodelist, levels = None):
        if levels != None :
            levels -= 1
            if levels < 0:return
        if node == None:return
        nodelist.append(node)
        for child in node.children:
            self.fill_nodelist(child, nodelist, levels)
    
    @property
    def edgelist(self):
        return self.reduce_edgelist(None)

    def reduce_edgelist(self, levels = None):
        edgelist = []
        for child in self.rootnode.children:
            self.fill_edgelist(child, edgelist, levels)
        return edgelist


    def fill_edgelist(self, node, edgelist, levels = None):
        if levels != None :
            levels -= 1
            if levels < 1:return # edges have one level less than nodes
        if node == None:return
        for child in node.children:
            edgelist.append([node,child])
            self.fill_edgelist(child, edgelist, levels)


##################################

#line1="trunk/en/trunk/"
#line2="trunk/en/book/appa-quickstart.xml"
#line3 ="trunk/tools/po4a/"





def containsText(text, regex):
    if (not regex) or (regex == "") : return None
    result = re.search(regex, text)
    return result is not None

def includeLineFilter(line, regex):
    if containsText(line, regex) == False: return ""
    return line

def excludeLineFilter(line, regex):
    if containsText(line, regex) == True: return ""
    return line



def get_graph_from_file(filename, include, exclude):
    graph = Graph()
    with open(filename) as f:
        for line in f:
            line = includeLineFilter(line, include)
            line = excludeLineFilter(line, exclude)
            graph.addpath(line)
    return graph

def get_nxgraph_from_pathgraph(pathgraph, levels=None):
    nxgraph = nx.DiGraph()
    for node in pathgraph.reduce_nodelist(levels):
        nxgraph.add_node(id(node), label=node.data)
    for edge in pathgraph.reduce_edgelist(levels):
        idedge = [id(node) for node in edge]
        nxgraph.add_edge(idedge[0], idedge[1])

    return nxgraph



#######################

def main(args):
    filename = args.file
    outputname = args.output
    
    dotfile = outputname + ".dot"
    pdffile = outputname + ".pdf"
    pngfile = outputname + ".png"

    print("reading: " + filename)
    pathgraph = get_graph_from_file(filename, args.include, args.exclude)
    graph = get_nxgraph_from_pathgraph(pathgraph, args.depth)

    print("writing dot")
    nx.write_dot(graph, dotfile)
    print("processing dot")
    os.system("dot -Tpng -Grankdir=LR " + dotfile + " -o " + pngfile)
    os.system("dot -Tpdf -Grankdir=LR " + dotfile + " -o " + pdffile)

#pos=nx.graphviz_layout(graph,prog='dot', args="-Grankdir=LR")
#nx.draw(graph,pos, with_labels=True, arrows=False)
#print(edgelist)





##################### Graph tests ###############

def datalist(nodelist):
    return [ node.data for node in nodelist]

def datalist2(edgelist):
    return [ datalist(edge) for edge in edgelist]

def test_emptypath():
    graph = Graph()
    graph.addpath("")
    assert datalist(graph.nodelist) == [] 
    
def test_simplepath():
    graph = Graph()
    graph.addpath("a/")
    assert datalist(graph.nodelist) == ["a"] 
    assert graph.edgelist == [] 
    
def test_simplepath1():
    graph = Graph()
    graph.addpath("a/b/a/")
    assert datalist(graph.nodelist) == ["a","b","a"] 
    assert datalist2(graph.edgelist) == [["a","b"],["b","a"]] 
    
def test_secondpath():
    graph = Graph()
    graph.addpath("a/b/a/")
    graph.addpath("a/b/c/")
    assert datalist(graph.nodelist) == ["a","b","a","c"] 
    assert datalist2(graph.edgelist) == [["a","b"],["b","a"],["b","c"]] 

def test_reduce_path_to_n_levels():
    graph = Graph()
    graph.addpath("a/b/c/d/")
    assert datalist(graph.reduce_nodelist(5)) == ["a","b","c","d"] 
    assert datalist(graph.reduce_nodelist(4)) == ["a","b","c","d"] 
    assert datalist(graph.reduce_nodelist(3)) == ["a","b","c"] 
    assert datalist(graph.reduce_nodelist(1)) == ["a"] 
    assert datalist2(graph.reduce_edgelist(5)) == [["a","b"],["b","c"],["c","d"]] 
    assert datalist2(graph.reduce_edgelist(3)) == [["a","b"],["b","c"]]

def test_containsTextNoRexexOrText():
    assert containsText("a", None) == None
    assert containsText("a", "") == None
    assert containsText("","a") == False

def test_containsText():
    assert containsText("aba","a") == True
    assert containsText("bacb","b.*b") == True


def test_includeLineFilter():
    assert includeLineFilter("a", "") == "a"
    assert includeLineFilter("a", None) == "a"
    assert includeLineFilter("bac", "a") == "bac"
    assert includeLineFilter("aaa", "b") == ""
    
def test_excludeLineFilter():
    assert excludeLineFilter("a","") == "a"
    assert excludeLineFilter("a","a") == ""
    assert excludeLineFilter("bcb","a") == "bcb"
    assert excludeLineFilter("bab","a") == ""
    

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Structure generator")
    parser.add_argument("--file", "-f" , help="File with structure information foramt: ls -R")
    parser.add_argument("--output", "-o" , help="output name",  default="structure")
    parser.add_argument("--depth", '-d', help="depth of tree", default=None, type=int)
    parser.add_argument("--include", '-i', help="regex to include path line", default="")
    parser.add_argument("--exclude", '-e', help="regex to excluded pathline", default="")

    args = parser.parse_args()
    #print (args.server)
    main(args)
