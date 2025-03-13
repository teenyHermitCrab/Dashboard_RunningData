#### code is a bit of a mess right now - bunch of different experiments jammed together.  clean up time!

find project here

https://www.corkhorde.com


This project is an ongoing sandbox to learn data visualization techniques. Primarily using python libraries **`plotly`** and **`dash`**.

All the data here is generated from personal Strava run data.  Recorded data starts late 2015.    

Some run titles have been scrubbed for privacy reasons. Map plots that are general (e.g., heatmaps) will include these runs. If map plots show specific trace lines, those runs will be excluded.

This site built manually using **``dash``**.  Not using a website builder for this exercise.


---
As this project is a learning environment, upcoming changes:
* Use browser storage to save data: dcc.Store or tabs to save state and speed transitions after initial loading
* Add Marin Headlands page after finishing development on Lake Sonoma
* Experimentation with clientside callbacks.
* Another interesting angle would be to incorporate **OAuth** authentication to Strava. This would allow users to check out their own data.
* Data is currently static. Add backend job to update data on daily or weekly basis
* minor issues:
  * change elevation units on Lake Sonoma topo to feet.
  * reduce file sizes:
    * summary dataframe doesn't need to have all the columns, save only what is used in plots
    * filter to use only every n-th location in individual
