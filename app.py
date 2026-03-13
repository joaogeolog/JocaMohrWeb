import streamlit as st
import numpy as np
import geostruct_engine as eng
import interface_widgets as ui
import visual_izacao_plots as viz

# Configuração Base
st.set_page_config(layout="wide", page_title="JocaMohr Web", page_icon="⚒️")

# 1. Garantia de Inicialização
# Se o app resetar, os DEFAULTS garantem que o código abaixo não quebre
if 'val_s1' not in st.session_state:
    for k, v in ui.DEFAULTS.items():
        if f'val_{k}' not in st.session_state:
            st.session_state[f'val_{k}'] = float(v) if isinstance(v, (int, float)) else v
    st.session_state['regime_sel'] = ui.DEFAULTS['regime']
    st.session_state['val_ang'] = ui.DEFAULTS['ang']

# 2. Captura Direta e Segura (Evita AttributeError)
s1 = st.session_state.get('val_s1', ui.DEFAULTS['s1'])
s3 = st.session_state.get('val_s3', ui.DEFAULTS['s3'])
pp = st.session_state.get('val_pp', ui.DEFAULTS['pp'])
alpha = st.session_state.get('val_alpha', ui.DEFAULTS['alpha'])
c = st.session_state.get('val_c', ui.DEFAULTS['c'])
phi = st.session_state.get('val_phi', ui.DEFAULTS['phi'])
ts = st.session_state.get('val_ts', ui.DEFAULTS['ts'])
pc = st.session_state.get('val_pc', ui.DEFAULTS['pc'])
regime = st.session_state.get('regime_sel', ui.DEFAULTS['regime'])
ang_s1 = st.session_state.get('val_ang', ui.DEFAULTS['ang'])

# 3. Cálculos Geomecânicos
s1_eff = s1 - (alpha * pp)
s3_eff = s3 - (alpha * pp)
ts_abs = abs(ts)

# Chamada do motor de cálculo (Lógica de Envoltória)
x_env, y_env, xt_coll = eng.calcular_envoltoria(ts_abs, pc, c, phi)

# 4. Lógica de Interseção (Trava o ponto na borda da envoltória)
sn_target = (s1_eff + s3_eff)/2 + (s1_eff - s3_eff)/2 * np.cos(np.radians(2 * ang_s1))
tn_target = abs((s1_eff - s3_eff)/2 * np.sin(np.radians(2 * ang_s1)))

path_x = st.session_state.get('path_x', [])
path_y = st.session_state.get('path_y', [])

# Calcula o ponto real: se sn_target/tn_target falha, sn/tn será a interseção
sn, tn, falhou = eng.calcular_ponto_com_intersecao(sn_target, tn_target, path_x, path_y, x_env, y_env)

# Geometria para o Mohr
xc_f, yc_f, res_c, xc_o, yc_o = eng.obter_geometria_v18((s1_eff+s3_eff)/2, (s1_eff-s3_eff)/2, x_env, y_env, ts_abs, pc)

# Dicionário de parâmetros apenas para o bloco 3D
params_3d = {"s1": s1, "s3": s3, "regime": regime, "ang_s1": ang_s1}

# 5. Renderização
col_3d, col_mohr = st.columns([1, 2])
with col_3d: 
    viz.plot_3d_block(params_3d)
with col_mohr: 
    viz.plot_mohr(x_env, y_env, xt_coll, xc_f, yc_f, res_c, xc_o, yc_o, sn, tn, path_x, path_y, falhou, params_3d)

ui.render_bottom_interface()

# 6. Atualização de Histórico (Path)
if 'path_x' not in st.session_state:
    st.session_state.path_x, st.session_state.path_y = [], []

if not path_x or (abs(sn - path_x[-1]) > 0.05 or abs(tn - path_y[-1]) > 0.05):
    st.session_state.path_x.append(sn)
    st.session_state.path_y.append(tn)
