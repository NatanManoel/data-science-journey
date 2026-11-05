#!/usr/bin/env python
# coding: utf-8

# ANÁLISE ESTATÍSTICA ESPACIAL
# Script: Extração de Dados do IBGE e NASA - SERGIPE (UF 28)

# In[ ]: Importação dos pacotes
import json
import os
import geopandas as gpd
import numpy as np
import pandas as pd
import requests
from shapely.geometry import LineString

print("Iniciando pipeline de dados reais para Sergipe")

# In[ ]: Configurações gerais
pasta_dados = "datasets"
os.makedirs(pasta_dados, exist_ok=True)
codigo_uf = "28"  # Código IBGE de Sergipe

headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}

# In[ ]: 1. Extração da Malha de Municípios do IBGE (GeoJSON)
caminho_malha = os.path.join(pasta_dados, f"malha_ibge_uf_{codigo_uf}.geojson")
url_api_malha = (
    f"https://servicodados.ibge.gov.br/api/v3/malhas/estados/{codigo_uf}"
    f"?intrarregiao=municipio&formato=application/vnd.geo+json&qualidade=intermediaria"
)

if not os.path.exists(caminho_malha):
    print(f"Baixando malha vetorial do IBGE para a UF {codigo_uf}...")
    resposta_malha = requests.get(url_api_malha, headers=headers, timeout=60)
    resposta_malha.raise_for_status()

    with open(caminho_malha, "w", encoding="utf-8") as f:
        f.write(resposta_malha.text)
    print(f"Malha municipal salva em: {caminho_malha}")
else:
    print(f"Malha municipal já existe em: {caminho_malha}")

# In[ ]: 2. Extração dos Nomes e Metadados das Localidades (JSON)
caminho_localidades = os.path.join(
    pasta_dados, f"municipios_ibge_uf_{codigo_uf}.json"
)
url_api_localidades = f"https://servicodados.ibge.gov.br/api/v1/localidades/estados/{codigo_uf}/municipios"

if not os.path.exists(caminho_localidades):
    print("Baixando dados de localidades do IBGE...")
    resposta_localidades = requests.get(
        url_api_localidades, headers=headers, timeout=60
    )
    resposta_localidades.raise_for_status()

    with open(caminho_localidades, "w", encoding="utf-8") as f:
        f.write(resposta_localidades.text)
    print(f"Tabela de localidades salva em: {caminho_localidades}")
else:
    print(f"Tabela de localidades já existe em: {caminho_localidades}")

# In[ ]: 3. Obtenção Direta dos Dados Socioeconômicos Oficiais (SIDRA API)
gdf_temp = gpd.read_file(caminho_malha)
gdf_temp["codarea"] = gdf_temp["codarea"].astype(int)
df_municipios_base = pd.DataFrame({"cod_ibge": gdf_temp["codarea"].unique()})

print("\nConsultando indicadores socioeconômicos reais na API SIDRA...")

# A. População Residente (Censo Demográfico - Tabela 4709, Variável 93, UF 28)
url_pop_sidra = "https://apisidra.ibge.gov.br/values/t/4709/n6/in%20n3%2028/v/93/p/last%201"
resp_pop = requests.get(url_pop_sidra, headers=headers, timeout=60)
resp_pop.raise_for_status()
json_pop = resp_pop.json()

# B. PIB per capita (Contas Regionais - Tabela 5938, Variável 37, UF 28)
url_pib_sidra = "https://apisidra.ibge.gov.br/values/t/5938/n6/in%20n3%2028/v/37/p/last%201"
resp_pib = requests.get(url_pib_sidra, headers=headers, timeout=60)
resp_pib.raise_for_status()
json_pib = resp_pib.json()

# Processamento tabular (primeira linha do SIDRA contém metadados de cabeçalho)
df_pop_real = pd.DataFrame(json_pop[1:])[["D1C", "V"]].rename(
    columns={"D1C": "cod_ibge", "V": "populacao"}
)
df_pib_real = pd.DataFrame(json_pib[1:])[["D1C", "V"]].rename(
    columns={"D1C": "cod_ibge", "V": "pib_per_capita"}
)

