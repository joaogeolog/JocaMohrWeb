import streamlit as st
import numpy as np
import geostruct_engine as eng
import interface_widgets as ui
import visualizacao_plots as viz

# 1. Configuração Base com CSS para eliminar o espaço em branco do topo
st.set_page_config(layout="wide", page_title="JocaMohr Web", page_icon="⚒️")

st.markdown("""
    <style>
        /* Remove o espaço do topo (header) e reduz o padding do container principal */
        .block-container { padding-top: 0rem !important; padding-bottom: 0rem !important; }
        header { visibility: hidden; }
        footer { visibility: hidden; }
        /* Reduz o espaço entre as colunas e os blocos */
        [data-testid="stVerticalBlock"] { gap: 0.1rem !important; }
    </style>
""", unsafe_allow_html=True)

# 2. Inicialização Robusta
if 'val_s1' not in st.session_state:
    p_init = {k: float(v) if isinstance(v, (int, float)) else v for k, v in ui.DEFAULTS.items()}
    p_init['ang_s1'] = p_init['ang']
    p_init['ts'] = abs(ui.DEFAULTS['ts'])
else:
    ts_val = st.session_state.get('val_ts', ui.DEFAULTS['ts'])
    p_init = {
        "s1": st.session_state.get('val_s1', ui.DEFAULTS['s1']),
        "s3": st.session_state.get('val_s3', ui.DEFAULTS['s3']),
        "pp": st.session_state.get('val_pp', ui.DEFAULTS['pp']),
        "alpha": st.session_state.get('val_alpha', ui.DEFAULTS['alpha']),
        "c": st.session_state.get('val_c', ui.DEFAULTS['c']),
        "phi": st.session_state.get('val_phi', ui.DEFAULTS['phi']),
        "ts": abs(ts_val),
        "pc": st.session_state.get('val_pc', ui.DEFAULTS['pc']),
        "regime": st.session_state.get('regime_sel', ui.DEFAULTS['regime']),
        "ang_s1": st.session_state.get('val_ang', ui.DEFAULTS['ang'])
    }

# 3. Cálculos
s1_eff = p_init["s1"] - (p_init["alpha"] * p_init["pp"])
s3_eff = p_init["s3"] - (p_init["alpha"] * p_init["pp"])
x_env, y_env, xt_coll = eng.calcular_envoltoria(p_init["ts"], p_init["pc"], p_init["c"], p_init["phi"])

sn, tn, falhou = eng.calcular_ponto_com_trava(s1_eff, s3_eff, p_init["ang_s1"], x_env, y_env, st.session_state.get('ponto_fisico', {}))
xc_s, yc_s, xc_f, yc_f, env_high = eng.obter_geometria_v18((s1_eff+s3_eff)/2, (s1_eff-s3_eff)/2, x_env, y_env)

# 4. Layout Superior (Visualização)
# Note que os gráficos foram configurados para altura de 450px em vez de 500px para ganhar espaço
col_3d, col_mohr = st.columns([1, 2])
with col_3d: 
    viz.plot_3d_block(p_init) # Certifique-se que no viz a altura seja params.get('height', 450)
with col_mohr: 
    viz.plot_mohr(x_env, y_env, xt_coll, xc_s, yc_s, xc_f, yc_f, env_high, sn, tn, st.session_state.get('path_x', []), st.session_state.get('path_y', []), falhou, p_init)

# 5. Interface Inferior
ui.render_bottom_interface()

# 6. Histórico
st.session_state.ponto_fisico = {'sn': sn, 'tn': tn}
if 'path_x' not in st.session_state: st.session_state.path_x, st.session_state.path_y = [], []
if not st.session_state.path_x or (abs(sn - st.session_state.path_x[-1]) > 0.02):
    st.session_state.path_x.append(sn)
    st.session_state.path_y.append(tn)
