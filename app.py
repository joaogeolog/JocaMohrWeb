import streamlit as st
import numpy as np
import plotly.graph_objects as go
import geostruct_engine as eng # Certifique-se que este arquivo está na mesma pasta

# Configuração da Página
st.set_page_config(layout="wide", page_title="JocaMohr Web", page_icon="⚒️")

# CSS para layout compacto
st.markdown("""
    <style>
    .block-container { padding-top: 1rem; }
    [data-testid="stMetricValue"] { font-size: 1.2rem; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR: CONTROLES (Substitui ControlWindow) ---
with st.sidebar:
    st.title("⚒️ JocaMohr Control")
    
    with st.expander("1. ESTADO DE TENSÃO (MPa)", expanded=True):
        s1 = st.slider("S1", 0.0, 400.0, 120.0, key="s1")
        s3 = st.slider("S3", 0.0, 300.0, 40.0, key="s3")
        pp = st.slider("P. Poros", 0.0, 200.0, 20.0, key="pp")
        alpha = st.slider("Biot (α)", 0.0, 1.0, 1.0, 0.05)

    with st.expander("2. PROPRIEDADES DA ROCHA", expanded=True):
        c = st.slider("Coesão", 0.0, 100.0, 15.0)
        phi = st.slider("Atrito (°)", 0.0, 60.0, 30.0)
        ts = st.slider("Tração", 0.0, 50.0, 10.0)
        pc = st.slider("Compressão", 0.0, 500.0, 180.0)

    regime = st.radio("Regime Tectônico", ["Normal", "Transcorrente", "Reverso"], horizontal=True)
    ang_s1 = st.slider("Ângulo com S1 (°)", 0.0, 90.0, 30.0)

# --- LÓGICA DE CÁLCULO (Conectada aos Sliders) ---
s1_eff = s1 - (alpha * pp)
s3_eff = s3 - (alpha * pp)
centro = (s1_eff + s3_eff) / 2
raio = (s1_eff - s3_eff) / 2

# Dados da Envoltória e Círculo via engine
x_env, y_env, xt_coll = eng.calcular_envoltoria(ts, pc, c, phi)
xr, yr, res_c, xc, yc = eng.obter_geometria_v18(centro, raio, x_env, y_env, ts, pc)

# Ponto atual no plano
theta_rad = np.radians(ang_s1)
sn_ponto = centro - raio * np.cos(2 * theta_rad)
tn_ponto = abs(raio * np.sin(2 * theta_rad))

# --- LAYOUT PRINCIPAL (MOSAICO) ---
col_main = st.container()

with col_main:
    # 1. DIAGRAMA DE MOHR (Topo)
    fig_mohr = go.Figure()
    
    # Envoltórias
    fig_mohr.add_trace(go.Scatter(x=x_env, y=y_env, name="Envoltória", line=dict(color='red', width=2)))
    # Círculo de Mohr
    fig_mohr.add_trace(go.Scatter(x=xr, y=yr, name="Círculo Estável", line=dict(color='blue', width=3)))
    fig_mohr.add_trace(go.Scatter(x=xc, y=yc, name="Círculo Falha", line=dict(color='black', dash='dash', width=1)))
    # Ponto no Plano
    fig_mohr.add_trace(go.Scatter(x=[sn_ponto], y=[tn_ponto], mode='markers+text', 
                                  marker=dict(size=12, color='yellow', line=dict(width=2)),
                                  text=["Estado no Plano"], textposition="top center"))

    fig_mohr.update_layout(title="Diagrama de Mohr-Coulomb Efetivo", height=400,
                          xaxis_title="σn' (MPa)", yaxis_title="τ (MPa)",
                          yaxis=dict(scaleanchor="x", scaleratio=1), margin=dict(t=40, b=40))
    st.plotly_chart(fig_mohr, use_container_width=True)

    # 2. BLOCO 3D (Base)
    st.subheader("Visualização 3D do Plano e Tensões")
    
    # Simulação dos Vetores S1 e S3 no 3D
    # Orientação baseada no regime
    if regime == 'Normal': v1, v3 = [0,0,1], [0,1,0]
    elif regime == 'Transcorrente': v1, v3 = [0,1,0], [1,0,0]
    else: v1, v3 = [1,0,0], [0,0,1]

    fig_3d = go.Figure()

    # Desenhar o Plano de Falha (Simplificado como um retângulo inclinado)
    d_rad = np.radians(90 - ang_s1 if regime != 'Transcorrente' else 90)
    # Coordenadas do plano
    px = [-1, 1, 1, -1]; py = [-1, -1, 1, 1]; pz = [np.tan(d_rad)*x for x in px]
    
    fig_3d.add_trace(go.Mesh3d(x=px, y=py, z=pz, color='lightblue', opacity=0.6, name="Plano de Falha"))

    # Vetores de Tensão (Setas usando Cone do Plotly)
    fig_3d.add_trace(go.Cone(x=[0], y=[0], z=[1.5], u=[0], v=[0], w=[-1], colorscale=[[0, 'blue'], [1, 'blue']], name="S1"))
    fig_3d.add_trace(go.Cone(x=[0], y=[1.5], z=[0], u=[0], v=[-1], w=[0], colorscale=[[0, 'red'], [1, 'red']], name="S3"))

    fig_3d.update_layout(scene=dict(aspectmode='data', 
                                    xaxis=dict(range=[-2,2]), yaxis=dict(range=[-2,2]), zaxis=dict(range=[-2,2])),
                         height=450, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig_3d, use_container_width=True)
