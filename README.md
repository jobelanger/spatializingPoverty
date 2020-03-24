# Spatializing Poverty

Morocco Accessibility Model
This model measures travel time from villages in Tinghir Province, Morocco, to 3 key services of interest: health services, markets (commune centres), and schools. Travel mode is driving*. 

*Walking will be modeled for villages over 5km from a road. This function is not currently in the model.

Project Phases:

- 1 | import and clean MAR network
- 2 | snap origins and destinations to network (x3 for each facility)
- 3 | run OD matrix to calculate driving travel time from each O to D. output is one value per each OD pair.
- 4 | export each set of travel times to .csv and validate in QGIS
- 5 | * Walking time model - create road features for areas over 5km from the network Graph
- 6 | * Create Graph of walking time and add to driving Graph.
- 7 | * Re-run steps 1-4 with new Graph object
- 8 | * Join origins and destinations names columns to OD matrix and export output. Current functionality not available in gostnets. 

- *** phase has not been implemented
