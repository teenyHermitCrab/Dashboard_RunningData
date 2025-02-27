import json
import numpy as np
import pandas as pd
import Assets.file_paths as fps

##### get my saved, processed data
df_all_runs: pd.DataFrame = pd.read_pickle(fps.page_overview_all_runs_df_path)

# overview page
with open(fps.page_overview_geojson_fips_path, 'r') as f:
    json_counties = json.load(f)
fips_to_name = pd.read_pickle(fps.page_overview_fips_to_name_df_pickle_path)

# Lake Sonoma page
df_all_LS_runs: pd.DataFrame = pd.read_pickle(fps.page_lake_sonoma_df_all_runs_path)
topo_pickle_path = fps.page_lake_sonoma_topo_map_path
df_topo = pd.read_pickle(topo_pickle_path)
# ls_run_file = fps.page_lake_sonoma_100K_run_path
# df_100K_run = pd.read_csv(ls_run_file)
# df_100K_run['elevation'] = df_100K_run['elevation'] + 3
Z:np.ndarray = pd.read_pickle(fps.page_lake_sonoma_topo_z_data_path)
Z_water:np.ndarray = pd.read_pickle(fps.page_lake_sonoma_topo_z_water_data_path)


