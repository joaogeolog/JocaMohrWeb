import streamlit as st
import numpy as np
import geostruct_engine as eng
import interface_widgets as ui
import visualizacao_plots as viz

# Configuração Base
st.set_page_config(layout="wide", page_title="JocaMohr Web", page_icon="⚒️")

# 1. Recuperação de Parâmetros (Garante que p_init sempre tenha os nomes corretos)
if 'val_s1' not in st.session_state:
    p_init = {k: float(v) if isinstance(v, (int, float)) else v for k, v in ui.DEFAULTS.items()}
    p_init['ang_s1'] = p_init['ang']
else:
    p_init = {
        "s1": st.session_state.get('val_s1', ui.DEFAULTS['s1']),
        "s3": st.session_state.get('val_s3', ui.DEFAULTS['s3']),
        "pp": st.session_state.get('val_pp', ui.DEFAULTS['pp']),
        "alpha": st.session_state.get('val_alpha', ui.DEFAULTS['alpha']),
        "c": st.session_state.get('val_c', ui.DEFAULTS['c']),
        "phi": st.session_state.get('val_phi', ui.DEFAULTS['phi']),
        "ts": st.session_state.get('val_ts', ui.DEFAULTS['ts']),
        "pc": st.session_state.get('val_pc', ui.DEFAULTS['pc']),
        "regime": st.session_state.get('regime_sel', ui.DEFAULTS['regime']),
        "ang_s1": st.session_state.get('val_ang', ui.DEFAULTS['ang'])
    }

# 2. Cálculos Iniciais
s1_eff = p_init["s1"] - (p_init["alpha"] * p_init["pp"])
s3_eff = p_init["s3"] - (p_init["alpha"] * p_init["pp"])

# Tratamos o módulo da tração aqui para evitar AttributeError na linha 36
ts_abs = abs(p_init["ts"])

# Geração da Envoltória
x_env, y_env, xt_coll = eng.calcular_envoltoria(ts_abs, p_init["pc"], p_init["c"], p_init["phi"])

# 3. Lógica de Interseção: Onde o ponto "trava" ao tocar a envoltória
sn_target = (s1_eff + s3_eff)/2 + (s1_eff - s3_eff)/2 * np.cos(np.radians(2 * p_init["ang_s1"]))
tn_target = abs((s1_eff - s3_eff)/2 * np.sin(np.radians(2 * p_init["ang_s1"])))

path_x = st.session_state.get('path_x', [])
path_y = st.session_state.get('path_y', [])

# A função de interseção garante que o ponto sn, tn nunca ultrapasse x_env, y_env
sn, tn, falhou = eng.calcular_ponto_com_intersecao(sn_target, tn_target, path_x, path_y, x_env, y_env)

# 4. Geometria e Plots
xc_f, yc_f, res_c, xc_o, yc_o = eng.obter_geometria_v18((s1_eff+s3_eff)/2, (s1_eff-s3_eff)/2, x_env, y_env, ts_abs, p_init["pc"])

col_3d, col_mohr = st.columns([1, 2])
with col_3d: 
    viz.plot_3d_block(p_init)
with col_mohr: 
    viz.plot_mohr(x_env, y_env, xt_coll, xc_f, yc_f, res_c, xc_o, yc_o, sn, tn, path_x, path_y, falhou, p_init)

ui.render_bottom_interface()

# 5. Atualização da Memória da Trajetória
if 'path_x' not in st.session_state:
    st.session_state.path_x, st.session_state.path_y = [], []

# Adiciona o ponto se ele se moveu, permitindo que ele "deslize" sobre a envoltória
if not path_x or (abs(sn - path_x[-1]) > 0.05 or abs(tn - path_y[-1]) > 0.05):
    st.session_state.path_x.append(sn)
    st.session_state.path_y.append(tn)
