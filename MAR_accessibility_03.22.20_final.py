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

# Clean network and export as "clean" networkx Graph object.
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

# find the largest subgraph of the network graph. 
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


# convert your network graph (default measurement in length) to a graph mesured in time.
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



###
'''Morocco Accessibility Model Part 2: OD Matrices'''
###


# import G_time from previous script
G = nx.read_gpickle(r'/Users/jobelanger/GOSTnets-master/morocco/G_time.pickle')

# import origins and destinations
# next, import origins (Tinghir villages) and destinations (health centres, markets, and schools). 

# read in origins
villages = gpd.read_file(os.path.join(dataPth, 'Tinghir_Villages.shp'))
# create x/y columns in villages dataframe
from shapely import geometry # sometimes you have to reimport
villages['x']= villages.geometry.x
villages['y']= villages.geometry.y
villages

# read in destination 1: Health
health = gpd.read_file(os.path.join(dataPth, 'Tinghir_Health.shp'))
health['x']= health.geometry.x
health['y']= health.geometry.y
health

# read in destination 2: Markets
markets = gpd.read_file(os.path.join(dataPth, 'tinghirMarketsP.shp')
                        
markets['x']= markets.geometry.x
markets['y']= markets.geometry.y
markets.head()

# read in destination 3: Schools
schools = gpd.read_file(os.path.join(dataPth, 'tinghirSchoolP.shp'))
schools['x']= schools.geometry.x
schools['y']= schools.geometry.y
schools.head()


# ### snap origins and destinations to the network 
# now use geopandas pandana_snap to get closest network node associated with the origin and destination nodes. 

# snap network to villages
villages = gn.pandana_snap_c(G_time, 
                           villages, 
                           source_crs='epsg:32629', 
                           target_crs='epsg:32629', 
                           add_dist_to_node_col=True)
# two new columns have been created with nearest network node from the node to the graph.
villages.head()
# create a list of villages using NN.
# the OD calculation function only takes lists as inputs.
villages_ls = list(set(list(villages.NN)))
villages_ls

# snap destination 1: Health
health = gn.pandana_snap(G_time, 
                         health, 
                         source_crs='epsg:32629',
                         target_crs='epsg:32629', 
                         add_dist_to_node_col=True)

health.head()
health_ls = list(set(list(health.NN)))
health_ls

# snap destination 2: Markets
markets = gn.pandana_snap(G_time, 
                           markets, 
                           source_crs='epsg:4326', 
                           target_crs='epsg:4326', 
                           add_dist_to_node_col=True)

markets.head()
markets_ls = list(set(list(markets.NN)))
markets_ls

# snap destination 3: Schools
schools = gn.pandana_snap(G_time, 
                           schools, 
                           source_crs='epsg:4326', 
                           target_crs='epsg:4326', 
                           add_dist_to_node_col=True)

schools.head()
schools_ls = list(set(list(schools.NN)))
schools_ls

# ### calculate origin-destination matrices
# run gostnets OD calculator for villages to each of the three destinations
# returns numpy matrix of format o-d with shortest travel time, which we will convert to a pandas dataframe, and then to a .csv.

# OD matrix villages to destination 1: Health
# 'VH' stands for village-to-health
OD_VH = gn.calculate_OD(G_time, 
                     villages_ls, 
                     health_ls, 
                     fail_value=9999999)

OD_VH
# check the shape to verify results
OD_VH.shape


# use minutes as the measure by dividing every value in the OD matrix by 60. 
# then convert the array to a df.
OD_VH = OD_VH/60
OD_VHdf = pd.DataFrame(OD_VH, columns=health_ls, index=villages_ls)
OD_VHdf


## OD matrix villages to destination 2: Markets/Commune Centers)
# 'VM' stands for village-to-markets
OD_VM = gn.calculate_OD(G_time, 
                     markets_ls, 
                     health_ls, 
                     fail_value=9999999)
OD_VM
OD_VM.shape


OD_VM = OD_VM/60
OD_VMdf = pd.DataFrame(OD_VM, columns=markets_ls, index=villages_ls)
OD_VMdf

# OD matrix villages to destination 3: Schools
# 'VS' stands for village-to-schools
OD_VS = gn.calculate_OD(G_time, 
                     schools_ls, 
                     health_ls, 
                     fail_value=9999999)
OD_VS
OD_VS.shape


OD_VS = O_VS/60
OD_VSdf = pd.DataFrame(OD_VS, columns=schools_ls, index=villages_ls)
OD_VSdf

# ### export OD matrix dataframes to .csv
# 
# export OD matrix dataframes to a .csv to view in QGIS and verify with Morocco field team
# rewrite output path to be Morocco gostnets output folder.
pth = outPth
OD_VH.to_file(pth, 'OD_village2health.csv')
OD_VM.to_file(pth, 'OD_village2market.csv')
OD_VS.to_file(pth, 'OD_village2school.csv')

# files can be found at: 
print(pth)