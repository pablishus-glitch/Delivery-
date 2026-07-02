import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO
from datetime import datetime

# =====================================================
# CONFIGURACION
# =====================================================
st.set_page_config(
    page_title="Dashboard Comercial Tigo Business",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Dashboard Delivery 📊")

st.caption(
    f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
)
	
# =====================================================
# CARGA DEL ARCHIVO
# =====================================================
archivo = st.file_uploader(
    "Seleccione el archivo Excel",
    type=["xlsx"]
)

archivo_anterior = st.sidebar.file_uploader(
    "📁 Matriz Anterior",
    type=["xlsx"]
)

if archivo is None:
    st.stop()

# =====================================================
# LEER EXCEL
# =====================================================
xls = pd.ExcelFile(archivo)

hoja_fijos = None
hoja_digital = None

for hoja in xls.sheet_names:
    nombre = hoja.lower()

    if "data fijos" in nombre:
        hoja_fijos = hoja

    if "data digital" in nombre:
        hoja_digital = hoja

if hoja_fijos:
    archivo.seek(0)
    df_fijos = pd.read_excel(
        archivo,
        sheet_name=hoja_fijos
    )
    df_fijos["TIPO"] = "Fijos"
else:
    df_fijos = pd.DataFrame()

if hoja_digital:
    archivo.seek(0)
    df_digital = pd.read_excel(
        archivo,
        sheet_name=hoja_digital
    )
    df_digital["TIPO"] = "Digital"
else:
    df_digital = pd.DataFrame()

if df_fijos.empty and df_digital.empty:
    st.error(
        f"No se encontraron hojas de Fijos o Digital.\nHojas encontradas: {xls.sheet_names}"
    )
    st.stop()

df = pd.concat(
    [df_fijos, df_digital],
    ignore_index=True
)

def cargar_matriz(archivo_excel):

    xls_ant = pd.ExcelFile(archivo_excel)

    hoja_fijos = None
    hoja_digital = None

    for hoja in xls_ant.sheet_names:
        nombre = hoja.lower()

        if "data fijos" in nombre:
            hoja_fijos = hoja

        if "data digital" in nombre:
            hoja_digital = hoja

    df_fijos_ant = pd.DataFrame()
    df_digital_ant = pd.DataFrame()

    if hoja_fijos:
        archivo_excel.seek(0)
        df_fijos_ant = pd.read_excel(
            archivo_excel,
            sheet_name=hoja_fijos
        )
        df_fijos_ant["TIPO"] = "Fijos"

    if hoja_digital:
        archivo_excel.seek(0)
        df_digital_ant = pd.read_excel(
            archivo_excel,
            sheet_name=hoja_digital
        )
        df_digital_ant["TIPO"] = "Digital"

    df_ant = pd.concat(
        [df_fijos_ant, df_digital_ant],
        ignore_index=True
    )

    df_ant.columns = df_ant.columns.str.strip()

    if "STATUS_SEGUIMIENTO" in df_ant.columns:
        df_ant["STATUS_SEGUIMIENTO"] = (
            df_ant["STATUS_SEGUIMIENTO"]
            .astype(str)
            .str.upper()
            .str.strip()
        )

    return df_ant

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
# CONSULTING
# =====================================================
consulting = pd.DataFrame()
ot_consulting = 0
monto_consulting = 0

if "NOMBRE_VENTAS_FIJOS" in df.columns:

    consulting = df[
        (df["TIPO"] == "Digital")
        &
        (
            df["NOMBRE_VENTAS_FIJOS"]
            .astype(str)
            .str.upper()
            .str.strip()
            == "SERVICIOS PROFESIONALES CIBERSEGURIDAD"
        )
        &
        (
            df["STATUS_SEGUIMIENTO"]
            .isin(
                [
                    "RETRASADO",
                    "VIGENTE",
                    "POSPUESTO",
                    "POSPUESTA"
                ]
            )
        )
    ].copy()

    ot_consulting = len(consulting)

    monto_consulting = (
        pd.to_numeric(
            consulting["MONTO_VENTA_FINAL"],
            errors="coerce"
        )
        .fillna(0)
        .sum()
    )

    # Eliminar Consulting del dashboard
    df = df.drop(consulting.index)

# =====================================================
# ESTADOS
# =====================================================
#st.write(df.columns.tolist())
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
# DASHBOARD POR GERENTE
# =====================================================
if "GERENTE_CARTERA" in df_estado.columns:

    st.subheader(
        "👥 Dashboard por Gerente"
    )

    gerente_df = (
        df_estado
        .groupby(
            [
                "GERENTE_CARTERA",
                "STATUS_SEGUIMIENTO"
            ]
        )
        .agg(
            OT=("STATUS_SEGUIMIENTO", "count"),
            MONTO=("MONTO_VENTA_FINAL", "sum")
        )
        .reset_index()
    )

    fig_gerente = px.bar(
        gerente_df,
        x="GERENTE_CARTERA",
        y="OT",
        color="STATUS_SEGUIMIENTO",
        barmode="group",
        text="OT",
        title="OT por Gerente y Estado",
        color_discrete_map={
            "RETRASADO": "red",
            "VIGENTE": "green",
            "POSPUESTO": "blue",
            "POSPUESTA": "blue"
        }
    )

    fig_gerente.update_layout(
        xaxis_title="Gerente de Cartera",
        yaxis_title="Cantidad de OT",
        legend_title="Estado"
    )

    st.plotly_chart(
        fig_gerente,
        use_container_width=True
    )
# =====================================================
# DASHBOARD POR COORDINACION
# =====================================================
for col_coord in [
    "COORDINACION",
    "COORDINACIÓN"
]:

    if col_coord in df_estado.columns:

        coord_df = (
            df_estado
            .groupby(
                [col_coord, "STATUS_SEGUIMIENTO"]
            )
            .agg(
                OT=("STATUS_SEGUIMIENTO", "count"),
                MONTO=("MONTO_VENTA_FINAL", "sum")
            )
            .reset_index()
        )

        # Excluir coordinaciones
        coord_df = coord_df[
            ~coord_df[col_coord].isin(
                ["SAC (LQEV)", "WHOLESALE"]
            )
        ]

        fig_coord = px.bar(
            coord_df,
            x=col_coord,
            y="OT",
            color="STATUS_SEGUIMIENTO",
            barmode="group",
            text="OT"
        )

        st.plotly_chart(
            fig_coord,
            use_container_width=True
        )

        break

# =====================================================
# KPI
# =====================================================
def formato_monto(valor):
    if valor >= 1_000_000:
        return f"${valor/1_000_000:.2f}M"
    elif valor >= 1_000:
        return f"${valor/1_000:.1f}K"
    else:
        return f"${valor:,.2f}"

st.subheader("Resumen Ejecutivo")

c1, c2, c3, c4 = st.columns(4)
c5, c6, c7, = st.columns(3)


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
        "🟣 OT Consulting",
        f"{ot_consulting:,}"
    )
    st.metric(
        "Monto Consulting",
        f"$ {monto_consulting:,.2f}"
    )

