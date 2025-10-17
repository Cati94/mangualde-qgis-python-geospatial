# -*- coding: utf-8 -*-
"""
Created on Wed Apr 30 10:51:43 2025

@author: Paddington
"""

import geopandas as gpd

#Carregar freguesias e isolar as de Manugualde 

# Carrega o ficheiro das freguesias (pode ser .shp, .gpkg ou .geojson)
freguesias = gpd.read_file("Users/Paddington/Desktop/Trabalho_geoespacial_Mangualde/data/CAOP/Continente_CAOP2024.gpkg")

# Verifica os nomes disponíveis
print(freguesias.columns)

# Filtra as freguesias de Mangualde
freg_mangualde = freguesias[freguesias["municipio"] == "Mangualde"]

# Confirma
print(freg_mangualde[["freguesia", "geometry"]])

#calculo da área das freguesias em hectares# 

# Garante o sistema de coordenadas em metros (ex: EPSG:3763)
freg_mangualde = freg_mangualde.to_crs(epsg=3763)

# Calcula a área em hectares
freg_mangualde["area_ha"] = freg_mangualde.geometry.area / 10_000

# Mostra resultado
print(freg_mangualde[["freguesia", "area_ha"]])

#Guardar para QGIS 
import os
print(os.getcwd())
os.chdir("C:/Users/Paddington/Desktop/Trabalho_geoespacial_Mangualde/python")

freg_mangualde.to_file("freguesias_mangualde.geojson", driver="GeoJSON")

import geopandas as gpd

# Carregar o ficheiro da COS de Mangualde
solo_mangualde = gpd.read_file("C:/Users/Paddington/Desktop/Trabalho_geoespacial_Mangualde/data/COS/COS_Mangualde.gpkg")

# Filtrar áreas florestais
florestal = solo_mangualde[solo_mangualde["COS18n1_L"] == "Florestas"]

# Calcular área total do concelho
area_total = solo_mangualde["Area_ha"].sum()

# Calcular área florestal
area_florestal = florestal["Area_ha"].sum()

# Calcular percentagem
percent_floresta = (area_florestal / area_total) * 100

print(f"Área florestal: {area_florestal:.2f} ha")
print(f"Percentagem da área florestal: {percent_floresta:.2f}%")


#Guardar para QGIS 
import os
print(os.getcwd())
os.chdir("C:/Users/Paddington/Desktop/Trabalho_geoespacial_Mangualde/python")
solo_mangualde.to_file("solo_mangualde.geojson", driver="GeoJSON")


#Elevacao e declive

import geopandas as gpd
import rasterio
import rasterio.mask
import numpy as np
import matplotlib.pyplot as plt

freg_mangualde = gpd.read_file("C:/Users/Paddington/Desktop/Trabalho_geoespacial_Mangualde/python/freguesias_mangualde.geojson")
with rasterio.open("C:/Users/Paddington/Desktop/Trabalho_geoespacial_Mangualde/srtm_pt.tif") as src:
    # Recorta o raster ao concelho
    out_image, out_transform = rasterio.mask.mask(src, freg_mangualde.geometry, crop=True)
    out_meta = src.meta.copy()

# Remove valores nulos (no data)
elev = out_image[0]
elev = elev[elev != src.nodata]

print(f"Altitude mínima: {np.min(elev):.2f} m")
print(f"Altitude máxima: {np.max(elev):.2f} m")

from scipy import ndimage

# Gradientes (derivadas em x e y)
gy, gx = np.gradient(out_image[0], 1)  # pixel = 1 unidade
slope = np.sqrt(gx**2 + gy**2)

# Converte para graus
slope_degrees = np.arctan(slope) * 180 / np.pi

print(f"Declive mínimo: {np.min(slope_degrees):.2f}°")
print(f"Declive máximo: {np.max(slope_degrees):.2f}°")


plt.figure(figsize=(12,5))

plt.subplot(1,2,1)
plt.title("Modelo Digital de Elevação")
plt.imshow(out_image[0], cmap="terrain")
plt.colorbar(label="m")

plt.subplot(1,2,2)
plt.title("Declive (graus)")
plt.imshow(slope_degrees, cmap="magma")
plt.colorbar(label="°")

plt.tight_layout()
plt.show()



# REDE VIÁRIA E EDIFÍCIOS

import osmnx as ox
import geopandas as gpd
from shapely.geometry import Polygon
import matplotlib.pyplot as plt

# Carregar o concelho
concelho = gpd.read_file("C:/Users/Paddington/Desktop/Trabalho_geoespacial_Mangualde/python/freguesias_mangualde.geojson")
concelho = concelho.to_crs(epsg=4326)  # projeta para WGS84 (necessário para OSM)

# Extrai as estradas dentro da geometria do concelho
estradas = ox.features_from_polygon(concelho.unary_union, tags={"highway": True})

# Mantém apenas as linhas (estradas)
estradas = estradas[estradas.geometry.type == 'LineString']

# Converter para CRS métrico (PT-TM06/ETRS89)
estradas = estradas.to_crs(epsg=3763)

# Calcular o comprimento total da rede viária
estradas["comprimento_m"] = estradas.geometry.length
total_km = estradas["comprimento_m"].sum() / 1000  # em km

print(f"Extensão total da rede viária: {total_km:.2f} km")

# Extrai edifícios dentro da geometria do concelho
edificios = ox.features_from_polygon(concelho.unary_union, tags={"building": True})

# Mantém apenas os polígonos (edifícios)
edificios = edificios[edificios.geometry.type == 'Polygon']

# Contar o número de edifícios
n_edificios = len(edificios)

print(f"Número total de edifícios digitalizados: {n_edificios}")

# Visualizar os resultados
fig, ax = plt.subplots(figsize=(10,10))
concelho.boundary.plot(ax=ax, color='black', linewidth=1)
estradas.plot(ax=ax, color='red', linewidth=0.5)
edificios.plot(ax=ax, color='gray', alpha=0.5)
plt.title("Rede Viária e Edifícios em Mangualde")
plt.show()

# Salvar os resultados em arquivos GeoJSON
import os
print(os.getcwd())
os.chdir("C:/Users/Paddington/Desktop/Trabalho_geoespacial_Mangualde/python")
estradas.to_file("estradas_mangualde.geojson", driver="GeoJSON")
edificios.to_file("edificios_mangualde.geojson", driver="GeoJSON")


