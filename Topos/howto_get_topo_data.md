# Where to get elevation data?

To be clear, I don't have any specialized knowledge of working with geo data. So probably there are much easier ways to get this data. I'm sure there are python libraries where I could extract this data programmatically

This is just where I got data initially.
<hr>

## NOAA
NOAA has a page where one can extract lidar data.  
https://www.coast.noaa.gov/dataviewer/#/lidar/search/

This does not have complete coverage, but it does have areas I am interested in.

1. Draw bounding box on map
2. Select data source and add to cart. Go to cart, press **Next**
    * TODO: I need to learn about these sources and why to pick one over another.
3. I chose following options:
    * **Projection**: Geographic (Lat/Lon)
    * **Output Product**: Raster
    * **Output Format**: Grid - GeoTiff 32-bit
    * **Grid Size**:  This value was increased to 50-100 ft or so to reduce the map size
4. Submit order, a confirmation email will be sent. Later, another email will provide link to data.
5. Download .zip link and extract
6. Use desktop QGIS to view .tiff file.  Note: not necessary to do this step, but it is a confimation that you got correct data. Use provided mosaic file if output was broken up into separate file. Just drag the .tiff file into application window.
    * find QGIS install [here](https://qgis.org/)
    * Instead of desktop app, I initially tried pip installing `gdal` but ran into issues.  Haven't further investigated, but I'd prefer a pip install
7. Use QGIS shell to translate .tiff file to .csv 
    * `gdal2xyz` is program to use.  
8. `pandas.read_csv()` gets you a pandas dataframe to work with.  If using output from `gdal2xyz`, you'll have to add column names to csv file or dataframe