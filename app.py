import streamlit as st
import numpy as np
import geostruct_engine as eng
import interface_widgets as ui
import visualizacao_plots as viz

st.set_page_config(layout="wide", page_title="JocaMohr Web", page_icon="⚒️")

# CSS para evitar rolagem global e permitir rolagem apenas na interface inferior
st.markdown("""
    <style>
    /* Remove rolagem global */
    .main .block-container {
        max-height: 100vh;
        overflow: hidden;
        padding-top: 1rem;
        padding-bottom: 0;
    }
    /* Container para os gráficos (fixo) */
    .fixed-plots {
        height: 55vh;
    }
    /* Container para a interface (rolagem se necessário) */
    .scrollable-ui {
        height: 40vh;
        overflow-y: auto;
        padding-right: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 1. ÁREA DE GRÁFICOS (SUPERIOR - FIXA)
plot_container = st.container()
with plot_container:
    st.markdown('<div class="fixed-plots">', unsafe_allow_html=True)
    col_cubo, col_mohr = st.columns([1, 2])

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

    s1_eff = p_init["s1"] - (p_init["alpha"] * p_init["pp"])
    s3_eff = p_init["s3"] - (p_init["alpha"] * p_init["pp"])
    x_env, y_env, xt_coll = eng.calcular_envoltoria(p_init["ts"], p_init["pc"], p_init["c"], p_init["phi"])
    sn, tn, falhou = eng.calcular_ponto_com_trava(s1_eff, s3_eff, p_init["ang_s1"], x_env, y_env, p_init["ts"], p_init["pc"], st.session_state.get('ponto_fisico', {'sn': 0.0, 'tn': 0.0}))
    xc_f, yc_f, res_c, xc_o, yc_o = eng.obter_geometria_v18((s1_eff+s3_eff)/2, (s1_eff-s3_eff)/2, x_env, y_env, p_init["ts"], p_init["pc"])

    with col_cubo:
        viz.plot_3d_block(p_init)
    with col_mohr:
        viz.plot_mohr(x_env, y_env, xt_coll, xc_f, yc_f, res_c, xc_o, yc_o, sn, tn, st.session_state.get('path_x', []), st.session_state.get('path_y', []), falhou, p_init)
    st.markdown('</div>', unsafe_allow_html=True)

# 2. ÁREA DE INTERFACE (INFERIOR - SCROLLABLE)
st.divider()
ui_container = st.container()
with ui_container:
    st.markdown('<div class="scrollable-ui">', unsafe_allow_html=True)
    p = ui.render_bottom_interface()
    st.markdown('</div>', unsafe_allow_html=True)

st.session_state.ponto_fisico = {'sn': sn, 'tn': tn}
