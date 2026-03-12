import streamlit as st
import numpy as np
import geostruct_engine as eng
import interface_widgets as ui
import visualizacao_plots as viz

st.set_page_config(layout="wide", page_title="JocaMohr Web")

# 1. Renderiza a Sidebar e pega os valores
p = ui.render_sidebar()

# 2. Realiza os cálculos (Lógica Pura)
s1_eff, s3_eff = p["s1"] - (p["alpha"] * p["pp"]), p["s3"] - (p["alpha"] * p["pp"])
centro, raio = (s1_eff + s3_eff) / 2, (s1_eff - s3_eff) / 2
x_env, y_env, xt_coll = eng.calcular_envoltoria(p["ts"], p["pc"], p["c"], p["phi"])
xr, yr, res_c, xc, yc = eng.obter_geometria_v18(centro, raio, x_env, y_env, p["ts"], p["pc"])
sn_p = centro - raio * np.cos(2 * np.radians(p["ang_s1"]))
tn_p = abs(raio * np.sin(2 * np.radians(p["ang_s1"])))

# 3. Renderiza os Gráficos
viz.plot_mohr(x_env, y_env, xr, yr, xc, yc, sn_p, tn_p)
viz.plot_3d_block(p["regime"], p["ang_s1"])
