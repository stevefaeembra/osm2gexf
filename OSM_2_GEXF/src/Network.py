'''
    Copyright (C) 2011 Steven Kay

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from distance import distVincenty

class OSMObject(object):

    """
    Root of all OSM objects.
    """
    
    def __init__(self,attrs):
        self.attrs=attrs
        self.id=attrs['id']
    
class OSMNode(OSMObject):
    
    """
    Node - may form part of a way, or may be an isolated point
    like a pub or bus-stop
    """
    
    def __init__(self,attrs):
        super(OSMNode,self).__init__(attrs)
        self.neighbours={} #ids of neighbours
        self.ways={} # ids of ways
        self.attrs=attrs
        
    def addNeighbour(self,nodeid):
        self.neighbours[nodeid]=""

    def dropNeighbour(self,nodeid):
        if self.neighbours.has_key(nodeid):
            del self.neighbours[nodeid]
        
    def addToWay(self,wayid):
        self.ways[wayid]=""

    def dropFromWay(self,wayid):
        if self.ways.has_key(wayid):
            del self.ways[wayid]

    def __repr__(self):
        s=[]
        s.append("NODE %s :" % (self.id,))
        s.append("Neighbours (%s) " % (", ".join(n for n in self.neighbours.keys())))
        s.append("Ways(%s) " % (", ".join(w for w in self.ways.keys())))
        s.append("Tags(%s) " % self.attrs)
        return "".join(s)

class OSMWay(OSMObject):
    
    """
    A way consists of a series of nodes joined together
    """
    
    def __init__(self,attrs):
        super(OSMWay,self).__init__(attrs)
        self.nodes=[] # simple list of nodes (order important)
        
    def addNode(self,nodeid):
        self.nodes.append(nodeid)

    def __repr__(self):
        s=[]
        s.append("WAY %s :" % (self.id,))
        s.append("Nodes (%s) " % (", ".join(n for n in self.nodes)))
        s.append("Tags(%s) " % (self.attrs,))
        return "".join(s)

"""
A weighter calculates the weight of an edge
takes two OSMNodes and the OSMWay node they belong to
then computes a float weight
"""

class weighter(object):
    
    def __init__(self,osmnodefrom,osmnodeto,way):
        self.fromnode=osmnodefrom
        self.tonode=osmnodeto
        self.way=way

    def getweight(self):
        return 1.0

class weighter_road_importance(weighter):
    
    def __init__(self,osmnodefrom,osmnodeto,way):
        super(weighter_road_importance,self).__init__(osmnodefrom,osmnodeto,way)
        
    def getweight(self):
        if self.way.attrs.has_key('highway'):
            type = self.way.attrs['highway']
            if type=='motorway': return 16.0
            if type=='trunk': return 8.0
            if type=='primary': return 6.0
            if type=='secondary': return 4.0
            if type=='tertiary': return 3.0
            if type=='residential': return 1.5
            if type=='service': return 1.0
            if type=='unclassified': return 1.0
            return 1.0
        else:
            return 1.0
            
class weighter_road_importance_distance(weighter_road_importance):
    
    def __init__(self,osmnodefrom,osmnodeto,way):
        super(weighter_road_importance_distance,self).__init__(osmnodefrom,osmnodeto,way)
    
    def getweight(self):
        weight=super(weighter_road_importance_distance,self).getweight()
        lon1 = float(self.fromnode.attrs['lon'])
        lat1 = float(self.fromnode.attrs['lat'])
        lon2 = float(self.tonode.attrs['lon'])
        lat2 = float(self.tonode.attrs['lat'])
        dist = distVincenty(lat1, lon1, lat2, lon2)
        return weight*dist

class GEXFFile():
    
    """
    Takes a network object and outputs GEXF format to a textIO instance
    such as a File object
    Currently very quick and dirty, plenty works needs doing to store
    things like edge weights and arbitrary collections of node properties
    """
    
    def __init__(self, textIO,network):
        """
        pass a subclass of textIObase
        """
        self.out = textIO
        self.net=network
        self.write()
        print "Wrote "+str(len(self.net.nodes))+" nodes"
        print "Wrote "+str(len(self.net.segments.keys()))+" edges"
        
    def write(self):        
        self.out.write("""<?xml version="1.0" encoding="UTF-8"?>
<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">
<meta lastmodifieddate="2009-03-20">
<creator>Gexf.net</creator>
<description>A hello world! file</description>
</meta>
<graph mode="static" defaultedgetype="directed">
<nodes>
""")
        self.out.write("""
<attributes class="node">
<attribute id="0" title="lat" type="float"/>
<attribute id="1" title="lon" type="float"/>
</attributes>
""")

        for nodeid in self.net.nodes:
            nodeobj=self.net.nodes[nodeid]
            if len(nodeobj.neighbours)>0:
                s=[]
                s.append ("<node id=\"%s\" label=\"%s\">\n" % (nodeid,nodeid))
                s.append("<attvalues>\n")
                s.append("<attvalue for=\"0\" value=\"%s\" />" % (nodeobj.attrs['lat']))
                s.append("<attvalue for=\"1\" value=\"%s\" />" % (nodeobj.attrs['lon']))
                s.append("</attvalues>\n")
                s.append("</node>")
                self.out.write("".join(s))
            
        self.out.write("</nodes>")

        self.out.write("<edges>")
        ix=0
        for edge in self.net.segments.keys():
            fromnodeid, tonodeid=edge
            s = "<edge id=\"%d\" source=\"%s\" target=\"%s\" weight=\"%2.4f\" />\n" % (ix,fromnodeid,tonodeid,self.net.segments[edge])
            self.out.write(s)
            ix+=1
        self.out.write("</edges>")

        self.out.write("    </graph>\n")
        self.out.write("</gexf>\n")

        self.out.close()

class OSMNetwork():
    
    """
    Represents a directed/undirected road network
    (a) a collection of nodes
    (b) a collection ways - series of nodes joined together e.g. for roads
    (c) segments - pairs of (nodefrom,nodeto) showing that two nodes are joined
    """
    
    def __init__(self):
        self.nodes={} # ID -> OSMNode
        self.ways={} # ID -> OSMWay
        self.segments={} # (fromNodeID,toNodeid)=""
    
    def addNode(self,nodeobj):
        id=nodeobj.id
        self.nodes[id]=nodeobj
        
    def dropNode(self,nodeid):
        if self.nodes.has_key(nodeid):
            del self.nodes[nodeid]
    
    def addWay(self,wayobject):
        id=wayobject.id
        self.ways[id]=wayobject
        nodeids=wayobject.nodes
        for node in nodeids:
            self.nodes[node].addToWay(id)
        for x in range(0,len(nodeids)-1):
            fromnode=nodeids[x]
            tonode=nodeids[x+1]
            self.addSegment(wayobject,fromnode,tonode,False)
       
    def dropWay(self,wayobject):
        id=wayobject.id
        del self.ways[id]
        nodeids=wayobject.nodes
        for node in nodeids:
            self.nodes[node].dropFromWay(id)
        for x in range(0,len(nodeids)-1):
            fromnode=nodeids[x]
            tonode=nodeids[x+1]
            self.dropSegment(fromnode,tonode,False)      
         
    def addSegment(self,wayobject,fromid,toid,directed=False):
        self.nodes[fromid].addNeighbour(toid)
        self.nodes[toid].addNeighbour(fromid)
        # work out weight of segment
        weighter = weighter_road_importance_distance(self.nodes[fromid],self.nodes[toid],wayobject)
        weight = weighter.getweight()
        key=(fromid,toid)
        self.segments[key]=weight
        if directed:
            key=(toid,fromid)
            self.segments[key]=weight

    def dropSegment(self,fromid,toid,directed=False):
        self.nodes[fromid].dropNeighbour(toid)
        self.nodes[toid].dropNeighbour(fromid)
        key=(fromid,toid)
        if self.segments.has_key(key):
            del self.segments[key]
        if directed:
            key=(toid,fromid)
            if self.segments.has_key(key):
                del self.segments[key]

    def simplify(self):
        """
        Simplify ways - useful to simplify things like circuses and
        roundabouts which may consist of a lot of very small segments
        Must only be called once network is complete 
        for each node 'B' in way which..
        (a) isnt the first or last node
        (b) has exactly two neighbours
        A <-> B <-> C
        We remove the node and join the outer 2 nodes 'A' and 'C'
        Weight of new segment (A,C) taken to be the sum of the weights
        of old segments (A,B) and (A,C)
        """
        dropped=0
        for nodeid in self.nodes.keys():
            if len(self.nodes[nodeid].neighbours)==2:
                if len(self.nodes[nodeid].ways)==1:
                    wayid = self.nodes[nodeid].ways.keys()[0]
                    if len(self.ways[wayid].nodes)>2:
                        anode=self.nodes[nodeid].neighbours.keys()[0]
                        cnode=self.nodes[nodeid].neighbours.keys()[1]
                        try:
                            self.nodes[anode].addNeighbour(cnode)
                            self.nodes[anode].dropNeighbour(nodeid)
                            self.nodes[cnode].addNeighbour(anode)
                            self.nodes[cnode].dropNeighbour(nodeid)
                            self.dropSegment(anode,nodeid)
                            self.dropSegment(nodeid,cnode)
                            self.addSegment(self.ways[wayid], anode, cnode)
                            dropped+=1
                        except:
                            print "oops..."
                        del self.nodes[nodeid]
        print "Simplify : Dropped %d segments" % (dropped,)
                        
    def debug(self):
        for node in self.nodes.values():
            print `node`
        for way in self.ways.values():
            print `way`
        for key in self.segments.keys():
            print "%s=%2.4f" % (key,self.segments[key])
        


if __name__ == '__main__':
    pass