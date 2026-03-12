import streamlit as st
import numpy as np
import plotly.graph_objects as go
import geostruct_engine as eng

# 1. Configuração da Página e CSS para Layout de Engenharia
st.set_page_config(layout="wide", page_title="JocaMohr Web", page_icon="⚒️")

st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    .stNumberInput div div input { font-weight: bold; }
    [data-testid="stExpander"] { border: 1px solid #e6e9ef; }
    </style>
    """, unsafe_allow_html=True)

# --- FUNÇÃO AUXILIAR PARA INPUTS LADO A LADO ---
def dual_input(label, min_v, max_v, default_v, step=1.0, key_p=""):
    st.write(f"**{label}**")
    c1, c2 = st.columns([2, 1])
    # O Slider define o valor base
    s_val = c1.slider(f"S_{key_p}", min_v, max_v, float(default_v), step=float(step), label_visibility="collapsed", key=f"slide_{key_p}")
    # O Number Input refina ou mostra o valor exato
    n_val = c2.number_input(f"N_{key_p}", min_v, max_v, float(s_val), step=float(step), label_visibility="collapsed", key=f"num_{key_p}")
    return n_val

# --- SIDEBAR: CONTROLES (ControlWindow) ---
with st.sidebar:
    st.title("⚒️ JocaMohr Web")
    st.caption("Geólogo: João Carlos Menescal | Macaé, RJ")

    with st.expander("1. ESTADO DE TENSÃO (MPa)", expanded=True):
        s1 = dual_input("S1", 0.0, 400.0, 120.0, key_p="s1")
        s3 = dual_input("S3", 0.0, 300.0, 40.0, key_p="s3")
        pp = dual_input("P. Poros", 0.0, 200.0, 20.0, key_p="pp")
        alpha = dual_input("Biot (α)", 0.0, 1.0, 1.0, step=0.01, key_p="alpha")

    with st.expander("2. PROPRIEDADES DA ROCHA", expanded=True):
        c_rock = dual_input("Coesão", 0.0, 100.0, 15.0, key_p="c")
        phi = dual_input("Atrito (°)", 0.0, 60.0, 30.0, key_p="phi")
        ts = dual_input("Tração", 0.0, 50.0, 10.0, key_p="ts")
        pc = dual_input("Compressão", 0.0, 500.0, 180.0, key_p="pc")

    with st.expander("3. ORIENTAÇÃO DO PLANO", expanded=True):
        regime = st.selectbox("Regime Tectônico", ["Normal", "Transcorrente", "Reverso"])
        ang_s1 = dual_input("Ângulo com S1 (°)", 0.0, 90.0, 30.0, step=0.1, key_p="ang")

# --- PROCESSAMENTO GEOMECÂNICO (Conectado aos Sliders) ---
s1_eff = s1 - (alpha * pp)
s3_eff = s3 - (alpha * pp)
centro, raio = (s1_eff + s3_eff) / 2, (s1_eff - s3_eff) / 2

# Chamas as funções do seu geostruct_engine.py
x_env, y_env, xt_coll = eng.calcular_envoltoria(ts, pc, c_rock, phi)
xr, yr, res_c, xc, yc = eng.obter_geometria_v18(centro, raio, x_env, y_env, ts, pc)

# Estado no plano atual
theta_rad = np.radians(ang_s1)
sn_p = centro - raio * np.cos(2 * theta_rad)
tn_p = abs(raio * np.sin(2 * theta_rad))

# --- LAYOUT PRINCIPAL (Mosaico Integrado) ---
col_main = st.container()

with col_main:
    # 1. DIAGRAMA DE MOHR
    fig_mohr = go.Figure()
    
    # Envoltória de Falha
    fig_mohr.add_trace(go.Scatter(x=x_env, y=y_env, name="Envoltória", line=dict(color='red', width=2)))
    
    # Círculos (Estável e Falha)
    fig_mohr.add_trace(go.Scatter(x=xr, y=yr, name="Círculo Mohr", line=dict(color='blue', width=3)))
    fig_mohr.add_trace(go.Scatter(x=xc, y=yc, name="Tensões Teóricas", line=dict(color='black', dash='dash', width=1)))
    
    # Ponto Crítico no Plano
    fig_mohr.add_trace(go.Scatter(x=[sn_p], y=[tn_p], mode='markers', 
                                  marker=dict(size=14, color='yellow', line=dict(width=2, color='black')),
                                  name="Estado no Plano"))

    fig_mohr.update_layout(title="Análise de Estabilidade de Mohr-Coulomb", height=420,
                          xaxis_title="Tensão Normal Efetiva σn' (MPa)", yaxis_title="Tensão Cisalhante τ (MPa)",
                          yaxis=dict(scaleanchor="x", scaleratio=1), margin=dict(t=50, b=50))
    st.plotly_chart(fig_mohr, use_container_width=True)

    # 2. VISUALIZAÇÃO 3D (Substituindo o PyVista)
    st.subheader("Bloco 3D e Vetores de Tensão")
    
    # Define eixos baseados no regime (Lógica Andersoniana)
    if regime == 'Normal': v1, v2, v3 = [0,0,1], [1,0,0], [0,1,0]
    elif regime == 'Transcorrente': v1, v2, v3 = [0,1,0], [0,0,1], [1,0,0]
    else: v1, v2, v3 = [1,0,0], [0,1,0], [0,0,1]

    fig_3d = go.Figure()

    # Desenha o Plano de Fratura inclinado
    dip_rad = np.radians(90 - ang_s1 if regime != 'Transcorrente' else 90)
    # Criando um mesh simples para o plano
    fig_3d.add_trace(go.Mesh3d(x=[-1,1,1,-1], y=[-1,-1,1,1], z=[-np.sin(dip_rad),-np.sin(dip_rad),np.sin(dip_rad),np.sin(dip_rad)], 
                               color='lightblue', opacity=0.7, name="Fratura"))

    # Adiciona cones para representar S1 (Azul) e S3 (Vermelho)
    fig_3d.add_trace(go.Cone(x=[0], y=[0], z=[1.2*v1[2]], u=[0], v=[0], w=[-v1[2]], colorscale=[[0, 'blue'], [1, 'blue']], showscale=False))
    fig_3d.add_trace(go.Cone(x=[1.2*v3[0]], y=[0], z=[0], u=[-v3[0]], v=[0], w=[0], colorscale=[[0, 'red'], [1, 'red']], showscale=False))

    fig_3d.update_layout(scene=dict(aspectmode='data', xaxis_visible=False, yaxis_visible=False, zaxis_visible=False),
                         height=400, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_3d, use_container_width=True)
