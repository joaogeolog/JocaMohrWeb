import streamlit as st
import numpy as np
import geostruct_engine as eng
import interface_widgets as ui
import visualizacao_plots as viz

# Configuração Base
st.set_page_config(layout="wide", page_title="JocaMohr Web", page_icon="⚒️")

# 1. Captura e Tratamento de Parâmetros
if 'val_s1' not in st.session_state:
    p_init = {k: float(v) if isinstance(v, (int, float)) else v for k, v in ui.DEFAULTS.items()}
    p_init['ang_s1'] = p_init['ang']
    p_init['ts_mod'] = abs(ui.DEFAULTS['ts'])
else:
    # Garantimos o módulo da tração para o motor de cálculo
    ts_slider = st.session_state.get('val_ts', ui.DEFAULTS['ts'])
    p_init = {
        "s1": st.session_state.get('val_s1', ui.DEFAULTS['s1']),
        "s3": st.session_state.get('val_s3', ui.DEFAULTS['s3']),
        "pp": st.session_state.get('val_pp', ui.DEFAULTS['pp']),
        "alpha": st.session_state.get('val_alpha', ui.DEFAULTS['alpha']),
        "c": st.session_state.get('val_c', ui.DEFAULTS['c']),
        "phi": st.session_state.get('val_phi', ui.DEFAULTS['phi']),
        "ts_mod": abs(ts_slider),
        "pc": st.session_state.get('val_pc', ui.DEFAULTS['pc']),
        "regime": st.session_state.get('regime_sel', ui.DEFAULTS['regime']),
        "ang_s1": st.session_state.get('val_ang', ui.DEFAULTS['ang'])
    }

# 2. Cálculos de Envoltória e Tensões Efetivas
s1_eff = p_init["s1"] - (p_init["alpha"] * p_init["pp"])
s3_eff = p_init["s3"] - (p_init["alpha"] * p_init["pp"])

# x_env e y_env definem a "fronteira" da rocha
x_env, y_env, xt_coll = eng.calcular_envoltoria(p_init["ts_mod"], p_init["pc"], p_init["c"], p_init["phi"])

# 3. Lógica de Interseção (O ponto "trava" na borda se tentar sair)
# Calculamos o ponto teórico pretendido (sn_target, tn_target)
sn_target = (s1_eff + s3_eff)/2 + (s1_eff - s3_eff)/2 * np.cos(np.radians(2 * p_init["ang_s1"]))
tn_target = abs((s1_eff - s3_eff)/2 * np.sin(np.radians(2 * p_init["ang_s1"])))

# Buscamos a interseção com a envoltória usando o histórico
path_x = st.session_state.get('path_x', [])
path_y = st.session_state.get('path_y', [])

# A nova função eng.calcular_ponto_com_intersecao retorna o ponto na borda se houver falha
sn, tn, falhou = eng.calcular_ponto_com_intersecao(sn_target, tn_target, path_x, path_y, x_env, y_env)

# Geometria dos círculos para o Plotly
xc_f, yc_f, res_c, xc_o, yc_o = eng.obter_geometria_v18((s1_eff+s3_eff)/2, (s1_eff-s3_eff)/2, x_env, y_env, p_init["ts_mod"], p_init["pc"])

# 4. Interface e Gráficos
col_3d, col_mohr = st.columns([1, 2])
with col_3d: 
    viz.plot_3d_block(p_init)
with col_mohr: 
    viz.plot_mohr(x_env, y_env, xt_coll, xc_f, yc_f, res_c, xc_o, yc_o, sn, tn, path_x, path_y, falhou, p_init)

ui.render_bottom_interface()

# 5. Atualização da Trajetória
if 'path_x' not in st.session_state:
    st.session_state.path_x, st.session_state.path_y = [], []

# Só adicionamos ao path se o ponto mudou significativamente (evita duplicatas paradas na borda)
if not path_x or (abs(sn - path_x[-1]) > 0.01 or abs(tn - path_y[-1]) > 0.01):
    st.session_state.path_x.append(sn)
    st.session_state.path_y.append(tn)
