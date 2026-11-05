#!/usr/bin/env python
# coding: utf-8

# ANÁLISE ESTATÍSTICA ESPACIAL

# %% INSTALAÇÃO DOS PACOTES NECESSÁRIOS
# Execute esta célula uma vez no ambiente Python em que o projeto será utilizado.
# Depois da instalação, você pode comentar esta célula para evitar reinstalações.
import subprocess
import sys

PACOTES_NECESSARIOS = [
    "geopandas",
    "libpysal",
    "esda",
    "splot",
    "rasterio",
    "shapely",
    "folium",
    "matplotlib",
    "numpy",
    "pandas",
    "plotly",
    "seaborn",
]

subprocess.check_call(
    [sys.executable, "-m", "pip", "install", *PACOTES_NECESSARIOS]
)
print("Instalação dos pacotes concluída!")

# %% [00] PREPARAÇÃO E IMPORTAÇÃO DOS PACOTES
# Nesta etapa são carregadas as bibliotecas e definidas as opções de exibição.
import glob
import json
import os
import warnings

import folium
import geopandas as gpd
import libpysal
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import plotly.express as px
import seaborn as sns
from esda.moran import Moran, Moran_Local
from rasterio.transform import from_origin
from shapely.validation import make_valid
from splot.esda import moran_scatterplot

warnings.filterwarnings("ignore")
pd.set_option("display.max_columns", 25)
pd.set_option("display.width", 1000)
plt.style.use(
    "seaborn-v0_8-whitegrid"
    if "seaborn-v0_8-whitegrid" in plt.style.available
    else "default"
)

print("Todos os pacotes foram importados com sucesso!")

#############################################################################
# %% [01] CARREGAMENTO E PREPARAÇÃO DAS BASES            #
#############################################################################
uf = "28"
pasta_dados = "datasets"

caminho_malha = os.path.join(pasta_dados, f"malha_ibge_uf_{uf}.geojson")
caminho_localidades = os.path.join(
    pasta_dados, f"municipios_ibge_uf_{uf}.json"
)
caminho_indicadores = os.path.join(
    pasta_dados, "indicadores_socioeconomicos_municipios.csv"
)
caminho_lojas = os.path.join(pasta_dados, "lojas_varejo.csv")
caminho_concorrentes = os.path.join(pasta_dados, "concorrentes_varejo.csv")
caminho_rodovias = os.path.join(pasta_dados, "rede_viaria.geojson")

# %% [01.1] Ler os arquivos oficiais, indicadores e bases comerciais.
# 01.1. Ler os arquivos oficiais, indicadores e bases comerciais.
# Todos os caminhos são relativos à pasta de execução do script.
# 1. Leitura dos dados geográficos e tabulares
gdf_ibge_bruto = gpd.read_file(caminho_malha)
df_nomes_municipios = pd.read_json(caminho_localidades)
df_indicadores = pd.read_csv(caminho_indicadores)
df_lojas = pd.read_csv(caminho_lojas)
df_concorrentes = pd.read_csv(caminho_concorrentes)
gdf_rodovias = gpd.read_file(caminho_rodovias)


# %% [01.2] Carregar a malha complementar de 2025 para comparação cartográfica.
# 01.2. Carregar a malha complementar de 2025 para comparação cartográfica.
# Se houver mais de um shapefile, selecione o arquivo correto abaixo.
# 6. Carregamento da malha municipal complementar de 2025 (Shapefile)
pasta_shapefiles = "./shapefiles/SE_Municipios_2025"

arquivos_shp = sorted(
    glob.glob(os.path.join(pasta_shapefiles, "**", "*.shp"), recursive=True)
)

# Se houver vários arquivos, priorize o que tiver "municip" no nome.
# Ajuste SHAPEFILE_PRINCIPAL manualmente se precisar selecionar outro arquivo.
SHAPEFILE_PRINCIPAL = None
if SHAPEFILE_PRINCIPAL:
    caminho_shapefile_2025 = os.path.join(
        pasta_shapefiles, SHAPEFILE_PRINCIPAL
    )
else:
    candidatos_municipais = [
        caminho
        for caminho in arquivos_shp
        if "municip" in os.path.basename(caminho).lower()
    ]
    caminho_shapefile_2025 = (candidatos_municipais or arquivos_shp)[0]

gdf_malha_2025 = gpd.read_file(caminho_shapefile_2025)


# Reparar geometrias inválidas sem alterar o CRS original
mascara_geometrias_invalidas = (
    gdf_malha_2025.geometry.notna() & ~gdf_malha_2025.geometry.is_valid
)
if mascara_geometrias_invalidas.any():
    print(
        "Reparando "
        f"{mascara_geometrias_invalidas.sum()} geometrias inválidas "
        "do shapefile 2025..."
    )
    gdf_malha_2025.loc[mascara_geometrias_invalidas, "geometry"] = (
        gdf_malha_2025.loc[mascara_geometrias_invalidas, "geometry"].apply(
            make_valid
        )
    )

print("\n--- SHAPEFILE MUNICIPAL COMPLEMENTAR 2025 ---")
print(f"Arquivo selecionado: {caminho_shapefile_2025}")
print(f"Feições: {len(gdf_malha_2025)}")
print(f"CRS original: {gdf_malha_2025.crs}")
print(f"Colunas: {gdf_malha_2025.columns.tolist()}")

# %% [01.3] Associar códigos IBGE a nomes, microrregiões e indicadores.
# 01.3. Associar códigos IBGE a nomes, microrregiões e indicadores.
# 2. Junção tabular da malha geográfica com nomes e microrregiões
gdf_ibge_bruto["codarea"] = gdf_ibge_bruto["codarea"].astype(int)

df_nomes_limpo = pd.DataFrame(
    {
        "cod_ibge": df_nomes_municipios["id"],
        "nome_municipio": df_nomes_municipios["nome"],
        "microrregiao": [
            m["nome"] for m in df_nomes_municipios["microrregiao"]
        ],
    }
)

gdf_municipios = gdf_ibge_bruto.merge(
    df_nomes_limpo, left_on="codarea", right_on="cod_ibge", how="inner"
)

# 3. Junção com indicadores socioeconômicos reais
gdf_municipios = gdf_municipios.merge(
    df_indicadores, on="cod_ibge", how="left"
)

