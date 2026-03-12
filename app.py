import streamlit as st
import numpy as np
import geostruct_engine as eng
import interface_widgets as ui
import visualizacao_plots as viz

# Configuração da página
st.set_page_config(layout="wide", page_title="JocaMohr Web", page_icon="⚒️")

# 1. Renderiza a Sidebar e obtém os parâmetros
p = ui.render_sidebar()

# 2. Processamento Geomecânico (Cálculos)
s1_eff = p["s1"] - (p["alpha"] * p["pp"])
s3_eff = p["s3"] - (p["alpha"] * p["pp"])
centro, raio = (s1_eff + s3_eff) / 2, (s1_eff - s3_eff) / 2

# Obtém dados da envoltória
x_env, y_env, xt_coll = eng.calcular_envoltoria(p["ts"], p["pc"], p["c"], p["phi"])

# Cálculo do ponto com trava (ponto_fisico inicializado no interface_widgets)
sn, tn, falhou = eng.calcular_ponto_com_trava(s1_eff, s3_eff, p["ang_s1"], x_env, y_env, p["ts"], p["pc"], st.session_state.ponto_fisico)

# Atualiza trajetória
st.session_state.ponto_fisico['sn'], st.session_state.ponto_fisico['tn'] = sn, tn
st.session_state.path_x.append(sn)
st.session_state.path_y.append(tn)

# Obtém geometria dos círculos (v18)
xc_f, yc_f, res_c, xc_o, yc_o = eng.obter_geometria_v18(centro, raio, x_env, y_env, p["ts"], p["pc"])

# 3. Renderização do Gráfico de Mohr (CORRIGIDO: Adicionado 'p' no final)
viz.plot_mohr(x_env, y_env, xt_coll, xc_f, yc_f, res_c, xc_o, yc_o, sn, tn, st.session_state.path_x, st.session_state.path_y, falhou, p)

# 4. Renderização do Bloco 3D
viz.plot_3d_block(p["regime"], p["ang_s1"])
