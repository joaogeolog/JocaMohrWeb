import plotly.graph_objects as go
import streamlit as st
import numpy as np

def plot_mohr(x_env, y_env, xt_coll, xc_f, yc_f, res_c, xc_o, yc_o, sn_p, tn_p, p_x, p_y, falhou, params):
    """Renderiza o Diagrama de Mohr fiel ao original."""
    fig = go.Figure()
    fig.add_shape(type="line", x0=-50, y0=0, x1=250, y1=0, line=dict(color="black", width=2))
    
    # Envoltórias
    fig.add_trace(go.Scatter(x=x_env[x_env<=0], y=y_env[x_env<=0], line=dict(color='blue', width=1.5), showlegend=False))
    fig.add_trace(go.Scatter(x=x_env[(x_env>0) & (x_env<=xt_coll)], y=y_env[(x_env>0) & (x_env<=xt_coll)], line=dict(color='red', width=1.5), showlegend=False))
    fig.add_trace(go.Scatter(x=x_env[x_env>xt_coll], y=y_env[x_env>xt_coll], line=dict(color='green', width=1.5), showlegend=False))
    
    # Círculos
    m_s = (yc_o < res_c - 1e-3)
    m_f = ~m_s & (yc_o > 0.05)
    fig.add_trace(go.Scatter(x=np.where(m_s, xc_o, np.nan), y=np.where(m_s, yc_o, np.nan), line=dict(color='#1f77b4', width=2.5), name="Estável"))
    fig.add_trace(go.Scatter(x=np.where(~m_s, xc_o, np.nan), y=np.where(~m_s, yc_o, np.nan), line=dict(color='black', width=1, dash='dash'), name="Teórico"))
    
    # Arcos de Falha Colapsados
    fig.add_trace(go.Scatter(x=np.where(m_f & (xc_f < 0), xc_f, np.nan), y=np.where(m_f & (xc_f < 0), yc_f, np.nan), line=dict(color='blue', width=4), showlegend=False))
    fig.add_trace(go.Scatter(x=np.where(m_f & (xc_f >= 0) & (xc_f <= xt_coll), xc_f, np.nan), y=np.where(m_f & (xc_f >= 0) & (xc_f <= xt_coll), yc_f, np.nan), line=dict(color='red', width=4), showlegend=False))
    fig.add_trace(go.Scatter(x=np.where(m_f & (xc_f > xt_coll), xc_f, np.nan), y=np.where(m_f & (xc_f > xt_coll), yc_f, np.nan), line=dict(color='green', width=4), showlegend=False))
    
    # Trajetória e Ponto
    fig.add_trace(go.Scatter(x=p_x, y=p_y, line=dict(color='orange', width=1.5, dash='dash'), name="Trajetória"))
    fig.add_trace(go.Scatter(x=[sn_p], y=[tn_p], mode='markers', marker=dict(size=14, color='yellow' if falhou else '#2ca02c', line=dict(width=2, color='black')), showlegend=False))
    
    fig.update_layout(xaxis=dict(range=[-50, 250]), yaxis=dict(range=[0, 100], scaleanchor="x", scaleratio=1), template="plotly_white", height=500)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def plot_3d_block(params):
    """Visualização 3D estável com triangulação manual."""
    ang_rad = np.radians(params['ang_s1'])
    reg = params['regime']
    s1, s3 = params['s1'], params['s3']
    s2 = (s1 + s3) / 2

    # Eixos por regime
    if reg == 'Normal':
        e1, e2, e3 = np.array([0,0,1]), np.array([1,0,0]), np.array([0,1,0])
    elif reg == 'Transcorrente':
        e1, e2, e3 = np.array([0,1,0]), np.array([0,0,1]), np.array([1,0,0])
    else: # Reverso
        e1, e2, e3 = np.array([1,0,0]), np.array([0,1,0]), np.array([0,0,1])

    # Vetores Sn e Tau
    norm = e1 * np.cos(ang_rad) + e3 * np.sin(ang_rad)
    tau_dir = -e1 * np.sin(ang_rad) + e3 * np.cos(ang_rad)
    
    fig = go.Figure()

    # Cubo Wireframe
    v = np.array([[-40,-40,-50], [40,-40,-50], [40,40,-50], [-40,40,-50], [-40,-40,50], [40,-40,50], [40,40,50], [-40,40,50]])
    edges = [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)]
    for e in edges:
        fig.add_trace(go.Scatter3d(x=[v[e[0]][0], v[e[1]][0]], y=[v[e[0]][1], v[e[1]][1]], z=[v[e[0]][2], v[e[1]][2]], mode='lines', line=dict(color='black', width=2), showlegend=False))

    # Plano (Triangulação Manual 0-1-2 e 0-2-3)
    size = 42
    p1, p2 = -size * e2 - size * tau_dir, size * e2 - size * tau_dir
    p3, p4 = size * e2 + size * tau_dir, -size * e2 + size * tau_dir
    pts = np.array([p1, p2, p3, p4])
    
    fig.add_trace(go.Mesh3d(x=pts[:,0], y=pts[:,1], z=np.clip(pts[:,2], -50, 50), i=[0,0], j=[1,2], k=[2,3], color='lightblue', opacity=0.8, showlegend=False))

    # Função para Vetores
    def add_arrow(direction, color, name, magnitude, inward=True):
        scale = 0.25
        d = direction / (np.linalg.norm(direction) + 1e-9)
        if inward:
            end_p = d * 55
            start_p = d * (55 + magnitude * scale)
            arrow_d = -d
        else:
            start_p = np.array([0,0,0])
            end_p = d * (magnitude * scale + 15)
            arrow_d = d

        fig.add_trace(go.Scatter3d(x=[start_p[0], end_p[0]], y=[start_p[1], end_p[1]], z=[start_p[2], end_p[2]], mode='lines', line=dict(color=color, width=6), showlegend=False))
        fig.add_trace(go.Cone(x=[end_p[0]], y=[end_p[1]], z=[end_p[2]], u=[arrow_d[0]], v=[arrow_d[1]], w=[arrow_d[2]], colorscale=[[0, color], [1, color]], showscale=False, sizemode="absolute", sizeref=12))
        fig.add_trace(go.Scatter3d(x=[start_p[0]*1.15 if inward else end_p[0]*1.2], y=[start_p[1]*1.15 if inward else end_p[1]*1.2], z=[start_p[2]*1.15 if inward else end_p[2]*1.2], mode='text', text=[f"<b>{name}</b>"], textfont=dict(color=color, size=13), showlegend=False))

    add_arrow(e1, "blue", "S1", s1)
    add_arrow(e2, "green", "S2", s2)
    add_arrow(e3, "red", "S3", s3)
    add_arrow(norm, "black", "Sn", s1*np.cos(ang_rad)**2 + s3*np.sin(ang_rad)**2, False)
    add_arrow(tau_dir, "orange", "Tau", abs(s1-s3)/2*np.sin(2*ang_rad), False)

    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode='data', camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))), height=500, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
