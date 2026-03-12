import streamlit as st
import numpy as np
import geostruct_engine as eng
import interface_widgets as ui
import visualizacao_plots as viz

# Configuração da página
st.set_page_config(layout="wide", page_title="JocaMohr Web", page_icon="⚒️")

# 1. Renderiza a Sidebar e obtém os parâmetros (Dicionário 'p')
p = ui.render_sidebar()

# 2. Processamento Geomecânico (Cálculos)
s1_eff = p["s1"] - (p["alpha"] * p["pp"])
s3_eff = p["s3"] - (p["alpha"] * p["pp"])
centro, raio = (s1_eff + s3_eff) / 2, (s1_eff - s3_eff) / 2

# Obtém dados da envoltória e geometria do círculo
x_env, y_env, xt_coll = eng.calcular_envoltoria(p["ts"], p["pc"], p["c"], p["phi"])
xr, yr, res_c, xc, yc = eng.obter_geometria_v18(centro, raio, x_env, y_env, p["ts"], p["pc"])

# Cálculo do ponto de estado no plano
theta_rad = np.radians(p["ang_s1"])
sn_p = centro - raio * np.cos(2 * theta_rad)
tn_p = abs(raio * np.sin(2 * theta_rad))

# 3. Renderização dos Gráficos (Atenção aos argumentos aqui)
viz.plot_mohr(x_env, y_env, xt_coll, xr, yr, xc, yc, sn_p, tn_p, p)

# 4. Renderização do Bloco 3D
viz.plot_3d_block(p["regime"], p["ang_s1"])
