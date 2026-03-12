import streamlit as st
import numpy as np
import geostruct_engine as eng
import interface_widgets as ui
import visualizacao_plots as viz

st.set_page_config(layout="wide", page_title="JocaMohr Web", page_icon="⚒️")

# Estilo para remover margens excessivas no topo
st.markdown("<style>.block-container {padding-top: 1rem;}</style>", unsafe_allow_html=True)

# 1. ÁREA DE GRÁFICOS (SUPERIOR)
# Divisão: 1/3 para o Cubo 3D (esquerda) e 2/3 para o Mohr (direita)
col_cubo, col_mohr = st.columns([1, 2])

# Inicialização silenciosa para obter parâmetros antes do render
if 'val_s1' not in st.session_state:
    p_init = {k: float(v) if isinstance(v, (int, float)) else v for k, v in ui.DEFAULTS.items()}
    p_init['ang_s1'] = p_init['ang']
else:
    p_init = {
        "s1": st.session_state.val_s1, "s3": st.session_state.val_s3, "pp": st.session_state.val_pp,
        "alpha": st.session_state.val_alpha, "c": st.session_state.val_c, "phi": st.session_state.val_phi,
        "ts": st.session_state.val_ts, "pc": st.session_state.val_pc,
        "regime": st.session_state.regime_sel if "regime_sel" in st.session_state else "Normal",
        "ang_s1": st.session_state.val_ang
    }

# Cálculos Geomecânicos
s1_eff = p_init["s1"] - (p_init["alpha"] * p_init["pp"])
s3_eff = p_init["s3"] - (p_init["alpha"] * p_init["pp"])
x_env, y_env, xt_coll = eng.calcular_envoltoria(p_init["ts"], p_init["pc"], p_init["c"], p_init["phi"])
sn, tn, falhou = eng.calcular_ponto_com_trava(s1_eff, s3_eff, p_init["ang_s1"], x_env, y_env, p_init["ts"], p_init["pc"], st.session_state.get('ponto_fisico', {'sn': 0.0, 'tn': 0.0}))
xc_f, yc_f, res_c, xc_o, yc_o = eng.obter_geometria_v18((s1_eff+s3_eff)/2, (s1_eff-s3_eff)/2, x_env, y_env, p_init["ts"], p_init["pc"])

with col_cubo:
    viz.plot_3d_block(p_init)

with col_mohr:
    viz.plot_mohr(x_env, y_env, xt_coll, xc_f, yc_f, res_c, xc_o, yc_o, sn, tn, st.session_state.get('path_x', []), st.session_state.get('path_y', []), falhou, p_init)

# 2. ÁREA DE INTERFACE (INFERIOR)
st.divider()
p = ui.render_bottom_interface()

# Atualização de estado após interação para o próximo loop
st.session_state.ponto_fisico = {'sn': sn, 'tn': tn}
