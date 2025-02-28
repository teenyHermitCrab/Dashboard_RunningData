This project is an ongoing sandbox to learn data visualization techniques. Primarily using python libraries **`plotly`** and **`dash`**.

All the data here is generated from personal Strava run data.  Recorded data starts late 2015.    

Some run titles have been scrubbed for privacy reasons. Map plots that are general (e.g., heatmaps) will include these runs. If map plots show specific trace lines, those runs will be excluded.

This site built manually using **``dash``**.  Not using a website builder for this exercise.


---
As this project is a learning environment, upcoming changes:

* Add Marin Headlands page after finishing development on Lake Sonoma

* Add sources for estimate fields.

* Optimize chart response speeds: experimentation with clientside callbacks.

* Another interesting angle would be to incorporate **OAuth** authentication to Strava. This would allow users to check out their own data.

* Data is currently static. Add backend job to update data on daily or weekly basis

* Use browser storage to save data: dcc.Store or tabs to save state and speed transitions after initial loading

* minor issues:
  * change elevation units on Lake Sonoma topo to feet.
  * need more examples for respiration equivalents
  * reduce file sizes:
    * summary dataframe doesn't need to have all the columns, save only what is used in plots
    * filter to use only every n-th location in individual run files.in individual run files.
  