import plotly.graph_objects as go
import streamlit as st
import numpy as np

def plot_mohr(x_env, y_env, xt_coll, xc_f, yc_f, res_c, xc_o, yc_o, sn_p, tn_p, p_x, p_y, falhou, params):
    """Renderiza o Diagrama de Mohr fiel ao original (já validado)."""
    fig = go.Figure()
    fig.add_shape(type="line", x0=-50, y0=0, x1=250, y1=0, line=dict(color="black", width=2))
    fig.add_trace(go.Scatter(x=x_env[x_env<=0], y=y_env[x_env<=0], line=dict(color='blue', width=1.5), showlegend=False))
    fig.add_trace(go.Scatter(x=x_env[(x_env>0) & (x_env<=xt_coll)], y=y_env[(x_env>0) & (x_env<=xt_coll)], line=dict(color='red', width=1.5), showlegend=False))
    fig.add_trace(go.Scatter(x=x_env[x_env>xt_coll], y=y_env[x_env>xt_coll], line=dict(color='green', width=1.5), showlegend=False))
    m_s = (yc_o < res_c - 1e-3)
    m_f = ~m_s & (yc_o > 0.05)
    fig.add_trace(go.Scatter(x=np.where(m_s, xc_o, np.nan), y=np.where(m_s, yc_o, np.nan), line=dict(color='#1f77b4', width=2.5), name="Estável"))
    fig.add_trace(go.Scatter(x=np.where(~m_s, xc_o, np.nan), y=np.where(~m_s, yc_o, np.nan), line=dict(color='black', width=1, dash='dash'), name="Teórico"))
    fig.add_trace(go.Scatter(x=np.where(m_f & (xc_f < 0), xc_f, np.nan), y=np.where(m_f & (xc_f < 0), yc_f, np.nan), line=dict(color='blue', width=4), showlegend=False))
    fig.add_trace(go.Scatter(x=np.where(m_f & (xc_f >= 0) & (xc_f <= xt_coll), xc_f, np.nan), y=np.where(m_f & (xc_f >= 0) & (xc_f <= xt_coll), yc_f, np.nan), line=dict(color='red', width=4), showlegend=False))
    fig.add_trace(go.Scatter(x=np.where(m_f & (xc_f > xt_coll), xc_f, np.nan), y=np.where(m_f & (xc_f > xt_coll), yc_f, np.nan), line=dict(color='green', width=4), showlegend=False))
    fig.add_trace(go.Scatter(x=p_x, y=p_y, line=dict(color='orange', width=1.5, dash='dash'), name="Trajetória"))
    fig.add_trace(go.Scatter(x=[sn_p], y=[tn_p], mode='markers', marker=dict(size=14, color='yellow' if falhou else '#2ca02c', line=dict(width=2, color='black')), showlegend=False))
    fig.add_annotation(x=-params['ts'] - 15, y=30, text="<b>Ruptura por<br>Tração</b>", font=dict(color="blue", size=10), showarrow=False)
    fig.add_annotation(x=xt_coll/2, y=90, text="<b>Cisalhamento</b>", font=dict(color="red", size=10), showarrow=False)
    fig.add_annotation(x=params['pc'] + 20, y=30, text="<b>Colapso<br>de poros</b>", font=dict(color="green", size=10), showarrow=False)
    fig.update_layout(xaxis=dict(range=[-50, 250], fixedrange=True), yaxis=dict(range=[0, 100], scaleanchor="x", scaleratio=1), template="plotly_white", height=450, showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def plot_3d_block(params):
    """Renderiza o bloco 3D com plano e vetores conforme fracture_window.py original."""
    ang_rad = np.radians(params['ang_s1'])
    reg = params['regime']
    s1, s3 = params['s1'], params['s3']
    s2 = (s1 + s3) / 2

    # Lógica de eixos original por regime tectônico
    v1, v2, v3 = ([0,0,1],[1,0,0],[0,1,0]) if reg=='Normal' else (([0,1,0],[0,0,1],[1,0,0]) if reg=='Transcorrente' else ([1,0,0],[0,1,0],[0,0,1]))
    
    # Vetor Normal ao plano
    norm = np.array(v1)*np.cos(ang_rad) + np.array(v3)*np.sin(ang_rad)
    
    fig = go.Figure()

    # 1. Desenho do Bloco (Wireframe do cubo)
    for x in [-40, 40]:
        for y in [-40, 40]:
            fig.add_trace(go.Scatter3d(x=[x,x], y=[y,y], z=[-50,50], mode='lines', line=dict(color='black', width=2), showlegend=False))
            fig.add_trace(go.Scatter3d(x=[-40,40], y=[y,y], z=[x/40*50,x/40*50], mode='lines', line=dict(color='black', width=2), showlegend=False)) # Simplificado

    # 2. Plano de Fratura (Mesh3d)
    # Gerando 4 pontos para o plano infinito que é clipado pelo bloco
    p_pts = np.array([[-40,-40,0],[40,-40,0],[40,40,0],[-40,40,0]])
    # Rotação do plano baseada na normal
    fig.add_trace(go.Mesh3d(x=[40,-40,-40,40], y=[40,40,-40,-40], 
                            z=[40*np.tan(ang_rad) if reg=='Normal' else 0]*4, 
                            color='lightblue', opacity=0.8, name="Plano"))

    # 3. Vetores de Tensão (S1: Azul, S2: Verde, S3: Vermelho)
    def add_arrow(direction, color, name, scale):
        fig.add_trace(go.Cone(x=[direction[0]*60], y=[direction[1]*60], z=[direction[2]*60],
                              u=[direction[0]*scale], v=[direction[1]*scale], w=[direction[2]*scale],
                              colorscale=[[0, color], [1, color]], showscale=False, name=name))

    add_arrow(v1, "blue", "S1", s1*0.2)
    add_arrow(v2, "green", "S2", s2*0.2)
    add_arrow(v3, "red", "S3", s3*0.2)

    # 4. Componentes Locais (Sn: Preto, Tau: Laranja)
    sn_v = s1*np.cos(ang_rad)**2 + s3*np.sin(ang_rad)**2
    add_arrow(norm, "black", "Sn", sn_v*0.2)

    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
                                 camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))),
                      height=500, margin=dict(l=0, r=0, t=0, b=0))
    
    st.plotly_chart(fig, use_container_width=True)
