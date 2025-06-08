# ── Dashboard de Ventas Retail – Colombia ────────────────────────────────
import streamlit as st, pandas as pd, plotly.express as px
from pathlib import Path
st.set_page_config(page_title="Dashboard Retail – Colombia", layout="wide")

# 1. Carga
FILE = Path("retail_limpio.xlsx")
df = pd.read_excel(FILE) if FILE.exists() else pd.read_excel(st.file_uploader("Sube retail_limpio.xlsx", type=["xlsx"]))
pais_col = next(c for c in df.columns if "pais" in c.lower() or "país" in c.lower())
df = df[df[pais_col].astype(str).str.strip().str.lower() == "colombia"]

# 2. Campos y filtros
df["Año"] = df["Fecha del pedido"].dt.year
df["Mes"] = df["Fecha del pedido"].dt.to_period("M")
años = sorted(df["Año"].unique())
sel  = st.sidebar.multiselect("Año", años, default=años)
df   = df[df["Año"].isin(sel)]

# 3. KPIs
ventas, gan = df["Ventas"].sum(), df["Ganancia"].sum()
pct_tec = df[df["Categoría"]=="Tecnología"]["Ventas"].sum()/ventas*100
pct_rap = df[df["Método de envío"]=="Rápido"]["Ventas"].sum()/ventas*100
k1,k2,k3,k4 = st.columns(4)
k1.metric("Ventas totales",f"${ventas:,.0f}")
k2.metric("Ganancia total",f"${gan:,.0f}")
k3.metric("% Tecnología",f"{pct_tec:.1f}%")
k4.metric("% Envío Rápido",f"{pct_rap:.1f}%")
st.markdown("---")

# 4. Gráficas
treemap = px.treemap(df,path=["Categoría","Subcategoría"],values="Ventas",color="Ganancia",
                     color_continuous_scale="RdBu",title="Ventas y Ganancia por Categoría / Subcategoría")

mens = (df.groupby("Mes")["Ventas"].sum().reset_index().sort_values("Mes"))
mens["Mes_str"]=mens["Mes"].astype(str)   # ← FIX Period → str
linea = px.line(mens,x="Mes_str",y="Ventas",title="Ventas mensuales (COP)")

env  = px.bar(df.groupby("Método de envío")["Ventas"].sum().reset_index(),
              x="Método de envío",y="Ventas",title="Ventas por Método de Envío",text_auto=".2s")

seg  = px.bar(df.groupby("Segmento")["Ventas"].sum().reset_index(),
              x="Ventas",y="Segmento",orientation="h",
              title="Ventas por Segmento",text_auto=".2s")

ciu  = px.bar(df.groupby("Ciudad")["Ganancia"].sum().nlargest(10).reset_index(),
              x="Ciudad",y="Ganancia",title="Top 10 Ciudades por Ganancia",text_auto=".2s")

# 5. Layout
l,r=st.columns(2); l.plotly_chart(treemap,use_container_width=True); r.plotly_chart(linea,use_container_width=True)
l2,r2=st.columns(2); l2.plotly_chart(env,use_container_width=True);   r2.plotly_chart(seg,use_container_width=True)
st.plotly_chart(ciu,use_container_width=True)
st.caption("Fuente: retail_limpio.xlsx – Filtrado a Colombia")
