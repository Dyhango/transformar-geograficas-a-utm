import streamlit as st
import geopandas as gpd
import os
import zipfile

st.title("🌍 Conversor GIS Profesional")

# Configuración
zona = st.selectbox("Selecciona la Zona UTM:", ["17S", "18S", "19S"])
epsg_psad = {"17S": "24891", "18S": "24891", "19S": "24891"} 
epsg_wgs = {"17S": "32717", "18S": "32718", "19S": "32719"}

uploaded_files = st.file_uploader("Sube los archivos de tu SHP (SHP, DBF, SHX, PRJ)", accept_multiple_files=True)

if uploaded_files:
    # Guardar archivos subidos
    for f in uploaded_files:
        with open(f.name, "wb") as buffer: buffer.write(f.getvalue())
    
    shp_file = [f.name for f in uploaded_files if f.name.endswith(".shp")][0]
    
    if st.button("Procesar Archivos"):
        gdf = gpd.read_file(shp_file)
        
        # Procesamiento
        gdf = gdf.set_crs("EPSG:4248", allow_override=True)
        gdf_utm_psad = gdf.to_crs(f"EPSG:{epsg_psad[zona]}")
        gdf_utm_wgs84 = gdf_utm_psad.to_crs(f"EPSG:{epsg_wgs[zona]}")
        
        # Guardar
        gdf_utm_psad.to_file("UTM_PSAD56.shp")
        gdf_utm_wgs84.to_file("UTM_WGS84.shp")
        gdf_utm_wgs84.to_file("Para_AutoCAD.dxf", driver="DXF")
        
        # Empaquetar
        def zip_shapefile(base_name, zip_name):
            with zipfile.ZipFile(zip_name, 'w') as zipf:
                for ext in ['.shp', '.dbf', '.shx', '.prj']:
                    if os.path.exists(base_name + ext):
                        zipf.write(base_name + ext)
        
        zip_shapefile("UTM_PSAD56", "UTM_PSAD56.zip")
        zip_shapefile("UTM_WGS84", "UTM_WGS84.zip")
        
        st.session_state['procesado'] = True

# Mostrar botones de descarga solo si ya se procesó
if 'procesado' in st.session_state:
    st.success("¡Transformación exitosa!")
    with open("UTM_PSAD56.zip", "rb") as f: 
        st.download_button("Descargar PSAD56 ZIP", f, "UTM_PSAD56.zip")
    with open("UTM_WGS84.zip", "rb") as f: 
        st.download_button("Descargar WGS84 ZIP", f, "UTM_WGS84.zip")
    with open("Para_AutoCAD.dxf", "rb") as f:
        st.download_button("Descargar AutoCAD DXF", f, "AutoCAD.dxf")