df_pop_real["cod_ibge"] = df_pop_real["cod_ibge"].astype(int)
df_pib_real["cod_ibge"] = df_pib_real["cod_ibge"].astype(int)

df_pop_real["populacao"] = pd.to_numeric(
    df_pop_real["populacao"], errors="coerce"
)
df_pib_real["pib_per_capita"] = pd.to_numeric(
    df_pib_real["pib_per_capita"], errors="coerce"
)

# Junção estrita dos dados oficiais
df_indicadores = df_municipios_base.merge(
    df_pop_real, on="cod_ibge", how="left"
).merge(df_pib_real, on="cod_ibge", how="left")

# Cálculo das métricas derivadas a partir dos dados reais
df_indicadores["renda_media_domiciliar"] = np.round(
    1350.0 + (df_indicadores["pib_per_capita"] * 0.040), 2
)
df_indicadores["indice_consumo"] = np.round(
    df_indicadores["pib_per_capita"]
    / df_indicadores["pib_per_capita"].median(),
    3,
)

caminho_csv_indicadores = os.path.join(
    pasta_dados, "indicadores_socioeconomicos_municipios.csv"
)
df_indicadores.to_csv(caminho_csv_indicadores, index=False, encoding="utf-8")
print(
    f"Indicadores oficiais do SIDRA baixados e salvos em: {caminho_csv_indicadores}"
)
print(df_indicadores.head())

# In[ ]: 4. Pontos Comerciais de Varejo (Estudo de Caso Sergipe)
df_lojas = pd.DataFrame(
    {
        "id_loja": [f"FILIAL_{i+1:02d}" for i in range(7)],
        "nome": [
            "Unidade Aracaju Centro",
            "Unidade Aracaju Jardins",
            "Unidade Aracaju Atalaia",
            "Unidade N. Sra. do Socorro",
            "Unidade Itabaiana Centro",
            "Unidade Lagarto",
            "Unidade Estância",
        ],
        "faturamento_mensal_k": [
            520.0,
            780.0,
            640.0,
            410.0,
            460.0,
            380.0,
            350.0,
        ],
        "latitude": [
            -10.9095,
            -10.9472,
            -10.9856,
            -10.8550,
            -10.6850,
            -10.9172,
            -11.2683,
        ],
        "longitude": [
            -37.0504,
            -37.0683,
            -37.0489,
            -37.1261,
            -37.4253,
            -37.6500,
            -37.4383,
        ],
    }
)
caminho_csv_lojas = os.path.join(pasta_dados, "lojas_varejo.csv")
df_lojas.to_csv(caminho_csv_lojas, index=False, encoding="utf-8")
print(f"Lojas salvas em: {caminho_csv_lojas}")

# In[ ]: 5. Pontos de Concorrência
df_concorrentes = pd.DataFrame(
    {
        "id_concorrente": [f"CONC_{i+1:02d}" for i in range(5)],
        "bandeira": [
            "GBarbosa (Cencosud)",
            "Assaí Atacadista",
            "Atacadão",
            "Nunes Peixoto",
            "Mix Mateus",
        ],
        "porte": ["Grande", "Grande", "Grande", "Médio", "Grande"],
        "latitude": [-10.9350, -10.9250, -10.8650, -10.6890, -10.9650],
        "longitude": [-37.0600, -37.0750, -37.1100, -37.4210, -37.0610],
    }
)
caminho_csv_concorrentes = os.path.join(pasta_dados, "concorrentes_varejo.csv")
df_concorrentes.to_csv(caminho_csv_concorrentes, index=False, encoding="utf-8")
print(f"Concorrentes salvos em: {caminho_csv_concorrentes}")

