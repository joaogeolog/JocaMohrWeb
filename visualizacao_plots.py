import plotly.graph_objects as go
import streamlit as st
import numpy as np

def plot_mohr(x_env, y_env, xt_coll, xr, yr, xc, yc, sn_p, tn_p, p_x, p_y, falhou):
    fig = go.Figure()
    fig.add_shape(type="line", x0=-50, y0=0, x1=250, y1=0, line=dict(color="black", width=2))

    # Envoltórias Coloridas (como no mohr_window.py original)
    fig.add_trace(go.Scatter(x=x_env[x_env<=0], y=y_env[x_env<=0], line=dict(color='blue', width=1.5), hoverinfo='skip', showlegend=False))
    fig.add_trace(go.Scatter(x=x_env[(x_env>0) & (x_env<=xt_coll)], y=y_env[(x_env>0) & (x_env<=xt_coll)], line=dict(color='red', width=1.5), hoverinfo='skip', showlegend=False))
    fig.add_trace(go.Scatter(x=x_env[x_env>xt_coll], y=y_env[x_env>xt_coll], line=dict(color='green', width=1.5), hoverinfo='skip', showlegend=False))

    # Círculo Estável e Teórico (Filtro para evitar linhas internas)
    res_c = np.interp(xc, x_env, y_env, left=0, right=0)
    m_s = yc <= res_c + 1e-3
    
    # Parte Estável (Azul)
    fig.add_trace(go.Scatter(x=np.where(m_s, xc, np.nan), y=np.where(m_s, yc, np.nan), line=dict(color='#1f77b4', width=3), name="Estável"))
    
    # Parte Falha (Tracejada)
    fig.add_trace(go.Scatter(x=np.where(~m_s, xc, np.nan), y=np.where(~m_s, yc, np.nan), line=dict(color='black', width=1, dash='dash'), name="Teórico"))

    # Arcos de Falha Espessos (width=4)
    m_f = ~m_s & (yc > 0.05)
    fig.add_trace(go.Scatter(x=np.where(m_f & (xc < 0), xc, np.nan), y=np.where(m_f & (xc < 0), yc, np.nan), line=dict(color='blue', width=4), showlegend=False))
    fig.add_trace(go.Scatter(x=np.where(m_f & (xc >= 0) & (xc <= xt_coll), xc, np.nan), y=np.where(m_f & (xc >= 0) & (xc <= xt_coll), yc, np.nan), line=dict(color='red', width=4), showlegend=False))
    fig.add_trace(go.Scatter(x=np.where(m_f & (xc > xt_coll), xc, np.nan), y=np.where(m_f & (xc > xt_coll), yc, np.nan), line=dict(color='green', width=4), showlegend=False))

    # Trajetória (Path) e Ponto
    fig.add_trace(go.Scatter(x=p_x, y=p_y, line=dict(color='orange', width=1.5, dash='dash'), name="Trajetória"))
    fig.add_trace(go.Scatter(x=[sn_p], y=[tn_p], mode='markers', marker=dict(size=14, color='yellow' if falhou else '#2ca02c', line=dict(width=2, color='black')), showlegend=False))

    fig.update_layout(title="ANÁLISE DE ESTABILIDADE (MOHR-COULOMB)", height=500, xaxis=dict(range=[-50, 250]), yaxis=dict(range=[0, 100], scaleanchor="x", scaleratio=1), template="plotly_white")
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def plot_3d_block(regime, ang_s1):
    st.subheader("Visualização Espacial do Bloco")
    st.info(f"Regime: {regime} | Ângulo: {ang_s1}°")