# Padronização de CRS para WGS84
if gdf_municipios.crs is None:
    gdf_municipios = gdf_municipios.set_crs(epsg=4674)
gdf_municipios = gdf_municipios.to_crs(epsg=4326)

# 4. GeoDataFrames de pontos
gdf_lojas_atuais = gpd.GeoDataFrame(
    df_lojas,
    geometry=gpd.points_from_xy(df_lojas["longitude"], df_lojas["latitude"]),
    crs="EPSG:4326",
)

gdf_concorrentes = gpd.GeoDataFrame(
    df_concorrentes,
    geometry=gpd.points_from_xy(
        df_concorrentes["longitude"], df_concorrentes["latitude"]
    ),
    crs="EPSG:4326",
)

print(
    f"Base carregada: {len(gdf_municipios)} municípios oficiais do Estado de Sergipe!"
)
print(
    gdf_municipios[
        ["cod_ibge", "nome_municipio", "populacao", "pib_per_capita"]
    ].head(5)
)

# %% [01.4] Conferir visualmente a distribuição das bases antes das análises.
# 01.4. Conferir visualmente a distribuição das bases antes das análises.
fig, ax = plt.subplots(figsize=(13, 9))
gdf_municipios.plot(
    ax=ax,
    color="whitesmoke",
    edgecolor="silver",
    linewidth=0.8,
    label="Municípios (IBGE)",
)
gdf_rodovias.plot(
    ax=ax,
    color="black",
    linewidth=2.5,
    linestyle="-",
    label="Eixo Rodoviário (BR-101 / BR-235)",
)
gdf_lojas_atuais.plot(
    ax=ax,
    color="blue",
    marker="o",
    markersize=120,
    edgecolor="white",
    label="Nossas Filiais",
)
gdf_concorrentes.plot(
    ax=ax,
    color="red",
    marker="X",
    markersize=120,
    edgecolor="yellow",
    label="Concorrentes",
)

ax.set_title(
    "SERGIPE: MALHA MUNICIPAL OFICIAL COM PONTOS COMERCIAIS (EPSG:4326)",
    fontsize=13,
    fontweight="bold",
    pad=12,
)
ax.set_xlabel("Longitude (°)")
ax.set_ylabel("Latitude (°)")
ax.legend(loc="lower left", frameon=True)
plt.tight_layout()
plt.show()

# %% [01.5] RECORTE ESPACIAL E VISUALIZAÇÃO — ARACAJU

COD_ARACAJU = 2800308

# 1. Selecionar o limite municipal de Aracaju
gdf_aracaju = gdf_municipios[gdf_municipios["cod_ibge"] == COD_ARACAJU].copy()

if gdf_aracaju.empty:
    raise ValueError("Aracaju não foi encontrado na malha municipal.")

# 2. Padronizar o sistema de coordenadas
gdf_aracaju = gdf_aracaju.to_crs(epsg=4326)
gdf_rodovias_4326 = gdf_rodovias.to_crs(epsg=4326)
gdf_lojas_4326 = gdf_lojas_atuais.to_crs(epsg=4326)
gdf_concorrentes_4326 = gdf_concorrentes.to_crs(epsg=4326)

# 3. Obter a geometria do município
limite_aracaju = gdf_aracaju.geometry.union_all()

# 4. Recortar rodovias e selecionar pontos dentro do município
gdf_rodovias_aracaju = gpd.clip(gdf_rodovias_4326, gdf_aracaju)

gdf_lojas_aracaju = gdf_lojas_4326[
    gdf_lojas_4326.geometry.within(limite_aracaju)
].copy()

gdf_concorrentes_aracaju = gdf_concorrentes_4326[
    gdf_concorrentes_4326.geometry.within(limite_aracaju)
].copy()

# 5. Plot exclusivo de Aracaju
fig, ax = plt.subplots(figsize=(12, 12))

gdf_aracaju.plot(
    ax=ax,
    color="#F2F2F2",
    edgecolor="black",
    linewidth=1.5,
    label="Limite municipal",
)

gdf_rodovias_aracaju.plot(ax=ax, color="gray", linewidth=1.2, label="Rodovias")

gdf_lojas_aracaju.plot(
    ax=ax,
    color="blue",
    marker="o",
    markersize=65,
    edgecolor="white",
    linewidth=0.7,
    label="Lojas próprias",
)

gdf_concorrentes_aracaju.plot(
    ax=ax,
    color="red",
    marker="X",
    markersize=65,
    edgecolor="white",
    linewidth=0.7,
    label="Concorrentes",
)

# 6. Ajustar enquadramento do mapa
xmin, ymin, xmax, ymax = gdf_aracaju.total_bounds
margem_x = (xmax - xmin) * 0.08
margem_y = (ymax - ymin) * 0.08

ax.set_xlim(xmin - margem_x, xmax + margem_x)
ax.set_ylim(ymin - margem_y, ymax + margem_y)

ax.set_title(
    "ARACAJU — DISTRIBUIÇÃO ESPACIAL DAS UNIDADES COMERCIAIS",
    fontsize=13,
    fontweight="bold",
    pad=15,
)

ax.set_xlabel("Longitude")
ax.set_ylabel("Latitude")
ax.legend(loc="best")
ax.set_aspect("equal")

plt.tight_layout()
plt.show()

# 7. Resumo do recorte
print("\n--- RECORTE ESPACIAL DE ARACAJU ---")
print(f"Lojas próprias: {len(gdf_lojas_aracaju)}")
print(f"Concorrentes: {len(gdf_concorrentes_aracaju)}")
print(f"Trechos de rodovias: {len(gdf_rodovias_aracaju)}")

#############################################################################
# %% [02] PROJEÇÃO CARTOGRÁFICA E COMPARAÇÃO DE MALHAS         #
#          SERGIPE EXIGE SIRGAS 2000 UTM FUSO 24S (EPSG:31984)              #
#############################################################################

ponto_loja_1 = gdf_lojas_atuais.geometry.iloc[0]
ponto_loja_2 = gdf_lojas_atuais.geometry.iloc[1]

dist_graus = ponto_loja_1.distance(ponto_loja_2)
print(f"Distância direta em Graus Decimais: {dist_graus:.6f}°")
print(
    "ALERTA: 1 grau de longitude na latitude de Sergipe (~ -10.5°) corresponde a aprox. 109.5 km!"
)

