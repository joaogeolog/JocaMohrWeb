import streamlit as st
import numpy as np
import geostruct_engine as eng
import interface_widgets as ui
import visualizacao_plots as viz

# 1. Configuração da Página
st.set_page_config(layout="wide", page_title="JocaMohr Web", page_icon="⚒️")

# 2. CSS DE CONTROLE TOTAL (Resolve o erro de posicionamento)
st.markdown("""
    <style>
    /* Esconde elementos desnecessários */
    header, footer {visibility: hidden !important;}
    
    /* Reseta o container principal para não ter margens nem rolagem */
    .main .block-container {
        padding: 0px !important;
        margin: 0px !important;
        max-height: 100vh !important;
        overflow: hidden !important;
    }

    /* FIXA OS GRÁFICOS NO TOPO (1/3 Cubo, 2/3 Mohr) */
    .top-section {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 55vh; /* Ocupa 55% da altura da tela */
        padding: 10px;
        display: flex;
        z-index: 1000;
        background-color: white;
    }

    /* FIXA A INTERFACE NA BASE */
    .bottom-section {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 45vh; /* Ocupa o restante da tela */
        padding: 10px;
        border-top: 2px solid #ddd;
        background-color: #f8f9fa;
        z-index: 1001;
    }
    
    /* Remove espaços fantasmas entre colunas do Streamlit */
    [data-testid="column"] {
        padding: 0px !important;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Lógica de Dados (Mantida conforme funcional)
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

# 4. Processamento Geomecânico
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

# 5. RENDERIZAÇÃO TOPO (Fixa em 55vh)
st.markdown('<div class="top-section">', unsafe_allow_html=True)
c_cubo, c_mohr = st.columns([1, 2])
with c_cubo:
    viz.plot_3d_block(p_init) #
with c_mohr:
    viz.plot_mohr(x_env, y_env, xt_coll, xc_f, yc_f, res_c, xc_o, yc_o, sn, tn, 
                  st.session_state.get('path_x', []), st.session_state.get('path_y', []), falhou, p_init) #
st.markdown('</div>', unsafe_allow_html=True)

# 6. RENDERIZAÇÃO BASE (Fixa em 45vh)
st.markdown('<div class="bottom-section">', unsafe_allow_html=True)
p = ui.render_bottom_interface() #
st.markdown('</div>', unsafe_allow_html=True)

# Atualização de Estado
st.session_state.ponto_fisico = {'sn': sn, 'tn': tn}
st.session_state.path_x.append(sn)
st.session_state.path_y.append(tn)
