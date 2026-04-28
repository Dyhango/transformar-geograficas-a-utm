import streamlit as st
import geopandas as gpd
import os
import zipfile

st.set_page_config(page_title="Conversor GIS Pro", layout="centered")
st.title("🌍 Conversor GIS Profesional")

# 1. Configuración de Zona
zona = st.selectbox("Selecciona la Zona UTM:", ["17S", "18S", "19S"])
epsg_psad = {"17S": "24891", "18S": "24891", "19S": "24891"} 
epsg_wgs = {"17S": "32717", "18S": "32718", "19S": "32719"}

uploaded_files = st.file_uploader("Sube los archivos de tu SHP (SHP, DBF, SHX, PRJ)", accept_multiple_files=True)

if st.button("Procesar Archivos"):
    if uploaded_files:
        # Limpieza previa
        for f in uploaded_files:
            with open(f.name, "wb") as buffer: buffer.write(f.getvalue())
        
        shp_file = [f.name for f in uploaded_files if f.name.endswith(".shp")][0]
        gdf = gpd.read_file(shp_file)
        
        # 2. Procesamiento
        # Forzamos entrada como Geográficas PSAD56 (EPSG:4248)
        gdf = gdf.set_crs("EPSG:4248", allow_override=True)
        
        # Proyección a UTM PSAD
        gdf_utm_psad = gdf.to_crs(f"EPSG:{epsg_psad[zona]}")
        
        # Transformación a UTM WGS84
        gdf_utm_wgs84 = gdf_utm_psad.to_crs(f"EPSG:{epsg_wgs[zona]}")
        
        # 3. Guardado de archivos
        gdf_utm_psad.to_file("UTM_PSAD56.shp")
        gdf_utm_wgs84.to_file("UTM_WGS84.shp")
        gdf_utm_wgs84.to_file("Para_AutoCAD.dxf", driver="DXF")
        
        # 4. Creación de ZIPs para mantener tablas de atributos
        def zip_shapefile(base_name, zip_name):
            with zipfile.ZipFile(zip_name, 'w') as zipf:
                for ext in ['.shp', '.dbf', '.shx', '.prj']:
                    if os.path.exists(base_name + ext):
                        zipf.write(base_name + ext)
        
        zip_shapefile("UTM_PSAD56", "UTM_PSAD56.zip")
        zip_shapefile("UTM_WGS84", "UTM_WGS84.zip")
        
        st.success("¡Transformación finalizada con éxito!")
        
        # 5. Botones de descarga
        with open("UTM_PSAD56.zip", "rb") as f: 
            st.download_button("Descargar PSAD56 (Completo)", f, "UTM_PSAD56.zip")
        with open("UTM_WGS84.zip", "rb") as f: 
            st.download_button("Descargar WGS84 (Completo)", f, "UTM_WGS84.zip")
        with open("Para_AutoCAD.dxf", "rb") as f:
            st.download_button("Descargar para AutoCAD (.dxf)", f, "AutoCAD_Layout.dxf")
    else:
        st.error("Por favor, sube los archivos necesarios.")