# %% [02.1] Converter as camadas para UTM 24S: distâncias e áreas passam a ser métricas.
# 02.1. Converter as camadas para UTM 24S: distâncias e áreas passam a ser métricas.
# Reprojeção para o Fuso UTM 24S (EPSG:31984)
EPSG_SERGIPE = 31984
gdf_municipios_utm = gdf_municipios.to_crs(epsg=EPSG_SERGIPE)
gdf_lojas_utm = gdf_lojas_atuais.to_crs(epsg=EPSG_SERGIPE)
gdf_concorrentes_utm = gdf_concorrentes.to_crs(epsg=EPSG_SERGIPE)
gdf_rodovias_utm = gdf_rodovias.to_crs(epsg=EPSG_SERGIPE)


# Reprojeção da malha complementar para o mesmo sistema métrico
gdf_malha_2025_utm = gdf_malha_2025.to_crs(epsg=EPSG_SERGIPE)
gdf_malha_2025_wgs = gdf_malha_2025.to_crs(epsg=4326)

# %% [02.2] Sobrepor as malhas para identificar diferenças de limites.
# 02.2. Sobrepor as malhas para identificar diferenças de limites.
# Comparação cartográfica entre as duas malhas
fig, ax = plt.subplots(figsize=(13, 10))

gdf_municipios_utm.boundary.plot(
    ax=ax,
    color="black",
    linewidth=0.8,
    label="Malha municipal IBGE utilizada na análise",
)

gdf_malha_2025_utm.boundary.plot(
    ax=ax,
    color="red",
    linewidth=0.5,
    linestyle="--",
    label="Shapefile municipal 2025",
)

ax.set_title(
    "SERGIPE: COMPARAÇÃO DAS MALHAS MUNICIPAIS\nIBGE x SHAPEFILE 2025",
    fontsize=13,
    fontweight="bold",
)
ax.set_xlabel("Coordenada Este / X (metros)")
ax.set_ylabel("Coordenada Norte / Y (metros)")
ax.legend(loc="lower left")
plt.tight_layout()
plt.show()

ponto_utm_1 = gdf_lojas_utm.geometry.iloc[0]
ponto_utm_2 = gdf_lojas_utm.geometry.iloc[1]
dist_metros = ponto_utm_1.distance(ponto_utm_2)
print(
    f"Distância métrica real no plano UTM 24S: {dist_metros:.2f} metros ({dist_metros/1000:.2f} km)"
)

# %% [02.3] Demonstrar por que buffers devem ser calculados em CRS projetado.
# 02.3. Demonstrar por que buffers devem ser calculados em CRS projetado.
buffer_errado_graus = gdf_lojas_atuais.geometry.iloc[[0]].buffer(0.05)
buffer_correto_metros = gdf_lojas_utm.geometry.iloc[[0]].buffer(5000)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

gpd.GeoSeries(buffer_errado_graus).plot(
    ax=ax1, color="salmon", alpha=0.5, edgecolor="red", linewidth=1.5
)
gdf_lojas_atuais.iloc[[0]].plot(ax=ax1, color="black", markersize=80)
ax1.set_title(
    "ERRO CRÍTICO: BUFFER EM GRAUS DECIMAIS (EPSG:4326)\nNão possui escala métrica uniforme",
    fontsize=11,
    fontweight="bold",
)
ax1.set_xlabel("Longitude (°)")
ax1.set_ylabel("Latitude (°)")

gpd.GeoSeries(buffer_correto_metros).plot(
    ax=ax2, color="lightgreen", alpha=0.5, edgecolor="darkgreen", linewidth=1.5
)
gdf_lojas_utm.iloc[[0]].plot(ax=ax2, color="black", markersize=80)
ax2.set_title(
    "FORMA CORRETA: BUFFER EM SISTEMA PROJETADO (EPSG:31984 - UTM 24S)\nRaio circular exato de 5.000 metros",
    fontsize=11,
    fontweight="bold",
)
ax2.set_xlabel("Coordenada Este / X (Metros)")
ax2.set_ylabel("Coordenada Norte / Y (Metros)")

plt.tight_layout()
plt.show()

#############################################################################
# %% [03] FILTROS TABULARES E ESPACIAIS           #
#############################################################################

# %% [03.1] Selecionar municípios por atributo socioeconômico.
# 03.1. Selecionar municípios por atributo socioeconômico.
# 1. FILTRO TABULAR (Calibrado para Sergipe: PIB per capita > R$ 100.000,00)
filtro_tab_pib = gdf_municipios_utm[
    gdf_municipios_utm["pib_per_capita"] > 100_000.0
]
print(
    f"Filtro Tabular: {len(filtro_tab_pib)} municípios possuem PIB per capita > R$ 100.000,00."
)

# %% [03.2] Identificar municípios que contêm lojas ou cruzam a rede viária.
# 03.2. Identificar municípios que contêm lojas ou cruzam a rede viária.
# 2. FILTROS ESPACIAIS
municipios_com_loja = gdf_municipios_utm[
    gdf_municipios_utm.geometry.apply(
        lambda pol: gdf_lojas_utm.within(pol).any()
    )
]
print(
    f"Filtro Espacial (Contains): {len(municipios_com_loja)} municípios possuem filiais próprias."
)
print(municipios_com_loja[["nome_municipio", "pib_per_capita", "populacao"]])

geometria_rodovia = gdf_rodovias_utm.unary_union
municipios_na_rodovia = gdf_municipios_utm[
    gdf_municipios_utm.intersects(geometria_rodovia)
]
print(
    f"Filtro Espacial (Intersects): {len(municipios_na_rodovia)} municípios são cortados pelo eixo rodoviário."
)

# %% [03.3] Examinar a distribuição da população dos municípios.
# 03.3. Examinar a distribuição da população dos municípios.
fig, ax = plt.subplots(figsize=(10, 5))

sns.histplot(
    data=gdf_municipios_utm,
    x="populacao",
    kde=True,
    color="darkcyan",
    bins=15,
    log_scale=True,
    ax=ax,
)

ax.set_title(
    "Distribuição da População dos Municípios de Sergipe",
    fontsize=13,
    fontweight="bold",
)

