#!/usr/bin/env python
# coding: utf-8

# last updated: 03.22.2020 by: Johanna Belanger
# 
# ## Morocco Accessibility Model Part 2: OD Matrix
# 
# ### Baseline model: This model measures travel time from villages in Tinghir Province, Morocco, to 3 key services of interest: health services, markets (commune centres), and schools. Travel mode is driving*. 
# 
# #### Walking will be modeled for villages over 5km from a road. This function is not currently in the model.
# 
# Phases:
# 
# - 1 | import and clean MAR network
# - 2 | snap origins and destinations to network (x3 for each facility)
# - 3 | run OD matrix to calculate driving travel time from each O to D. output is one value per each OD pair.*
# - 4 | export each set of travel times to .csv and validate in QGIS*
# - 5 | * Walking time model - create road features for areas over 5km from the network Graph
# - 6 | * Create Graph of walking time and add to driving Graph.
# - 7 | * Re-run steps 1-4 with new Graph object
# - 8 | * Join origins and destinations names columns to OD matrix and export output. Current functionality not available in gostnets. 
# 
# * phase has not been implemented

# In[ ]:


# configure script
import geopandas as gpd
import pandas as pd
import os, sys, time
# set file path of GOSTnets scripts.  
sys.path.append(os.path.join(os.path.dirname(os.getcwd()), r'/Users/jobelanger/GOSTnets-master/GOSTnets'))
import GOSTnets as gn
import networkx as nx
import osmnx as ox
from shapely.ops import unary_union
from shapely.wkt import loads
from shapely.geometry import LineString, MultiLineString, Point


# In[ ]:


# set paths
pth = os.path.join(os.path.dirname(os.getcwd()), r'/Users/jobelanger/GOSTnets-master/morocco')
dataPth = r'/Users/jobelanger/GOSTnets-master/morocco/data'
outPth = r'/Users/jobelanger/GOSTnets-master/morocco/outputs'


# In[ ]:


# import G_time from previous script
G = nx.read_gpickle(r'/Users/jobelanger/GOSTnets-master/morocco/G_time.pickle')


# ### import origins and destinations
# 
# next, import origins (Tinghir villages) and destinations (health centres, markets, and schools). 

# In[ ]:


# read in origins
villages = gpd.read_file(os.path.join(dataPth, 'Tinghir_Villages.shp'))

# create x/y columns in villages dataframe
from shapely import geometry
villages['x']= villages.geometry.x
villages['y']= villages.geometry.y

villages


# In[ ]:


# read in destination 1: Health
health = gpd.read_file(os.path.join(dataPth, 'Tinghir_Health.shp'))

from shapely import geometry
health['x']= health.geometry.x
health['y']= health.geometry.y

health


# In[ ]:


# read in destination 2: Markets
markets = gpd.read_file(os.path.join(dataPth, 'tinghirMarketsP.shp')
                        
from shapely import geometry
markets['x']= markets.geometry.x
markets['y']= markets.geometry.y

markets.head()


# In[ ]:


# read in destination 3: Schools
schools = gpd.read_file(os.path.join(dataPth, 'tinghirSchoolP.shp'))

schools['x']= schools.geometry.x
schools['y']= schools.geometry.y

schools.head()


# ### snap origins and destinations to the network 
# 
# 
# now use geopandas pandana_snap to get closest network node associated with the origin and destination nodes. 

# In[ ]:


# snap network to villages
villages = gn.pandana_snap_c(G_time, 
                           villages, 
                           source_crs='epsg:32629', 
                           target_crs='epsg:32629', 
                           add_dist_to_node_col=True)


# In[ ]:


# two new columns have been created with nearest network node from the node to the graph.
villages.head()


# In[ ]:


# create a list of villages using NN.
# the OD calculation function only takes lists as inputs.
villages_ls = list(set(list(villages.NN)))
villages_ls


# In[ ]:


# snap destination 1: Health
health = gn.pandana_snap(G_time, 
                         health, 
                         source_crs='epsg:32629',
                         target_crs='epsg:32629', 
                         add_dist_to_node_col=True)

health.head()


# In[ ]:


health_ls = list(set(list(health.NN)))
health_ls


# In[ ]:


# snap destination 2: Markets
markets = gn.pandana_snap(G_time, 
                           markets, 
                           source_crs='epsg:4326', 
                           target_crs='epsg:4326', 
                           add_dist_to_node_col=True)

markets.head()


# In[ ]:


markets_ls = list(set(list(markets.NN)))
markets_ls


# In[ ]:


# snap destination 3: Schools
schools = gn.pandana_snap(G_time, 
                           schools, 
                           source_crs='epsg:4326', 
                           target_crs='epsg:4326', 
                           add_dist_to_node_col=True)

schools.head()


# In[ ]:


schools_ls = list(set(list(schools.NN)))
schools_ls


# ### calculate origin-destination matrices 
# 
# run gostnets OD calculator for villages to each of the three destinations
# 
# returns numpy matrix of format o-d with shortest travel time, which we will convert to a pandas dataframe, and then to a .csv.

# In[ ]:


# OD matrix villages to destination 1: Health
# 'VH' stands for village-to-health
OD_VH = gn.calculate_OD(G_time, 
                     villages_ls, 
                     health_ls, 
                     fail_value=9999999)

OD


# In[ ]:


# check the shape to verify results
OD_VH.shape


# In[ ]:


# use minutes as the measure by dividing every value in the OD matrix by 60. 
# then convert the array to a df.
OD_VH = OD_VH/60

OD_VHdf = pd.DataFrame(OD_VH, columns=health_ls, index=villages_ls)

OD_VHdf


# In[ ]:


## OD matrix villages to destination 2: Markets/Commune Centers)
# 'VM' stands for village-to-markets
OD_VM = gn.calculate_OD(G_time, 
                     markets_ls, 
                     health_ls, 
                     fail_value=9999999)

OD_VM


# In[ ]:


OD_VM.shape


# In[ ]:


OD_VM = OD_VM/60

OD_VMdf = pd.DataFrame(OD_VM, columns=markets_ls, index=villages_ls)

OD_VMdf


# In[ ]:


# OD matrix villages to destination 3: Schools
# 'VS' stands for village-to-schools
OD_VS = gn.calculate_OD(G_time, 
                     schools_ls, 
                     health_ls, 
                     fail_value=9999999)

OD_VS


# In[ ]:


OD_VS.shape


# In[ ]:


OD_VS = O_VS/60

OD_VSdf = pd.DataFrame(OD_VS, columns=schools_ls, index=villages_ls)

OD_VSdf


# ### export OD matrix dataframes to .csv
# 
# export OD matrix dataframes to a .csv to view in QGIS and verify with Morocco field team

# In[ ]:


# rewrite output path to be Morocco gostnets output folder.
pth = outPth
OD_VH.to_file(pth, 'OD_village2health.csv')
OD_VM.to_file(pth, 'OD_village2market.csv')
OD_VS.to_file(pth, 'OD_village2school.csv')


# In[ ]:


# files can be found at: 
print(pth)


# #### find the full script as a .py file in the same folder.
