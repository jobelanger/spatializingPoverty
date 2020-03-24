#!/usr/bin/env python
# coding: utf-8

# last updated: 03.22.2020 by Johanna Belanger
# 
# ## Morocco Accessibility Model Part 1: Prep Network
# 
# ### Baseline model: This model measures travel time from villages in Tinghir Province, Morocco, to 3 key services of interest: health services, markets (commune centres), and schools. Travel mode is driving*. 
# 
# #### Walking will be modeled for villages over 5km from a road. This function is not currently in the model.
# 
# Phases:
# 
# - 1 | import and clean MAR network
# - 2 | snap origins and destinations to network (x3 for each facility)
# - 3 | run OD matrix to calculate driving travel time from each O to D. output is one value per each OD pair.
# - 4 | export each set of travel times to .csv and validate in QGIS
# - 5 | * Walking time model - create road features for areas over 5km from the network Graph
# - 6 | * Create Graph of walking time and add to driving Graph.
# - 7 | * Re-run steps 1-4 with new Graph object
# - 8 | * Join origins and destinations names columns to OD matrix and export output. Current functionality not available in gostnets. 
# 
# - *** phase has not been implemented

# In[ ]:


# configure script
import geopandas as gpd
import pandas as pd
import os, sys, time
# set file path of GOSTnets scripts
sys.path.append(os.path.join(r'/Users/jobelanger/GOSTnets-master/GOSTnets'))
import GOSTnets as gn
import networkx as nx
import osmnx as ox
from shapely.ops import unary_union
from shapely.wkt import loads
from shapely.geometry import LineString, MultiLineString, Point
import load_osm as losm


# set file path and load osm.pbf
pth = r'/Users/jobelanger/GOSTnets-master/morocco'
dataPth = r'/Users/jobelanger/GOSTnets-master/morocco/data'
outPth = r'/Users/jobelanger/GOSTnets-master/morocco/outputs'

# osm pbf last downloaded on: [insert date]
fil = r'morocco-latest.osm.pbf'
f = os.path.join(pth, 'data', fil)
mar = losm.OSM_to_network(f)


aoi = r'/Users/jobelanger/GOSTnets-master/mar/tinghirP.shp'

shp = gpd.read_file(os.path.join(dataPth, aoi))
print(shp)

shp_poly = shp.geometry.iloc[0]
# Check that the shape looks right
print(shp_poly)

# create G from tinghir roads within AOI
G = ox.graph_from_polygon(bound, network_type='drive')

# save the roads object as a pickle
gn.save(G, 'mar_unclean', './', pickle=True, nodes=False, edges=True)


# ## Step 2: Clean network and export as "clean" networkx Graph object.
# set the EPSG code for Morocco (MAR).
UTMZs = {'MAR':32629}

# do not adjust. OSM natively comes in ESPG 4326.
WGS = {'init':'epsg:4326'}

# this process can clean multiple networks at once in a loop style
countries = ['MAR']

# adjust to your input filepath:
base_pth = os.path.join(os.path.dirname(os.getcwd()), r'/Users/jobelanger/GOSTnets-master/morocco')
data_pth = os.path.join(base_pth, 'outputs')

for country in countries:
    print('\n--- processing for: %s ---\n' % country)
    print('start: %s\n' % time.ctime())

    print('Outputs can be found at: %s\n' % (data_pth))
        
    UTM = {'init': 'epsg:%d' % UTMZs[country]}
    
    G = nx.read_gpickle(os.path.join(data_pth, 'mar_unclean.pickle'))
    
    G = gn.clean_network(G, data_pth, country, UTM, WGS, 0.5, verbose = False)
    
    nx.write_gpickle(G, os.path.join(data_pth, 'mar_clean.pickle'))
    print('\nend: %s' % time.ctime())
    print('\n--- processing complete for: %s ---' % country)


print(G)


# ### find the largest subgraph of the network graph. 
# network analysis will only work correctly on graphs that are fully connected, otherwise there will be error.

# find largest sub graph of your Graph.
print('G before:')
print(G.size())
G_before = G.size()
largest = max(nx.strongly_connected_components(G), key=len)
G = nx.induced_subgraph(G, largest).copy()
print('G after:')
print(G.size())
G_after = G.size()

# calculate the percent of the network that is completed.
# analysis will only work correctly on graphs that are connected.
G_diff = (G_before - G_after)
G_diffPerc = (G_diff/G_before) * 100
G_percent = 100 - G_diffPerc
print(G_diff)
print(G_diffPerc)
print(G_percent)


# save the largest subgraph
gn.save(G, 'G_largest', './', pickle=True, nodes=False, edges=True)


# ### convert your network graph (default measurement in length) to a graph mesured in time.
# 
# uses the gostnets convert_network_to_time function and takes a speed dictionary and road colmn attribute as inputs. 
speedDict = {
                'residential': 30,  # kmph
                'primary': 60, # kmph
                'primary_link':55,
                'trunk': 40,
                'trunk_link':35,
                'secondary': 50, # kmph
                'secondary_link':45,
                'tertiary':40,
                'tertiary_link': 35,
                'unclassified':30, 
                'road':20,
                'crossing':20,
                'living_street':10
    
                } 


# convert network to time in minutes. use factor of 1000 to convert from km to meters
G_time = gn.convert_network_to_time(G, 
                                    distance_tag = 'length', 
                                    road_col = 'infra_type', 
                                    speed_dict = speedDict, 
                                    factor = 1000)


# save G_time object as pickle
gn.save(G_time, 'G_time', './', pickle=True, nodes=False, edges=True)


# ### now move on to the next script to run the OD matrices: "MAR_OD_03.22.2020_JB"