ax.set_xlabel("População (habitantes) - escala logarítmica")
ax.set_ylabel("Quantidade de municípios")

ax.grid(axis="y", linestyle="--", alpha=0.3)

plt.tight_layout()
plt.show()

#############################################################################
# %% [04] OPERAÇÕES ESPACIAIS AVANÇADAS                         #
#############################################################################

# %% [04.1] Recortar a rede viária pelo limite do estado.
# 04.1. Recortar a rede viária pelo limite do estado.
# 1. RECORTE ESPACIAL (CLIP)
mascara_estado = gdf_municipios_utm.unary_union
rodovias_clipadas = gpd.clip(gdf_rodovias_utm, mascara_estado)
rodovias_clipadas["extensao_real_km"] = (
    rodovias_clipadas.geometry.length / 1000.0
)
print("--- REDE VIÁRIA APÓS CLIP ---")
print(rodovias_clipadas[["nome_rodovia", "extensao_real_km"]])

# %% [04.2] Agrupar municípios por microrregião e somar a população.
# 04.2. Agrupar municípios por microrregião e somar a população.
# 2. DISSOLVE POR MICRORREGIÕES DE SERGIPE
gdf_microrregioes = gdf_municipios_utm.dissolve(
    by="microrregiao", aggfunc={"populacao": "sum"}
)
gdf_microrregioes["area_total_km2"] = (
    gdf_microrregioes.geometry.area / 1000000.0
)
print(
    f"\n--- DISSOLVE: {len(gdf_municipios_utm)} municípios fundidos em {len(gdf_microrregioes)} microrregiões ---"
)
print(gdf_microrregioes[["populacao", "area_total_km2"]].head(5))

# %% [04.3] Criar áreas de influência de 15 km ao redor das lojas.
# 04.3. Criar áreas de influência de 15 km ao redor das lojas.
# 3. ZONAS DE INFLUÊNCIA (BUFFERS DE 15 KM)
gdf_buffers_15km = gdf_lojas_utm.copy()
gdf_buffers_15km["geometry"] = gdf_lojas_utm.geometry.buffer(15000)

# %% [04.4] Cruzar os buffers com os municípios para medir a área interceptada.
# 04.4. Cruzar os buffers com os municípios para medir a área interceptada.
# 4. OVERLAY (SOBREPOSIÇÃO TOPOLÓGICA)
gdf_overlay_cobertura = gpd.overlay(
    gdf_municipios_utm, gdf_buffers_15km, how="intersection"
)
gdf_overlay_cobertura["area_atendida_km2"] = (
    gdf_overlay_cobertura.geometry.area / 1000000.0
)

# %% [04.5] Visualizar o resultado do Clip e do Dissolve.
# 04.5. Visualizar o resultado do Clip e do Dissolve.
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

gdf_municipios_utm.plot(ax=ax1, color="whitesmoke", edgecolor="silver")
rodovias_clipadas.plot(
    ax=ax1, color="navy", linewidth=3, label="Rodovia Recortada (Clip)"
)
ax1.set_title(
    "RECORTE ESPACIAL (CLIP)\nRodovias contidas em Sergipe",
    fontsize=11,
    fontweight="bold",
)
ax1.legend(loc="lower left")

gdf_microrregioes.plot(
    column="populacao",
    cmap="Blues",
    edgecolor="black",
    linewidth=1.2,
    ax=ax2,
    legend=True,
    scheme="quantiles",
    legend_kwds={"title": "População (Quantis)"},
)
ax2.set_title(
    "AGREGAÇÃO ESPACIAL (DISSOLVE)\nPolígonos fundidos por Microrregiões de Sergipe",
    fontsize=11,
    fontweight="bold",
)
plt.tight_layout()
plt.show()

#############################################################################
# %% [05] DADOS MATRICIAIS (RASTER) E ESTATÍSTICAS               #
#############################################################################
caminho_raster_real = os.path.join(pasta_dados, "temperatura_real_nasa.npy")
caminho_meta_raster = os.path.join(pasta_dados, "temperatura_meta_nasa.json")

matriz_temperatura = np.load(caminho_raster_real)
with open(caminho_meta_raster, "r", encoding="utf-8") as f:
    meta_raster = json.load(f)

nrows = meta_raster["nrows"]
ncols = meta_raster["ncols"]
lon_min = meta_raster["lon_min"]
lon_max = meta_raster["lon_max"]
lat_min = meta_raster["lat_min"]
lat_max = meta_raster["lat_max"]

res_x = (lon_max - lon_min) / (ncols - 1)
res_y = (lat_max - lat_min) / (nrows - 1)
transform_afim = from_origin(lon_min, lat_max, res_x, res_y)

print("--- MATRIZ RASTER REAL DA NASA CARREGADA (SERGIPE) ---")
print(f"Resolução da Grade: {res_x:.4f}° Lon x {res_y:.4f}° Lat")
print(f"Dimensões da Matriz: {nrows} linhas x {ncols} colunas")

mascara_validos = matriz_temperatura != -9999.0
media_correta = matriz_temperatura[mascara_validos].mean()
print(f"Média real após mascarar NoData: {media_correta:.2f} °C")

# %% [05.1] Calcular uma média raster aproximada por município usando a janela
# 05.1. Calcular uma média raster aproximada por município usando a janela
# retangular do polígono (sem máscara exata de recorte da geometria).
# Estatísticas Zonais Municipais
medias_municipais_raster = []
for poligono in gdf_municipios.geometry:
    bx_min, by_min, bx_max, by_max = poligono.bounds
    col_ini = max(0, int((bx_min - transform_afim.c) / transform_afim.a))
    col_fim = min(
        ncols, int((bx_max - transform_afim.c) / transform_afim.a) + 1
    )
    lin_ini = max(0, int((transform_afim.f - by_max) / abs(transform_afim.e)))
    lin_fim = min(
        nrows, int((transform_afim.f - by_min) / abs(transform_afim.e)) + 1
    )

    janela = matriz_temperatura[lin_ini:lin_fim, col_ini:col_fim]
    janela_valida = janela[janela != -9999.0]
    medias_municipais_raster.append(
        np.round(np.mean(janela_valida), 2)
        if len(janela_valida) > 0
        else np.round(media_correta, 2)
    )