# In[ ]: 6. Rede Viária Estruturante de Sergipe (BR-101 e BR-235)
linha_br101 = LineString(
    [
        (-36.8406, -10.2108),  # Divisa AL / Propriá
        (-37.0200, -10.5800),  # Carmópolis / Japaratuba
        (-37.1261, -10.8550),  # N. Sra. do Socorro
        (-37.2064, -11.0147),  # São Cristóvão
        (-37.4383, -11.2683),  # Estância
        (-37.7500, -11.4700),  # Cristinápolis / Divisa BA
    ]
)

linha_br235 = LineString(
    [
        (-37.0504, -10.9095),  # Aracaju
        (-37.1500, -10.8500),  # Saída Metropolitana
        (-37.4253, -10.6850),  # Itabaiana
    ]
)

gdf_rodovias = gpd.GeoDataFrame(
    {
        "nome_rodovia": ["Eixo BR-101 (Norte-Sul)", "Eixo BR-235 (Agreste)"],
        "tipo": [
            "Rodovia Federal Tronco",
            "Rodovia Federal de Interiorização",
        ],
        "geometry": [linha_br101, linha_br235],
    },
    crs="EPSG:4326",
)
caminho_rodovias = os.path.join(pasta_dados, "rede_viaria.geojson")
gdf_rodovias.to_file(caminho_rodovias, driver="GeoJSON")
print(f"Rede viária salva em: {caminho_rodovias}")

# In[ ]: 7. Extração Direta de Dados Climáticos da NASA POWER API
print("\nConsultando grade climática real na API NASA POWER para Sergipe...")

# Bounding box delimitando o Estado de Sergipe
lat_min, lat_max = -11.8, -9.4
lon_min, lon_max = -38.5, -36.2

caminho_raster_real = os.path.join(pasta_dados, "temperatura_real_nasa.npy")
caminho_meta_raster = os.path.join(pasta_dados, "temperatura_meta_nasa.json")

url_nasa = (
    f"https://power.larc.nasa.gov/api/temporal/climatology/regional"
    f"?latitude-min={lat_min}&latitude-max={lat_max}"
    f"&longitude-min={lon_min}&longitude-max={lon_max}"
    f"&parameters=T2M&community=RE&format=JSON"
)

resp_nasa = requests.get(url_nasa, headers=headers, timeout=60)
resp_nasa.raise_for_status()
dados_nasa = resp_nasa.json()

features = dados_nasa.get("features", [])
print(f"Total de pontos climáticos retornados: {len(features)}")

pontos_grade = []
for f in features:
    lon = f["geometry"]["coordinates"][0]
    lat = f["geometry"]["coordinates"][1]
    t2m_dados = f["properties"]["parameter"]["T2M"]
    temp_anual = t2m_dados.get("ANN", list(t2m_dados.values())[0])

    val_temp = float(temp_anual) if temp_anual != -999.0 else -9999.0
    pontos_grade.append({"lat": lat, "lon": lon, "temp": val_temp})

df_grade = pd.DataFrame(pontos_grade)

lats_unicas = sorted(df_grade["lat"].unique(), reverse=True)
lons_unicas = sorted(df_grade["lon"].unique())

matriz_real = np.full((len(lats_unicas), len(lons_unicas)), fill_value=-9999.0)

lat_idx = {lat: i for i, lat in enumerate(lats_unicas)}
lon_idx = {lon: j for j, lon in enumerate(lons_unicas)}

for _, row in df_grade.iterrows():
    matriz_real[lat_idx[row["lat"]], lon_idx[row["lon"]]] = row["temp"]

np.save(caminho_raster_real, matriz_real)

metadados_raster = {
    "lon_min": float(min(lons_unicas)),
    "lon_max": float(max(lons_unicas)),
    "lat_min": float(min(lats_unicas)),
    "lat_max": float(max(lats_unicas)),
    "nrows": int(len(lats_unicas)),
    "ncols": int(len(lons_unicas)),
}

with open(caminho_meta_raster, "w", encoding="utf-8") as f:
    json.dump(metadados_raster, f)

print("Grade climática da NASA baixada e processada com sucesso!")
print(
    f"Temperatura média real em Sergipe: {matriz_real[matriz_real != -9999.0].mean():.2f} °C"
)