with c5:
    st.metric(
        "💰 Monto en Riesgo",
        f"$ {retrasado['MONTO_VENTA_FINAL'].fillna(0).sum():,.2f}"
    )

with c6:
    st.metric(
        "📋 Total OT",
        f"{len(df_estado):,}"
    )

with c7:
    porcentaje = 0

    if len(df_estado) > 0:
        porcentaje = (
            len(retrasado)
            / len(df_estado)
        ) * 100

    st.metric(
        "% Retrasadas",
        f"{porcentaje:.1f}%"
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
    resumen.style.format(
        {
            "MONTO": "${:,.2f}"
        }
    ),
    use_container_width=True
)

# =====================================================
# COMPARATIVO BACKLOG
# =====================================================

if archivo_anterior:

    df_anterior = cargar_matriz(
        archivo_anterior
    )

    estados = [
        "RETRASADO",
        "VIGENTE",
        "POSPUESTO",
        "POSPUESTA"
    ]

    df_anterior = df_anterior[
        df_anterior["STATUS_SEGUIMIENTO"]
        .isin(estados)
    ]

    resumen_ant = (
        df_anterior
        .groupby("STATUS_SEGUIMIENTO")
        .agg(
            OT_ANTERIOR=(
                "STATUS_SEGUIMIENTO",
                "count"
            ),
            MONTO_ANTERIOR=(
                "MONTO_VENTA_FINAL",
                "sum"
            )
        )
        .reset_index()
    )

    resumen_act = (
        df_estado
        .groupby("STATUS_SEGUIMIENTO")
        .agg(
            OT_ACTUAL=(
                "STATUS_SEGUIMIENTO",
                "count"
            ),
            MONTO_ACTUAL=(
                "MONTO_VENTA_FINAL",
                "sum"
            )
        )
        .reset_index()
    )

    comparativo = (
        resumen_ant
        .merge(
            resumen_act,
            on="STATUS_SEGUIMIENTO",
            how="outer"
        )
        .fillna(0)
    )

    comparativo["VARIACION_OT"] = (
        comparativo["OT_ACTUAL"]
        -
        comparativo["OT_ANTERIOR"]
    )

    comparativo["VARIACION_MONTO"] = (
        comparativo["MONTO_ACTUAL"]
        -
        comparativo["MONTO_ANTERIOR"]
    )

    st.subheader(
        "📈 Variación del Backlog"
    )

    st.dataframe(
    comparativo.style.format(
        {
            "OT_ANTERIOR": "{:,.0f}",
            "OT_ACTUAL": "{:,.0f}",
            "VARIACION_OT": "{:,.0f}",
            "MONTO_ANTERIOR": "${:,.2f}",
            "MONTO_ACTUAL": "${:,.2f}",
            "VARIACION_MONTO": "${:,.2f}"
        }
    ),
    use_container_width=True
)
fig = px.bar(
    resumen,
    x="STATUS_SEGUIMIENTO",
    y="OT",
    color="STATUS_SEGUIMIENTO",
    text="OT",
    color_discrete_map={
        "VIGENTE": "green",
        "RETRASADO": "red",
        "POSPUESTO": "blue",
        "POSPUESTA": "blue"
    }
)

st.plotly_chart(
    fig,
    use_container_width=True
)

st.subheader(
    "Distribución de Estados"
)
fig_pie = px.pie(
    resumen,
    values="OT",
    names="STATUS_SEGUIMIENTO",
    hole=0.4,
    color="STATUS_SEGUIMIENTO",
    color_discrete_map={
        "VIGENTE": "green",
        "RETRASADO": "red",
        "POSPUESTO": "blue",
        "POSPUESTA": "blue"
    }
)
st.plotly_chart(
    fig_pie,
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
        title="OT Retrasadas, Vigentes y Pospuestas por Año",
        color_discrete_map={
            "POSPUESTO": "#0070C0",
            "POSPUESTA": "#0070C0",
            "VIGENTE": "#00B050",
            "RETRASADO": "#C00000"
        }
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
        title="Monto por Estado y Año",
        color_discrete_map={
            "VIGENTE": "#00B050",
            "RETRASADO": "#C00000",
            "POSPUESTO": "#0070C0",
            "POSPUESTA": "#0070C0"
        }
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