gdf_municipios_utm["temperatura_media_superficie"] = medias_municipais_raster
gdf_municipios["temperatura_media_superficie"] = medias_municipais_raster

# %% [05.2] Extrair o valor do pixel correspondente à localização de cada loja.
# 05.2. Extrair o valor do pixel correspondente à localização de cada loja.
# Amostragem Pontual nas Lojas
temp_lojas = []
for ponto in gdf_lojas_atuais.geometry:
    c_p = min(
        ncols - 1, max(0, int((ponto.x - transform_afim.c) / transform_afim.a))
    )
    l_p = min(
        nrows - 1,
        max(0, int((transform_afim.f - ponto.y) / abs(transform_afim.e))),
    )
    val_pixel = matriz_temperatura[l_p, c_p]
    temp_lojas.append(
        np.round(val_pixel, 2) if val_pixel != -9999.0 else media_correta
    )

gdf_lojas_utm["temperatura_pixel"] = temp_lojas

# %% [05.3] Visualizar o raster e sua relação espacial com municípios e lojas.
# 05.3. Visualizar o raster e sua relação espacial com municípios e lojas.
fig, ax = plt.subplots(figsize=(11, 8))
matriz_plotagem = np.where(
    matriz_temperatura == -9999.0, np.nan, matriz_temperatura
)

im = ax.imshow(
    matriz_plotagem,
    cmap="YlOrRd",
    extent=[lon_min, lon_max, lat_min, lat_max],
    origin="upper",
    alpha=0.85,
)
gdf_municipios.boundary.plot(ax=ax, color="black", linewidth=0.7, alpha=0.8)
gdf_lojas_atuais.plot(
    ax=ax,
    color="blue",
    marker="o",
    markersize=120,
    edgecolor="white",
    linewidth=1.2,
    label="Filiais Próprias",
)
cbar = plt.colorbar(im, ax=ax, fraction=0.03, pad=0.04)
cbar.set_label("Temperatura Média Anual Real (°C) - NASA POWER", fontsize=11)
ax.set_title(
    "SERGIPE: CLIMATOLOGIA REAL (NASA POWER) COM MALHA DO IBGE",
    fontsize=13,
    fontweight="bold",
    pad=12,
)
ax.set_xlabel("Longitude (°)")
ax.set_ylabel("Latitude (°)")
ax.legend(loc="lower left", frameon=True)
plt.tight_layout()
plt.show()

#############################################################################
# %% [06] ANÁLISE EXPLORATÓRIA DE DADOS ESPACIAIS (AEE)         #
#############################################################################
gdf_municipios_utm["area_oficial_km2"] = (
    gdf_municipios_utm.geometry.area / 1000000.0
)

# %% [06.1] Construir indicadores observados a partir das lojas e da população.
# 06.1. Construir indicadores observados a partir das lojas e da população.
# Contagem observada de filiais próprias por município.
lojas_municipios = gpd.sjoin(
    gdf_lojas_utm[["geometry"]].copy(),
    gdf_municipios_utm[["cod_ibge", "geometry"]].copy(),
    how="left",
    predicate="within",
)

contagem_filiais = (
    lojas_municipios.dropna(subset=["cod_ibge"])
    .groupby("cod_ibge")
    .size()
    .rename("filiais_proprias")
)

gdf_municipios_utm = gdf_municipios_utm.merge(
    contagem_filiais, on="cod_ibge", how="left"
)
gdf_municipios_utm["filiais_proprias"] = (
    gdf_municipios_utm["filiais_proprias"].fillna(0).astype(int)
)

# Potencial demográfico: população total e população em municípios sem filial.
# A segunda métrica destaca mercados sem presença própria, sem dividir pela população.
gdf_municipios_utm["populacao_sem_filial"] = np.where(
    gdf_municipios_utm["filiais_proprias"] == 0,
    gdf_municipios_utm["populacao"],
    0,
)

gdf_municipios_utm["densidade_populacional"] = (
    gdf_municipios_utm["populacao"] / gdf_municipios_utm["area_oficial_km2"]
)

print("\n--- INDICADORES OBSERVADOS POR MUNICÍPIO ---")
print(
    gdf_municipios_utm[
        [
            "nome_municipio",
            "populacao",
            "filiais_proprias",
            "populacao_sem_filial",
        ]
    ]
    .sort_values("populacao", ascending=False)
    .head(10)
)

# Gráficos: presença de filiais, população total e mercado sem filial.
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(22, 6))

gdf_municipios_utm.plot(
    column="filiais_proprias",
    cmap="Blues",
    legend=True,
    edgecolor="gray",
    linewidth=0.5,
    ax=ax1,
)
ax1.set_title(
    "FILIAIS PRÓPRIAS POR MUNICÍPIO\n(Contagem observada no dataset)",
    fontsize=11,
    fontweight="bold",
)
ax1.axis("off")

gdf_municipios_utm.plot(
    column="populacao",
    cmap="YlOrRd",
    legend=True,
    edgecolor="gray",
    linewidth=0.5,
    ax=ax2,
    legend_kwds={"label": "Habitantes", "shrink": 0.75},
)
ax2.set_title(
    "POPULAÇÃO TOTAL POR MUNICÍPIO\n(Tamanho do mercado potencial)",
    fontsize=11,
    fontweight="bold",
)
ax2.axis("off")

gdf_municipios_utm.plot(
    column="populacao_sem_filial",
    cmap="Oranges",
    legend=True,
    edgecolor="gray",
    linewidth=0.5,
    ax=ax3,
    legend_kwds={
        "label": "Habitantes em municípios sem filial",
        "shrink": 0.75,
    },
)
ax3.set_title(
    "POPULAÇÃO EM MUNICÍPIOS SEM FILIAL\n(Indicação de mercado ainda não atendido)",
    fontsize=11,
    fontweight="bold",
)
ax3.axis("off")
plt.tight_layout()
plt.show()

#############################################################################
# %% [07] AUTOCORRELAÇÃO ESPACIAL (MORAN E LISA)                #
#############################################################################
# Esta etapa avalia se municípios com valores semelhantes de PIB per capita
# tendem a estar próximos espacialmente. A matriz Queen considera vizinhos
# que compartilham uma aresta ou um vértice.

