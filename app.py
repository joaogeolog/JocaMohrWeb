import streamlit as st
import numpy as np
import geostruct_engine as eng
import interface_widgets as ui
import visualizacao_plots as viz

# Configuração Base
st.set_page_config(layout="wide", page_title="JocaMohr Web", page_icon="⚒️")

# 1. Inicialização Forçada do Session State
# Isso garante que NADA chegue vazio ao motor de cálculo
for key, default_val in ui.DEFAULTS.items():
    if f'val_{key}' not in st.session_state:
        st.session_state[f'val_{key}'] = float(default_val) if isinstance(default_val, (int, float)) else default_val

if 'regime_sel' not in st.session_state:
    st.session_state['regime_sel'] = ui.DEFAULTS['regime']

# 2. Atribuição Local com Fallbacks (Segurança Máxima)
# Se o .get falhar, o valor do ui.DEFAULTS entra na hora
s1    = st.session_state.get('val_s1',    ui.DEFAULTS['s1'])
s3    = st.session_state.get('val_s3',    ui.DEFAULTS['s3'])
pp    = st.session_state.get('val_pp',    ui.DEFAULTS['pp'])
alpha = st.session_state.get('val_alpha', ui.DEFAULTS['alpha'])
c     = st.session_state.get('val_c',     ui.DEFAULTS['c'])
phi   = st.session_state.get('val_phi',   ui.DEFAULTS['phi'])
ts    = st.session_state.get('val_ts',    ui.DEFAULTS['ts'])
pc    = st.session_state.get('val_pc',    ui.DEFAULTS['pc'])
reg   = st.session_state.get('regime_sel', ui.DEFAULTS['regime'])
ang   = st.session_state.get('val_ang',    ui.DEFAULTS['ang'])

# 3. Processamento de Variáveis
s1_eff = float(s1 - (alpha * pp))
s3_eff = float(s3 - (alpha * pp))
ts_abs = float(abs(ts)) # Módulo da tração para a matemática da envoltória

# Chamada do Motor de Cálculo
# IMPORTANTE: Verifique se no geostruct_engine.py a função segue essa ordem: (ts, pc, c, phi)
try:
    x_env, y_env, xt_coll = eng.calcular_envoltoria(ts_abs, pc, c, phi)
except Exception as e:
    st.error(f"Erro no motor de cálculo: {e}")
    st.stop()

# 4. Lógica de Interseção (Caminho de Ruptura)
sn_target = (s1_eff + s3_eff)/2 + (s1_eff - s3_eff)/2 * np.cos(np.radians(2 * ang))
tn_target = abs((s1_eff - s3_eff)/2 * np.sin(np.radians(2 * ang)))

path_x = st.session_state.get('path_x', [])
path_y = st.session_state.get('path_y', [])

# Calcula o ponto na borda se houver falha
sn, tn, falhou = eng.calcular_ponto_com_intersecao(sn_target, tn_target, path_x, path_y, x_env, y_env)

# Geometria dos Círculos
xc_f, yc_f, res_c, xc_o, yc_o = eng.obter_geometria_v18((s1_eff+s3_eff)/2, (s1_eff-s3_eff)/2, x_env, y_env, ts_abs, pc)

# Dicionário de Parâmetros para os Gráficos
params_viz = {"s1": s1, "s3": s3, "regime": reg, "ang_s1": ang}

# 5. Renderização
col_3d, col_mohr = st.columns([1, 2])
with col_3d: 
    viz.plot_3d_block(params_viz)
with col_mohr: 
    viz.plot_mohr(x_env, y_env, xt_coll, xc_f, yc_f, res_c, xc_o, yc_o, sn, tn, path_x, path_y, falhou, params_viz)

ui.render_bottom_interface()

# 6. Atualização do Histórico (Trajetória)
if 'path_x' not in st.session_state:
    st.session_state.path_x, st.session_state.path_y = [], []

if not path_x or (abs(sn - path_x[-1]) > 0.05 or abs(tn - path_y[-1]) > 0.05):
    st.session_state.path_x.append(sn)
    st.session_state.path_y.append(tn)
