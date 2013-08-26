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

from xml.sax.handler import ContentHandler 
from Network import OSMNode,OSMWay

"""
Filters take an OSMObject and either accept it (true) or reject it (false)
Add filters to OSMBasicParser using its addFilter(filter) method
The object is accepted or rejected using the AND of all the filters
"""

class OSMFilter(object):
    
    def accept(self,obj):
        return True
    
class OSMWayFilter(OSMFilter):
    
    def accept(self,obj):
        return super(OSMWayFilter,self).accept(obj)
    
class OSMWayRoadFilter(OSMWayFilter):
    
    def accept(self,obj):
        res=False
        if "highway" in obj.attrs.keys():
            if obj.attrs['highway'] in ['primary','secondary','tertiary','residential','unclassified']:
                res=True
        return res


class OSMParserContext(object):
    """
    An enum to keep track of context for the
    SAX parser (are we inside a node or a way element?)
    """
    UNKNOWN = 0
    INSIDE_NODE = 1
    INSIDE_WAY = 2

class OSMParser(ContentHandler):
    
    """
    SAX-based parser for OSM XML files
    Null implementation, does nothing - simply
    a framework for subclasses that actually
    do something ;-)
    """
       
    def __init__(self):
        pass
    
    def startElement(self, name, attrs):
         
        if name=="node":
            # node definition
            pass
        
        if name=="nd":
            # node as part of a way
            pass
        
        if name=="tag":
            # tag (maybe part of node or way)
            pass
        
        if name=="way":
            # way
            pass
            
    def endElement(self, name): 

        if name=="node":
            # node definition
            pass
               
        if name=="tag":
            # tag (maybe part of node or way)
            pass
        
        if name=="way":
            # way
            pass
            
    def characters (self, ch): 
        pass

class OSMCounterParser(OSMParser):
    
    """
    SAX-based parser for OSM XML files
    Simply counts number of each type of object
    Useful for assessing the size of a file
    """
       
    def __init__(self):
        self.nodes=0
        self.ways=0
    
    def startElement(self, name, attrs):
         
        if name=="node":
            self.nodes+=1
               
        if name=="way":
            # way
            self.ways+=1
            
class OSMNetworkParser(OSMParser):
    
    """
    A more useful parser, hopefully.
    Creates dictionaries of nodes and ways,
    and links the two up into a network
    """
   
    def __init__(self,osm_network):
        self.net = osm_network
        self.filters=[]
        self.currentway=None
        #self.addFilter(OSMFilter())
    
    def addFilter(self, filter):
        """
        add a filter to the filter chain
        """
        self.filters.append(filter)
        
    def _getAttrDict(self,xmlattrs):
        """
        takes xml attributes list and converts to a dictionary
        """
        res={}
        for (k,v) in xmlattrs.items():
            res[k]=v
        return res
        
    def startElement(self, name, attrs):
         
        if name=="node":
            self.context=OSMParserContext.INSIDE_NODE
            self.currentnode = OSMNode(self._getAttrDict(attrs))

        if name=="tag":
            key = attrs['k']
            value = attrs['v']
            if self.context==OSMParserContext.INSIDE_NODE:
                self.currentnode.attrs[key]=value
            if self.context==OSMParserContext.INSIDE_WAY:
                self.currentway.attrs[key]=value
        
        if name=="nd":
            nodeid = attrs['ref']
            self.currentway.addNode(nodeid)
               
        if name=="way":
            # way
            self.context=OSMParserContext.INSIDE_WAY
            self.currentway = OSMWay(self._getAttrDict(attrs))
            
    def endElement(self, name): 

        if name=="node":
            # node definition
            self.net.addNode(self.currentnode)
                       
        if name=="way":
            # way
            accept = True
            for filt in self.filters:
                accept = accept and filt.accept(self.currentway) 
            if accept:
                self.net.addWay(self.currentway)

    def debug(self):
        self.net.debug()