# %% [07.1] Construir a matriz de pesos espaciais pelo critério Queen.
# 07.1. Construir a matriz de pesos espaciais pelo critério Queen.
w_rainha = libpysal.weights.Queen.from_dataframe(gdf_municipios_utm)
w_rainha.transform = "R"

print("\n--- DIAGNÓSTICO DA MATRIZ DE PESOS ESPACIAIS W (SERGIPE) ---")
print(f"Quantidade de municípios avaliados: {w_rainha.n}")
print(
    f"Média de municípios vizinhos por feição: {w_rainha.mean_neighbors:.2f}"
)
if len(w_rainha.islands) > 0:
    print(
        "Municípios sem vizinhos na matriz Queen:",
        list(w_rainha.islands),
    )

# %% [07.2] Calcular o I de Moran Global para o PIB per capita.
# 07.2. Calcular o I de Moran Global para o PIB per capita.
# O teste verifica a existência de autocorrelação espacial no conjunto do estado.
moran_global = Moran(gdf_municipios_utm["pib_per_capita"], w_rainha)

print("\n--- TESTE ESTATÍSTICO: I DE MORAN GLOBAL ---")
print(f"Estatística I de Moran: {moran_global.I:.4f}")
print(f"P-valor (Monte Carlo): {moran_global.p_sim:.5f}")
print(f"Z-score: {moran_global.z_sim:.4f}")

# %% [07.3] Visualizar a vizinhança Queen e o Moran Scatterplot.
# 07.3. Visualizar a vizinhança Queen e o Moran Scatterplot.
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 7))

gdf_municipios_utm.plot(
    ax=ax1, color="whitesmoke", edgecolor="silver", alpha=0.8
)
w_rainha.plot(
    gdf_municipios_utm,
    ax=ax1,
    edge_kws={"color": "navy", "linewidth": 0.8},
    node_kws={"color": "red", "s": 25},
)
ax1.set_title(
    "GRAFO DE VIZINHANÇA W (CRITÉRIO QUEEN - SERGIPE)",
    fontsize=11,
    fontweight="bold",
)
ax1.axis("off")

moran_scatterplot(moran_global, zstandard=True, ax=ax2)
ax2.set_title(
    "MORAN SCATTERPLOT - PIB PER CAPITA (SERGIPE)",
    fontsize=11,
    fontweight="bold",
)
ax2.set_xlabel("PIB per capita padronizado (Z)")
ax2.set_ylabel("Defasagem espacial do PIB (W_z)")
plt.tight_layout()
plt.show()

# %% [07.4] Calcular o Moran Local (LISA) e classificar os agrupamentos.
# 07.4. Calcular o Moran Local (LISA) e classificar os agrupamentos.
# Os quadrantes identificam clusters Alto-Alto/Baixo-Baixo e outliers espaciais.
lisa_local = Moran_Local(
    gdf_municipios_utm["pib_per_capita"], w_rainha, seed=42
)

rotulos_lisa = []
for p, q in zip(lisa_local.p_sim, lisa_local.q):
    if p >= 0.05:
        rotulos_lisa.append("Não Significativo")
    elif q == 1:
        rotulos_lisa.append("Alto-Alto (Hotspot)")
    elif q == 2:
        rotulos_lisa.append("Baixo-Baixo (Coldspot)")
    elif q == 3:
        rotulos_lisa.append("Baixo-Alto (Outlier)")
    elif q == 4:
        rotulos_lisa.append("Alto-Baixo (Outlier)")
    else:
        rotulos_lisa.append("Não Significativo")

gdf_municipios_utm["lisa_cluster"] = rotulos_lisa

# %% [07.5] Mapear os clusters LISA estatisticamente significativos.
# 07.5. Mapear os clusters LISA estatisticamente significativos.
cores_lisa = {
    "Não Significativo": "lightgray",
    "Alto-Alto (Hotspot)": "crimson",
    "Baixo-Baixo (Coldspot)": "royalblue",
    "Baixo-Alto (Outlier)": "lightblue",
    "Alto-Baixo (Outlier)": "salmon",
}

fig, ax = plt.subplots(figsize=(10, 8))
for categoria, cor in cores_lisa.items():
    sub = gdf_municipios_utm[gdf_municipios_utm["lisa_cluster"] == categoria]
    if not sub.empty:
        sub.plot(
            color=cor,
            edgecolor="white",
            linewidth=0.8,
            ax=ax,
            label=categoria,
        )

ax.set_title(
    "MAPA DE CLUSTERS LISA (MORAN LOCAL) - SERGIPE\n"
    "Hotspots, Coldspots e outliers espaciais do PIB per capita",
    fontsize=13,
    fontweight="bold",
)
ax.axis("off")
ax.legend(title="Tipologia LISA (p < 0,05)", loc="lower left")
plt.tight_layout()
plt.show()

# Resumo da quantidade de municípios em cada classe LISA.
print("\n--- DISTRIBUIÇÃO DOS CLUSTERS LISA ---")
print(gdf_municipios_utm["lisa_cluster"].value_counts())


# %% [08] DISTRIBUIÇÃO ESPACIAL DOS PONTOS DE CLIENTES
# Os pontos são agregados em células hexagonais e em uma superfície KDE.

df_pontos_clientes = pd.read_csv(
    "./datasets/observacoes_clientes.csv", encoding="utf-8-sig"
)

colunas_coordenadas = [
    "este_x_m_epsg31984",
    "norte_y_m_epsg31984",
]
df_pontos_clientes[colunas_coordenadas] = df_pontos_clientes[
    colunas_coordenadas
].apply(pd.to_numeric, errors="coerce")
df_pontos_clientes = df_pontos_clientes.dropna(
    subset=colunas_coordenadas
).copy()

clientes_x = df_pontos_clientes["este_x_m_epsg31984"].to_numpy()
clientes_y = df_pontos_clientes["norte_y_m_epsg31984"].to_numpy()

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

hb = ax1.hexbin(clientes_x, clientes_y, gridsize=25, cmap="magma", mincnt=1)
cb = fig.colorbar(hb, ax=ax1)
cb.set_label("Pontos por célula hexagonal")
ax1.set_title(
    "AGREGAÇÃO REGULAR POR HEXBIN (SERGIPE)\n"
    "(Distribuição espacial dos pontos de clientes)",
    fontsize=12,
    fontweight="bold",
)
ax1.set_xlabel("Coordenada Este / X (m)")
ax1.set_ylabel("Coordenada Norte / Y (m)")

