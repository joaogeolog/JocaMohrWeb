import streamlit as st
import numpy as np
import geostruct_engine as eng
import interface_widgets as ui
import visualizacao_plots as viz

# 1. Configuração da Página
st.set_page_config(
    layout="wide", 
    page_title="JocaMohr Web", 
    page_icon="⚒️"
)

# 2. Renderização da Barra Lateral e Captura de Parâmetros
# Retorna um dicionário 'p' com todos os valores dos sliders/inputs
p = ui.render_sidebar()

# 3. Processamento Geomecânico
# Cálculo das Tensões Efetivas
s1_eff = p["s1"] - (p["alpha"] * p["pp"])
s3_eff = p["s3"] - (p["alpha"] * p["pp"])
centro = (s1_eff + s3_eff) / 2
raio = (s1_eff - s3_eff) / 2

# Geração da Envoltória de Falha (Tração, Shear, Colapso)
x_env, y_env, xt_coll = eng.calcular_envoltoria(p["ts"], p["pc"], p["c"], p["phi"])

# Cálculo do Ponto Crítico no Plano com a Lógica de Trava (Clamping)
# Utiliza o session_state.ponto_fisico para manter a consistência da trava
sn, tn, falhou = eng.calcular_ponto_com_trava(
    s1_eff, s3_eff, p["ang_s1"], 
    x_env, y_env, p["ts"], p["pc"], 
    st.session_state.ponto_fisico
)

# Atualização da Trajetória (Path) e do Ponto Atual no Estado da Sessão
st.session_state.ponto_fisico['sn'] = sn
st.session_state.ponto_fisico['tn'] = tn
st.session_state.path_x.append(sn)
st.session_state.path_y.append(tn)

# Geração da Geometria dos Círculos (Original vs Colapsado) para o Plot
# xc_f/yc_f: Círculo que "achata" na envoltória
# xc_o/yc_o: Círculo teórico que fica tracejado
xc_f, yc_f, res_c, xc_o, yc_o = eng.obter_geometria_v18(
    centro, raio, x_env, y_env, p["ts"], p["pc"]
)

# 4. Interface de Visualização (Main Panel)
col_mohr, col_3d = st.columns([1.2, 0.8])

with col_mohr:
    # Renderiza o Diagrama de Mohr com Arcos de Falha e Círculo Tracejado
    viz.plot_mohr(
        x_env, y_env, xt_coll, 
        xc_f, yc_f, res_c, xc_o, yc_o, 
        sn, tn, 
        st.session_state.path_x, 
        st.session_state.path_y, 
        falhou, p
    )

with col_3d:
    # Renderiza o Bloco 3D com Vetores de Tensão e Plano de Fratura
    viz.plot_3d_block(p)

# 5. Rodapé Informativo (Opcional)
st.divider()
st.caption(f"Modo: Geomecânica de Reservatório | Regime: {p['regime']} | Ângulo Crítico: {p['ang_s1']}°")
