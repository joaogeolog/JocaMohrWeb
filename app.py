import streamlit as st
import numpy as np
import geostruct_engine as eng
import interface_widgets as ui
import visualizacao_plots as viz

# 1. Configuração Base do Streamlit
st.set_page_config(layout="wide", page_title="JocaMohr Web", page_icon="⚒️")
st.markdown("<style>header {visibility: hidden;} .block-container {padding-top: 1rem !important;}</style>", unsafe_allow_html=True)

# 2. Inicialização do Estado (Session State)
if 'val_s1' not in st.session_state:
    p_init = {k: float(v) if isinstance(v, (int, float)) else v for k, v in ui.DEFAULTS.items()}
    p_init['ang_s1'] = p_init['ang']
    p_init['val_mergulho'] = p_init['mergulho']
    st.session_state.path_x, st.session_state.path_y = [], []
else:
    p_init = {
        "s1": st.session_state.get('val_s1', ui.DEFAULTS['s1']),
        "s3": st.session_state.get('val_s3', ui.DEFAULTS['s3']),
        "pp": st.session_state.get('val_pp', ui.DEFAULTS['pp']),
        "alpha": st.session_state.get('val_alpha', ui.DEFAULTS['alpha']),
        "c": st.session_state.get('val_c', ui.DEFAULTS['c']),
        "phi": st.session_state.get('val_phi', ui.DEFAULTS['phi']),
        "ts": abs(st.session_state.get('val_ts', ui.DEFAULTS['ts'])),
        "pc": st.session_state.get('val_pc', ui.DEFAULTS['pc']),
        "regime": st.session_state.get('regime_sel', ui.DEFAULTS['regime']),
        "ang_s1": st.session_state.get('val_ang', ui.DEFAULTS['ang']),
        "val_mergulho": st.session_state.get('val_mergulho', ui.DEFAULTS['mergulho'])
    }

# 3. Cálculos Geomecânicos (Tensões Efetivas)
s1_eff = p_init["s1"] - (p_init["alpha"] * p_init["pp"])
s3_eff = p_init["s3"] - (p_init["alpha"] * p_init["pp"])

# Cálculo da Envoltória de Falha
x_env, y_env, xt_coll = eng.calcular_envoltoria(p_init["ts"], p_init["pc"], p_init["c"], p_init["phi"])

# Cálculo do Ponto no Plano (Usa Ângulo com S1)
sn, tn, falhou = eng.calcular_ponto_com_trava(s1_eff, s3_eff, p_init["ang_s1"], x_env, y_env, st.session_state.get('ponto_fisico', {}))

# Atualização da Trajetória (Rastro Laranja)
if not st.session_state.path_x or (abs(sn - st.session_state.path_x[-1]) > 0.05):
    st.session_state.path_x.append(sn)
    st.session_state.path_y.append(tn)

# Geometria do Círculo de Mohr (Sólido/Tracejado)
xc_s, yc_s, xc_f, yc_f, env_high = eng.obter_geometria_v18((s1_eff+s3_eff)/2, (s1_eff-s3_eff)/2, x_env, y_env)

# 4. Layout e Renderização dos Gráficos
col_3d, col_mohr = st.columns([1, 2])

with col_3d: 
    # Passa p_init que agora contém 'val_mergulho' para orientar o plano XYZ
    viz.plot_3d_block(p_init)

with col_mohr: 
    viz.plot_mohr(x_env, y_env, xt_coll, xc_s, yc_s, xc_f, yc_f, env_high, sn, tn, st.session_state.path_x, st.session_state.path_y, falhou, p_init)

# 5. Interface de Usuário (Barras e Sliders)
ui.render_bottom_interface()

# Salva o ponto atual para a lógica de trava do próximo frame
st.session_state.ponto_fisico = {'sn': sn, 'tn': tn}