sns.kdeplot(
    x=clientes_x,
    y=clientes_y,
    ax=ax2,
    cmap="viridis",
    fill=True,
    levels=14,
    thresh=0.05,
)
ax2.scatter(
    clientes_x[::40],
    clientes_y[::40],
    color="red",
    s=6,
    alpha=0.5,
    label="Pontos de clientes",
)
ax2.set_title(
    "ESTIMAÇÃO DE DENSIDADE DE KERNEL (KDE)\n"
    "(Distribuição espacial dos pontos de clientes)",
    fontsize=12,
    fontweight="bold",
)
ax2.set_xlabel("Coordenada Este / X (m)")
ax2.set_ylabel("Coordenada Norte / Y (m)")
ax2.legend()
plt.tight_layout()
plt.show()

#############################################################################
# %% [09] ESTUDO DE CASO — OPORTUNIDADES DE EXPANSÃO (WHITE SPACES)                 #
#############################################################################
# %% [09.1] Localizar cada filial no município correspondente.
# 09.1. Localizar cada filial no município correspondente.
gdf_lojas_localizadas = gpd.sjoin(
    gdf_lojas_utm,
    gdf_municipios_utm[["cod_ibge", "nome_municipio", "geometry"]],
    how="inner",
    predicate="within",
)

lojas_por_municipio = (
    gdf_lojas_localizadas.groupby("cod_ibge")["id_loja"].count().reset_index()
)
lojas_por_municipio.rename(
    columns={"id_loja": "qtd_filiais_atuais"}, inplace=True
)

gdf_municipios_utm = gdf_municipios_utm.merge(
    lojas_por_municipio, on="cod_ibge", how="left"
)
gdf_municipios_utm["qtd_filiais_atuais"] = (
    gdf_municipios_utm["qtd_filiais_atuais"].fillna(0).astype(int)
)

# %% [09.2] Unificar os buffers de 15 km e calcular a cobertura municipal.
# 09.2. Unificar os buffers de 15 km e calcular a cobertura municipal.
buffer_unificado_lojas = gdf_lojas_utm.geometry.buffer(15000).unary_union

cobertura_pct_lista = []
for poligono in gdf_municipios_utm.geometry:
    if not poligono.intersects(buffer_unificado_lojas):
        cobertura_pct_lista.append(0.0)
    else:
        intersecao = poligono.intersection(buffer_unificado_lojas)
        pct = (intersecao.area / poligono.area) * 100.0
        cobertura_pct_lista.append(np.round(pct, 2))

gdf_municipios_utm["cobertura_lojas_pct"] = cobertura_pct_lista

# %% [09.3] Classificar oportunidades usando medianas de PIB e população
# 09.3. Classificar oportunidades usando medianas de PIB e população
# e baixa cobertura atual. O critério é exploratório e pode ser calibrado.
mediana_pib = gdf_municipios_utm["pib_per_capita"].median()
mediana_pop = gdf_municipios_utm["populacao"].median()

gdf_municipios_utm["prioridade_expansao"] = (
    (gdf_municipios_utm["pib_per_capita"] >= mediana_pib)
    & (gdf_municipios_utm["populacao"] >= mediana_pop)
    & (gdf_municipios_utm["cobertura_lojas_pct"] < 20.0)
)

print("\n--- MUNICÍPIOS PRIORITÁRIOS PARA EXPANSÃO EM SERGIPE ---")
municipios_alvo = gdf_municipios_utm[
    gdf_municipios_utm["prioridade_expansao"]
].sort_values(by="populacao", ascending=False)
print(
    municipios_alvo[
        [
            "nome_municipio",
            "populacao",
            "pib_per_capita",
            "cobertura_lojas_pct",
        ]
    ].head(8)
)

fig, ax = plt.subplots(figsize=(14, 9))

gdf_municipios_utm.plot(
    column="pib_per_capita",
    cmap="Greys",
    alpha=0.35,
    edgecolor="silver",
    ax=ax,
    legend=True,
    scheme="quantiles",
    legend_kwds={"title": "PIB per capita (Quantis)"},
)
gpd.GeoSeries([buffer_unificado_lojas], crs=f"EPSG:{EPSG_SERGIPE}").plot(
    ax=ax,
    color="blue",
    alpha=0.15,
    edgecolor="blue",
    linestyle="--",
    label="Cobertura Atual (15 km)",
)
municipios_alvo.boundary.plot(
    ax=ax,
    color="red",
    linewidth=2.5,
    linestyle="-",
    label="Oportunidade (White Space)",
)
gdf_lojas_utm.plot(
    ax=ax,
    color="blue",
    marker="o",
    markersize=130,
    edgecolor="white",
    label="Nossa Filial",
)
gdf_concorrentes_utm.plot(
    ax=ax,
    color="black",
    marker="X",
    markersize=130,
    edgecolor="yellow",
    label="Concorrente",
)

for _, reg in municipios_alvo.head(5).iterrows():
    c = reg.geometry.centroid
    ax.text(
        c.x,
        c.y,
        reg["nome_municipio"],
        fontsize=9,
        ha="center",
        va="center",
        color="darkred",
        fontweight="bold",
    )

ax.set_title(
    "SERGIPE: ONDE EXPANDIR NOVAS LOJAS? (WHITE SPACES DE MERCADO)",
    fontsize=13,
    fontweight="bold",
    pad=15,
)
ax.axis("off")
ax.legend(loc="lower left", frameon=True)
plt.tight_layout()
plt.show()

#############################################################################
# %% [10] MAPAS INTERATIVOS — FOLIUM E PLOTLY                        #
#############################################################################
gdf_municipios_wgs = gdf_municipios_utm.to_crs(epsg=4326)
gdf_lojas_wgs = gdf_lojas_utm.to_crs(epsg=4326)
gdf_conc_wgs = gdf_concorrentes_utm.to_crs(epsg=4326)
gdf_buffers_wgs = gpd.GeoDataFrame(
    geometry=[buffer_unificado_lojas], crs=f"EPSG:{EPSG_SERGIPE}"
).to_crs(epsg=4326)

