# 2AMD20
2AMD20 project

This project aims to merge 4 different datasets into one knowledge graph. The datasets to merge are: <br>
-housing prices <br>
-housing availability <br>
-population density <br>
-movement between municipalities <br>
<br>
The raw data can be found in the Data folder. The notebook used to clean this data is done in "Official_dataset_cleaning.ipynb" which can be found in the Code folder.
The output of this script are the cleaned datasets in cleanedDFs. The metaData folder contains all information on the original datasets. <br>
<br>
To run the visualisation tool, got to the directory: 2AMD20/Code/Visualization_tool. Here you will find visualisation.py, which is a visualisation tool build in DASH. All necessary libraries can be found at the top of the python file as imports. The file can be run from a python environment and will create it's own localhost from which the visualisation tool can be used.
