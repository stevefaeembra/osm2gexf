osm2gexf
========

converts OSM xml files to a network graph in GEXF format

Intro
=====
This is a Python library which allows you to convert an OpenSteetMap (OSM) xml file into a GEXF file for import into Gephi, or other GEXF aware libraries.

The aim is to allow Street Network Analysis of OSM data using Gephi or other tools. 
This can then allow you to compute centralities, betweenness, eccentricity, etc.

An example can be found in demo.py

For larger OSM files I suggest you enable the 'network simplify'. This converts series of edges so that each series of edges between junctions is simplified to a single segment. THis helps keep the network size down.

Dependencies
============
None on the python side, all libraries are built in

Optional but recommended : a tool or library to process gexf files
Gephi - https://gephi.org/

