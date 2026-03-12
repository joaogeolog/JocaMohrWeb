import plotly.graph_objects as go
import numpy as np
import streamlit as st

def plot_mohr(x_env, y_env, xr, yr, xc, yc, sn_p, tn_p):
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x_env, y=y_env, name="Envoltória", line=dict(color='red', width=2)))
    fig.add_trace(go.Scatter(x=xr, y=yr, name="Círculo Mohr", line=dict(color='blue', width=3)))
    fig.add_trace(go.Scatter(x=xc, y=yc, name="Tensões Teóricas", line=dict(color='black', dash='dash', width=1)))
    fig.add_trace(go.Scatter(x=[sn_p], y=[tn_p], mode='markers', 
                              marker=dict(size=14, color='yellow', line=dict(width=2, color='black'))))
    fig.update_layout(title="Diagrama de Mohr-Coulomb", height=400, yaxis=dict(scaleanchor="x", scaleratio=1))
    st.plotly_chart(fig, use_container_width=True)

def plot_3d_block(regime, ang_s1):
    # Lógica de eixos simplificada
    v1 = [0,0,1] if regime == 'Normal' else ([0,1,0] if regime == 'Transcorrente' else [1,0,0])
    fig = go.Figure()
    # Adicione aqui as geometrias do plano e cones que discutimos
    fig.update_layout(title="Bloco Geomecânico 3D", height=400)
    st.plotly_chart(fig, use_container_width=True)
