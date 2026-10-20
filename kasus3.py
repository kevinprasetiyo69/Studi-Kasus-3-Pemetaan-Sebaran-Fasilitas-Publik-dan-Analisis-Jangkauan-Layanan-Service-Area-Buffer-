import folium
import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

data_facilities = {
    'facility_id': ['FAS-01', 'FAS-02'],
    'name': ['Fasilitas Pusat', 'Fasilitas Cabang'],
    'latitude': [-3.7928, -3.8050],
    'longitude': [102.2608, 102.2750],
}
df_fac = pd.DataFrame(data_facilities)
gdf_fac = gpd.GeoDataFrame(
    df_fac,
    geometry=gpd.points_from_xy(df_fac.longitude, df_fac.latitude),
    crs='EPSG:4326',
)

data_residents = {
    'resident_id': ['R-01', 'R-02', 'R-03', 'R-04'],
    'resident_name': ['Area Warga A', 'Area Warga B', 'Area Warga C', 'Area Warga D'],
    'latitude': [-3.7950, -3.7900, -3.8200, -3.8020],
    'longitude': [102.2620, 102.2580, 102.3000, 102.2710],
}
df_res = pd.DataFrame(data_residents)
gdf_res = gpd.GeoDataFrame(
    df_res,
    geometry=gpd.points_from_xy(df_res.longitude, df_res.latitude),
    crs='EPSG:4326',
)

gdf_fac_utm = gdf_fac.to_crs('EPSG:32748')
gdf_res_utm = gdf_res.to_crs('EPSG:32748')

gdf_fac_utm['buffer_1km'] = gdf_fac_utm.geometry.buffer(1000)
gdf_buffer = gdf_fac_utm.set_geometry('buffer_1km')

joined = gpd.sjoin(gdf_res_utm, gdf_buffer, predicate='within', how='left')
terlayani_ids = joined[joined['facility_id'].notnull()]['resident_id'].unique()

print('=== STATUS JANGKAUAN LAYANAN ===')
for _, row in gdf_res.iterrows():
  status = 'Terjangkau' if row['resident_id'] in terlayani_ids else 'Di Luar Radius (Blank Spot)'
  print(f"{row['resident_name']}: {status}")

gdf_buffer_wgs = gdf_buffer.to_crs('EPSG:4326')

peta = folium.Map(location=[-3.7989, 102.2679], zoom_start=13)

folium.GeoJson(
    gdf_buffer_wgs,
    style_function=lambda x: {
        'fillColor': '#3388ff',
        'color': '#0033cc',
        'weight': 2,
        'fillOpacity': 0.25,
    },
    tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['Layanan:']),
).add_to(peta)

for _, row in gdf_fac.iterrows():
  folium.Marker(
      location=[row['latitude'], row['longitude']],
      popup=f"<b>{row['name']}</b>",
      icon=folium.Icon(color='blue', icon='info-sign'),
  ).add_to(peta)

for _, row in gdf_res.iterrows():
  is_covered = row['resident_id'] in terlayani_ids
  color = 'green' if is_covered else 'red'
  folium.Marker(
      location=[row['latitude'], row['longitude']],
      popup=f"{row['resident_name']} ({'Terjangkau' if is_covered else 'Blank Spot'})",
      icon=folium.Icon(color=color, icon='user'),
  ).add_to(peta)

peta.save('index.html')
print('\nPeta WebGIS berhasil disimpan ke file index.html')
