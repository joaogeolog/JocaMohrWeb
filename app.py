import streamlit as st
import geostruct_engine as eng
import interface_widgets as ui
import visualizacao_3d as v3d
import visualizacao_mohr as vmohr

st.set_page_config(layout="wide", page_title="JocaMohr Web")
st.markdown("""<style>header {visibility: hidden;} .main .block-container {padding-top: 0rem !important; margin-top: -30px !important;}</style>""", unsafe_allow_html=True)

if 'val_s1' not in st.session_state:
    for k, v in ui.DEFAULTS.items(): st.session_state[f'val_{k}'] = v
    st.session_state.path_x, st.session_state.path_y = [], []

# Coleta de Parâmetros e Forçamento de Sincronia
p = {k: st.session_state.get(f'val_{k}', v) for k, v in ui.DEFAULTS.items()}
p['regime'] = st.session_state.get('regime_sel', 'Normal')
p['ang_s1'] = st.session_state.get('val_ang', 30.0)
p['val_mergulho'] = st.session_state.get('val_mergulho', 60.0) # Força o mergulho pro 3D

# Cálculos
s1_e = p['s1'] - (p['alpha'] * p['pp'])
s3_e = p['s3'] - (p['alpha'] * p['pp'])
xe, ye, xt = eng.calcular_envoltoria(p['ts'], p['pc'], p['c'], p['phi'])
sn, tn, fail = eng.calcular_ponto_com_trava(s1_e, s3_e, p['ang_s1'], xe, ye, st.session_state.get('ponto', {}))

if not st.session_state.path_x or abs(sn - st.session_state.path_x[-1]) > 0.05:
    st.session_state.path_x.append(sn); st.session_state.path_y.append(tn)

xcs, ycs, xcf, ycf, m_high = eng.obter_geometria_v18((s1_e+s3_e)/2, (s1_e-s3_e)/2, xe, ye)

# Renderização
c_3d, c_mohr = st.columns([1, 2])
with c_3d: v3d.render_3d_block(p)
with c_mohr: vmohr.render_mohr_plot(xe, ye, xt, xcs, ycs, xcf, ycf, m_high, sn, tn, st.session_state.path_x, st.session_state.path_y, fail)

ui.render_ui()
st.session_state.ponto = {'sn': sn, 'tn': tn}
