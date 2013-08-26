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

from Network import OSMNetwork, GEXFFile
from OSMParser import OSMNetworkParser, OSMWayRoadFilter
from xml.sax import make_parser 


if __name__ == '__main__':
    """
    Sample code. Create the OSM SAX parser, build a network object and
    output it to a GEXF file for use in Gephi
    """       
            
    network = OSMNetwork()
    parser = make_parser()    
    osmparser = OSMNetworkParser(network)
    osmparser.addFilter(OSMWayRoadFilter())
    parser.setContentHandler(osmparser)
    parser.parse(open(r'/path/to/file.osm'))
    osmparser.net.simplify()        
    out = GEXFFile(file(r'/path/to/output.gexf','w'),osmparser.net)
    print "Done!"