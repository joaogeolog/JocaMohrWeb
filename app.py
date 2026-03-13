import streamlit as st
import numpy as np
import geostruct_engine as eng
import interface_widgets as ui
import visualizacao_plots as viz

# 1. Configuração da Página
st.set_page_config(layout="wide", page_title="JocaMohr Web", page_icon="⚒️")

# 2. CSS para Molduras e Ajuste de Topo
st.markdown("""
    <style>
    header {visibility: hidden;}
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 0rem !important;
    }
    /* Estilo das Molduras */
    .moldura-3d {
        border: 2px solid #f39c12; 
        border-radius: 8px; 
        padding: 5px;
        background-color: white;
    }
    .moldura-mohr {
        border: 2px solid #27ae60; 
        border-radius: 8px; 
        padding: 5px;
        background-color: white;
    }
    .moldura-ui {
        border: 1px solid #ddd; 
        border-radius: 8px; 
        padding: 15px;
        background-color: #f9f9f9;
        margin-top: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Gestão de Estado
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

# 4. Cálculos Geomecânicos
s1_eff = p_init["s1"] - (p_init["alpha"] * p_init["pp"])
s3_eff = p_init["s3"] - (p_init["alpha"] * p_init["pp"])
x_env, y_env, xt_coll = eng.calcular_envoltoria(p_init["ts"], p_init["pc"], p_init["c"], p_init["phi"])
sn, tn, falhou = eng.calcular_ponto_com_trava(
    s1_eff, s3_eff, p_init["ang_s1"], x_env, y_env, p_init["ts"], p_init["pc"], 
    st.session_state.get('ponto_fisico', {'sn': 0.0, 'tn': 0.0})
)
xc_f, yc_f, res_c, xc_o, yc_o = eng.obter_geometria_v18(
    (s1_eff+s3_eff)/2, (s1_eff-s3_eff)/2, x_env, y_env, p_init["ts"], p_init["pc"]
)

# 5. ÁREA SUPERIOR: GRÁFICOS COM MOLDURAS
col_3d, col_mohr = st.columns([1, 2])

with col_3d:
    st.markdown('<div class="moldura-3d">', unsafe_allow_html=True)
    viz.plot_3d_block(p_init)
    st.markdown('</div>', unsafe_allow_html=True)

with col_mohr:
    st.markdown('<div class="moldura-mohr">', unsafe_allow_html=True)
    viz.plot_mohr(x_env, y_env, xt_coll, xc_f, yc_f, res_c, xc_o, yc_o, sn, tn, 
                  st.session_state.get('path_x', []), st.session_state.get('path_y', []), falhou, p_init)
    st.markdown('</div>', unsafe_allow_html=True)

# 6. ÁREA INFERIOR: INTERFACE COM MOLDURA
st.markdown('<div class="moldura-ui">', unsafe_allow_html=True)
p = ui.render_bottom_interface()
st.markdown('</div>', unsafe_allow_html=True)

# Atualização de Trajetória
st.session_state.ponto_fisico = {'sn': sn, 'tn': tn}
st.session_state.path_x.append(sn)
st.session_state.path_y.append(tn)