centro_lat = gdf_municipios_wgs.geometry.centroid.y.mean()
centro_lon = gdf_municipios_wgs.geometry.centroid.x.mean()

# %% [10.1] Construir e salvar o mapa HTML com camadas ativáveis.
# 10.1. Construir e salvar o mapa HTML com camadas ativáveis.
# Folium
url_tile_esri = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"
atribuicao_esri = "Tiles &copy; Esri &mdash; Source: Esri, DeLorme, NAVTEQ"

mapa_dinamico_folium = folium.Map(
    location=[centro_lat, centro_lon],
    zoom_start=9,
    tiles=url_tile_esri,
    attr=atribuicao_esri,
)


# Camada complementar: limites municipais do shapefile 2025
grupo_malha_2025 = folium.FeatureGroup(
    name="Malha Municipal Complementar 2025", show=False
)

colunas_tooltip_2025 = [
    coluna
    for coluna in gdf_malha_2025_wgs.columns
    if coluna != gdf_malha_2025_wgs.geometry.name
][:3]

config_geojson_2025 = {
    "name": "Limites Municipais 2025",
    "style_function": lambda feature: {
        "fillColor": "orange",
        "color": "darkorange",
        "weight": 1.2,
        "fillOpacity": 0.05,
    },
}

if colunas_tooltip_2025:
    config_geojson_2025["tooltip"] = folium.GeoJsonTooltip(
        fields=colunas_tooltip_2025, sticky=True
    )

folium.GeoJson(gdf_malha_2025_wgs.to_json(), **config_geojson_2025).add_to(
    grupo_malha_2025
)

grupo_malha_2025.add_to(mapa_dinamico_folium)

folium.GeoJson(
    gdf_buffers_wgs.to_json(),
    name="Área de Cobertura Atual (15 km)",
    style_function=lambda x: {
        "fillColor": "#0055ff",
        "color": "#0022aa",
        "weight": 1.8,
        "fillOpacity": 0.15,
        "dashArray": "4, 4",
    },
).add_to(mapa_dinamico_folium)

grupo_filiais = folium.FeatureGroup(name="Nossas Filiais").add_to(
    mapa_dinamico_folium
)
for _, reg in gdf_lojas_wgs.iterrows():
    folium.Marker(
        location=[reg.geometry.y, reg.geometry.x],
        popup=f"<b>{reg['nome']}</b><br>Faturamento: R$ {reg['faturamento_mensal_k']}k",
        tooltip=reg["nome"],
        icon=folium.Icon(color="blue", icon="shopping-cart", prefix="fa"),
    ).add_to(grupo_filiais)

grupo_concorrencia = folium.FeatureGroup(name="Concorrentes").add_to(
    mapa_dinamico_folium
)
for _, reg in gdf_conc_wgs.iterrows():
    folium.CircleMarker(
        location=[reg.geometry.y, reg.geometry.x],
        radius=6,
        popup=f"Concorrente: {reg['bandeira']} ({reg['porte']})",
        color="red",
        fill=True,
        fill_color="red",
        fill_opacity=0.8,
    ).add_to(grupo_concorrencia)

municipios_alvo_wgs = gdf_municipios_wgs[
    gdf_municipios_wgs["prioridade_expansao"]
]
folium.GeoJson(
    municipios_alvo_wgs.to_json(),
    name="★ Municípios Alvo (White Spaces)",
    style_function=lambda x: {
        "fillColor": "none",
        "color": "#ff0000",
        "weight": 2.5,
        "dashArray": "5, 5",
    },
    tooltip=folium.GeoJsonTooltip(
        fields=[
            "nome_municipio",
            "populacao",
            "pib_per_capita",
            "cobertura_lojas_pct",
        ],
        aliases=[
            "Município:",
            "População Real:",
            "PIB per capita (R$):",
            "Cobertura Atual (%):",
        ],
        localize=True,
    ),
).add_to(mapa_dinamico_folium)

folium.LayerControl(collapsed=False).add_to(mapa_dinamico_folium)

caminho_html_folium = os.path.join(
    pasta_dados, "mapa_interativo_ibge_folium.html"
)
mapa_dinamico_folium.save(caminho_html_folium)
print(f"\nMapa Folium salvo em: {os.path.abspath(caminho_html_folium)}")

# %% [10.2] Construir e salvar o mapa interativo de pontos com Plotly.
# 10.2. Construir e salvar o mapa interativo de pontos com Plotly.
# Plotly
df_pontos_plotly = pd.concat(
    [
        pd.DataFrame(
            {
                "nome": gdf_lojas_wgs["nome"],
                "tipo": "Filial Própria",
                "lat": gdf_lojas_wgs.geometry.y,
                "lon": gdf_lojas_wgs.geometry.x,
                "faturamento_k": gdf_lojas_wgs["faturamento_mensal_k"],
            }
        ),
        pd.DataFrame(
            {
                "nome": gdf_conc_wgs["bandeira"],
                "tipo": "Concorrente",
                "lat": gdf_conc_wgs.geometry.y,
                "lon": gdf_conc_wgs.geometry.x,
                "faturamento_k": 0.0,
            }
        ),
    ],
    ignore_index=True,
)

fig_plotly = px.scatter_map(
    df_pontos_plotly,
    lat="lat",
    lon="lon",
    color="tipo",
    hover_name="nome",
    hover_data={
        "tipo": True,
        "lat": False,
        "lon": False,
        "faturamento_k": True,
    },
    color_discrete_map={"Filial Própria": "blue", "Concorrente": "red"},
    zoom=8.2,
    center={"lat": centro_lat, "lon": centro_lon},
    map_style="carto-positron",
    title="SERGIPE: MAPA INTERATIVO PLOTLY",
)
fig_plotly.update_layout(margin={"r": 0, "t": 40, "l": 0, "b": 0})
caminho_html_plotly = os.path.join(
    pasta_dados, "mapa_interativo_ibge_plotly.html"
)
fig_plotly.write_html(caminho_html_plotly)
print(f"Mapa Plotly salvo em: {os.path.abspath(caminho_html_plotly)}")


# ============================================================================
# FIM DO SCRIPT
# Arquivos HTML gerados:
# - datasets/mapa_interativo_ibge_folium.html
# - datasets/mapa_interativo_ibge_plotly.html
# ============================================================================
