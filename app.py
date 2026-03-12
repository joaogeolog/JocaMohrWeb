import streamlit as st
import numpy as np
import geostruct_engine as eng
import interface_widgets as ui
import visualizacao_plots as viz

st.set_page_config(layout="wide", page_title="JocaMohr Web")

p = ui.render_sidebar()

# Cálculos com a Lógica de Trava (Path)
s1_eff, s3_eff = p["s1"] - (p["alpha"] * p["pp"]), p["s3"] - (p["alpha"] * p["pp"])
x_env, y_env, xt_coll = eng.calcular_envoltoria(p["ts"], p["pc"], p["c"], p["phi"])

sn, tn, falhou = eng.calcular_ponto_com_trava(s1_eff, s3_eff, p["ang_s1"], x_env, y_env, p["ts"], p["pc"], st.session_state.ponto_fisico)

st.session_state.ponto_fisico['sn'], st.session_state.ponto_fisico['tn'] = sn, tn
st.session_state.path_x.append(sn); st.session_state.path_y.append(tn)

xc_f, yc_f, res_c, xc_o, yc_o = eng.obter_geometria_v18((s1_eff+s3_eff)/2, (s1_eff-s3_eff)/2, x_env, y_env, p["ts"], p["pc"])

viz.plot_mohr(x_env, y_env, xt_coll, xc_f, yc_f, xc_o, yc_o, sn, tn, st.session_state.path_x, st.session_state.path_y, falhou)
viz.plot_3d_block(p["regime"], p["ang_s1"])
