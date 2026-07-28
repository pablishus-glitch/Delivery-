import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Commercial Intelligence Center",
    page_icon="📊",
    layout="wide"
)

@st.cache_data
def cargar_datos(archivo):
    return pd.read_excel(archivo)

def aplicar_filtros(df):

    st.sidebar.header("🎯 Filtros")

    cliente = st.sidebar.multiselect(
        "Cliente",
        sorted(df["CLIENTE"].dropna().unique())
    )

    producto = st.sidebar.multiselect(
        "Producto",
        sorted(df["PRODUCTO"].dropna().unique())
    )

    estado = st.sidebar.multiselect(
        "Estado",
        sorted(df["ESTADO"].dropna().unique())
    )

    ejecutivo = st.sidebar.multiselect(
        "Ejecutivo Comercial",
        sorted(df["EJECUTIVO_COMERCIAL"].dropna().unique())
    )

    if cliente:
        df = df[df["CLIENTE"].isin(cliente)]

    if producto:
        df = df[df["PRODUCTO"].isin(producto)]

    if estado:
        df = df[df["ESTADO"].isin(estado)]

    if ejecutivo:
        df = df[df["EJECUTIVO_COMERCIAL"].isin(ejecutivo)]

    return df

def obtener_kpis(df):

    clientes = df["CLIENTE"].nunique()
    servicios = len(df)
    mrc = df["MRC_USD"].sum()
    mbf = df["MBF_USD"].sum()

    return clientes, servicios, mrc, mbf

def resumen_clientes(df):

    tabla = (
        df.groupby("CLIENTE")
        .agg(
            SERVICIOS=("CLIENTE","count"),
            MRC_USD=("MRC_USD","sum"),
            MBF_USD=("MBF_USD","sum")
        )
        .reset_index()
    )

    tabla = tabla.sort_values(
        by="MRC_USD",
        ascending=False
    )

    return tabla

# =====================================================
# TOP 10 CLIENTES
# =====================================================

def top_clientes(df):

    top = (
        df.groupby("CLIENTE")["MRC_USD"]
        .sum()
        .reset_index()
        .sort_values("MRC_USD", ascending=False)
        .head(10)
    )

    return top

# =====================================================
# TOP PRODUCTOS
# =====================================================

def top_productos(df):

    productos = (
        df.groupby("PRODUCTO")
        .size()
        .reset_index(name="SERVICIOS")
        .sort_values("SERVICIOS", ascending=False)
    )

    return productos




st.title("📊 Commercial Intelligence Center")
st.caption("Tigo Business")

archivo = st.file_uploader(
    "Seleccione el Cubo Comercial",
    type=["xlsx"]
)

if archivo is None:
    st.stop()

df = cargar_datos(archivo)
df = aplicar_filtros(df)

st.success(f"✅ Cubo cargado correctamente ({len(df):,} registros)")

clientes, servicios, mrc, mbf = obtener_kpis(df)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("👥 Clientes", f"{clientes:,}")

with col2:
    st.metric("📦 Servicios", f"{servicios:,}")

with col3:
    st.metric("💰 MRC USD", f"${mrc:,.2f}")

with col4:
    st.metric("💵 MBF USD", f"${mbf:,.2f}")

# =====================================================
# TOP 10 CLIENTES
# =====================================================

st.subheader("🏆 Top 10 Clientes por MRC")

top = top_clientes(df)

fig = px.bar(
    top,
    x="MRC_USD",
    y="CLIENTE",
    orientation="h",
    text_auto=".2s"
)

fig.update_layout(
    yaxis={"categoryorder": "total ascending"}
)

st.plotly_chart(fig, use_container_width=True)

# =====================================================
# PRODUCTOS MÁS VENDIDOS
# =====================================================

st.subheader("📦 Productos más vendidos")

productos = top_productos(df)

fig = px.bar(
    productos.head(10),
    x="SERVICIOS",
    y="PRODUCTO",
    orientation="h",
    text_auto=True
)

fig.update_layout(
    yaxis={"categoryorder": "total ascending"}
)

st.plotly_chart(fig, use_container_width=True)

# =====================================================
# CONTRATOS PROXIMOS A VENCER
# =====================================================

def contratos_por_vencer(df):

    vencer = (
        df[df["MESES_RESTANTES"] <= 6]
        .sort_values("MESES_RESTANTES")
    )

    return vencer[
        [
            "CLIENTE",
            "PRODUCTO",
            "MRC_USD",
            "MESES_RESTANTES",
            "EJECUTIVO_COMERCIAL"
        ]
    ]

# =====================================================
# RESUMEN DE CLIENTES
# =====================================================

st.subheader("👥 Resumen de Clientes")

tabla_clientes = resumen_clientes(df)

st.dataframe(
    tabla_clientes,
    use_container_width=True,
    hide_index=True
)

# =====================================================
# CONTRATOS PROXIMOS A VENCER
# =====================================================

st.subheader("⏳ Contratos próximos a vencer (6 meses)")

vencer = contratos_por_vencer(df)

st.dataframe(
    vencer,
    use_container_width=True,
    hide_index=True
)
