import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

# =====================================================
# CONFIGURACION
# =====================================================
st.set_page_config(
    page_title="Dashboard Comercial Tigo Business",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard Delivery 📊")

# =====================================================
# CARGA DEL ARCHIVO
# =====================================================
archivo = st.file_uploader(
    "Seleccione el archivo Excel",
    type=["xlsx"]
)

if archivo is None:
    st.stop()

# =====================================================
# LEER EXCEL
# =====================================================
df_fijos = pd.read_excel(
    archivo,
    sheet_name="data Fijos"
)

# Volver al inicio del archivo
archivo.seek(0)

df_digital = pd.read_excel(
    archivo,
    sheet_name="data Digital"
)

# Crear columna tipo
df_fijos["TIPO"] = "Fijos"
df_digital["TIPO"] = "Digital"

# Unir
df = pd.concat(
    [df_fijos, df_digital],
    ignore_index=True
)

# =====================================================
# LIMPIEZA
# =====================================================
df.columns = df.columns.str.strip()

if "STATUS_SEGUIMIENTO" in df.columns:
    df["STATUS_SEGUIMIENTO"] = (
        df["STATUS_SEGUIMIENTO"]
        .astype(str)
        .str.upper()
        .str.strip()
    )

# =====================================================
# FECHA
# =====================================================
columna_fecha = None

for c in [
    "FECHA",
    "FECHA_VENTA",
    "FECHA_INGRESO",
    "FECHA_SOLICITUD"
]:
    if c in df.columns:
        columna_fecha = c
        break

if columna_fecha:

    df[columna_fecha] = pd.to_datetime(
        df[columna_fecha],
        errors="coerce"
    )

    df["AÑO"] = df[columna_fecha].dt.year
    df["MES"] = (
        df[columna_fecha]
        .dt.month_name()
    )

# =====================================================
# FILTROS
# =====================================================
st.sidebar.header("Filtros")

# Tipo
tipo = st.sidebar.multiselect(
    "Tipo de Servicio",
    sorted(df["TIPO"].dropna().unique())
)

if tipo:
    df = df[df["TIPO"].isin(tipo)]

# Gerente
if "GERENTE_CARTERA" in df.columns:

    gerente = st.sidebar.multiselect(
        "Gerente de Cartera",
        sorted(
            df["GERENTE_CARTERA"]
            .dropna()
            .unique()
        )
    )

    if gerente:
        df = df[
            df["GERENTE_CARTERA"]
            .isin(gerente)
        ]

# Coordinacion
for c in [
    "COORDINACION",
    "COORDINACIÓN"
]:
    if c in df.columns:

        coordinacion = st.sidebar.multiselect(
            "Coordinación",
            sorted(
                df[c]
                .dropna()
                .unique()
            )
        )

        if coordinacion:
            df = df[
                df[c]
                .isin(coordinacion)
            ]

        break

# Ejecutivo
if "EJECUTIVO" in df.columns:

    ejecutivo = st.sidebar.multiselect(
        "Ejecutivo",
        sorted(
            df["EJECUTIVO"]
            .dropna()
            .unique()
        )
    )

    if ejecutivo:
        df = df[
            df["EJECUTIVO"]
            .isin(ejecutivo)
        ]

# Cliente
if "CLIENTE" in df.columns:

    cliente = st.sidebar.multiselect(
        "Cliente",
        sorted(
            df["CLIENTE"]
            .dropna()
            .unique()
        )
    )

    if cliente:
        df = df[
            df["CLIENTE"]
            .isin(cliente)
        ]

# Año
if "AÑO" in df.columns:

    anio = st.sidebar.multiselect(
        "Año",
        sorted(
            df["AÑO"]
            .dropna()
            .unique()
        )
    )

    if anio:
        df = df[
            df["AÑO"]
            .isin(anio)
        ]

# Mes
if "MES" in df.columns:

    mes = st.sidebar.multiselect(
        "Mes",
        sorted(
            df["MES"]
            .dropna()
            .unique()
        )
    )

    if mes:
        df = df[
            df["MES"]
            .isin(mes)
        ]

# =====================================================
# ESTADOS
# =====================================================
df_estado = df[
    df["STATUS_SEGUIMIENTO"].isin(
        [
            "RETRASADO",
            "VIGENTE",
            "POSPUESTO",
            "POSPUESTA"
        ]
    )
]

retrasado = df_estado[
    df_estado["STATUS_SEGUIMIENTO"]
    == "RETRASADO"
]

vigente = df_estado[
    df_estado["STATUS_SEGUIMIENTO"]
    == "VIGENTE"
]

pospuesto = df_estado[
    df_estado["STATUS_SEGUIMIENTO"]
    .isin(["POSPUESTO", "POSPUESTA"])
]

# =====================================================
# KPI
# =====================================================
st.subheader("Resumen Ejecutivo")

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric(
        "🔴 OT Retrasadas",
        len(retrasado)
    )
    st.metric(
        "Monto Retrasado",
        f"$ {retrasado['MONTO_VENTA_FINAL'].fillna(0).sum():,.2f}"
    )

with c2:
    st.metric(
        "🟢 OT Vigentes",
        len(vigente)
    )
    st.metric(
        "Monto Vigente",
        f"$ {vigente['MONTO_VENTA_FINAL'].fillna(0).sum():,.2f}"
    )

with c3:
    st.metric(
        "🟡 OT Pospuestas",
        len(pospuesto)
    )
    st.metric(
        "Monto Pospuesto",
        f"$ {pospuesto['MONTO_VENTA_FINAL'].fillna(0).sum():,.2f}"
    )

with c4:
    st.metric(
        "💰 Monto en Riesgo",
        f"$ {retrasado['MONTO_VENTA_FINAL'].fillna(0).sum():,.2f}"
    )

# =====================================================
# RESUMEN
# =====================================================
st.subheader("Resumen por Estado")

resumen = (
    df_estado
    .groupby("STATUS_SEGUIMIENTO")
    .agg(
        OT=("STATUS_SEGUIMIENTO", "count"),
        MONTO=("MONTO_VENTA_FINAL", "sum")
    )
    .reset_index()
)

st.dataframe(
    resumen,
    use_container_width=True
)

fig = px.bar(
    resumen,
    x="STATUS_SEGUIMIENTO",
    y="OT",
    color="STATUS_SEGUIMIENTO",
    text="OT"
)

st.plotly_chart(
    fig,
    use_container_width=True
)

# =====================================================
# GRAFICA DE OT POR AÑO
# =====================================================
if "AÑO" in df_estado.columns:

    st.subheader(
        "📈 OT por Estado y Año"
    )

    grafica_anio = (
        df_estado
        .groupby(
            ["AÑO", "STATUS_SEGUIMIENTO"]
        )
        .size()
        .reset_index(name="OT")
    )

    fig_anio = px.bar(
        grafica_anio,
        x="AÑO",
        y="OT",
        color="STATUS_SEGUIMIENTO",
        barmode="group",
        text="OT",
        title="OT Retrasadas, Vigentes y Pospuestas por Año"
    )

    fig_anio.update_layout(
        xaxis_title="Año",
        yaxis_title="Cantidad de OT",
        legend_title="Estado"
    )

    st.plotly_chart(
        fig_anio,
        use_container_width=True
    )

# =====================================================
# GRAFICA DE MONTO POR AÑO
# =====================================================
if "AÑO" in df_estado.columns:

    st.subheader(
        "💰 Monto por Estado y Año"
    )

    monto_anio = (
        df_estado
        .groupby(
            ["AÑO", "STATUS_SEGUIMIENTO"]
        )
        .agg(
            MONTO=("MONTO_VENTA_FINAL", "sum")
        )
        .reset_index()
    )

    fig_monto = px.bar(
        monto_anio,
        x="AÑO",
        y="MONTO",
        color="STATUS_SEGUIMIENTO",
        barmode="group",
        title="Monto por Estado y Año"
    )

    fig_monto.update_layout(
        xaxis_title="Año",
        yaxis_title="Monto ($)",
        legend_title="Estado"
    )

    st.plotly_chart(
        fig_monto,
        use_container_width=True
    )

# =====================================================
# TOP CLIENTES
# =====================================================
if "CLIENTE" in retrasado.columns:

    st.subheader(
        "🏆 Top 10 Clientes Retrasados"
    )

    top = (
        retrasado
        .groupby("CLIENTE")
        .agg(
            OT=("CLIENTE", "count"),
            MONTO=("MONTO_VENTA_FINAL", "sum")
        )
        .sort_values(
            "OT",
            ascending=False
        )
        .head(10)
        .reset_index()
    )

    st.dataframe(
        top,
        use_container_width=True
    )

# =====================================================
# EXPORTAR
# =====================================================
buffer = BytesIO()

with pd.ExcelWriter(
    buffer,
    engine="openpyxl"
) as writer:

    df_estado.to_excel(
        writer,
        index=False,
        sheet_name="Detalle"
    )

st.download_button(
    "📥 Descargar Detalle",
    data=buffer.getvalue(),
    file_name="Backlog.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# =====================================================
# DETALLE
# =====================================================
st.subheader("Detalle de OT")

st.dataframe(
    df_estado,
    use_container_width=True
)