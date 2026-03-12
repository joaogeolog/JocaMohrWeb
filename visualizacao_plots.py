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
    
    # Rótulos
    fig.add_annotation(x=-params['ts'] - 15, y=30, text="<b>Ruptura por<br>Tração</b>", font=dict(color="blue", size=10), showarrow=False)
    fig.add_annotation(x=xt_coll/2, y=90, text="<b>Cisalhamento</b>", font=dict(color="red", size=10), showarrow=False)
    fig.add_annotation(x=params['pc'] + 20, y=30, text="<b>Colapso<br>de poros</b>", font=dict(color="green", size=10), showarrow=False)
    
    fig.update_layout(xaxis=dict(range=[-50, 250]), yaxis=dict(range=[0, 100], scaleanchor="x", scaleratio=1), template="plotly_white", height=450, showlegend=False)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def plot_3d_block(params):
    """Visualização 3D com correção matemática da Normal e Tau."""
    ang_rad = np.radians(params['ang_s1'])
    reg = params['regime']
    s1, s3 = params['s1'], params['s3']
    s2 = (s1 + s3) / 2 

    # 1. Definição dos eixos por regime
    if reg == 'Normal':
        v1, v2, v3 = np.array([0,0,1]), np.array([1,0,0]), np.array([0,1,0])
    elif reg == 'Transcorrente':
        v1, v2, v3 = np.array([0,1,0]), np.array([0,0,1]), np.array([1,0,0])
    else: # Reverso
        v1, v2, v3 = np.array([1,0,0]), np.array([0,1,0]), np.array([0,0,1])

    # 2. Cálculo da Normal e Tau Direção (Rigor Geomecânico)
    # Sn é ortogonal ao plano rotacionado
    norm = v1 * np.cos(ang_rad) + v3 * np.sin(ang_rad)
    # Tau é a direção de máximo cisalhamento no plano (contido no plano v1-v3)
    tau_dir = -v1 * np.sin(ang_rad) + v3 * np.cos(ang_rad)
    
    fig = go.Figure()

    # 3. CUBO WIREFRAME
    v = np.array([[-40,-40,-50], [40,-40,-50], [40,40,-50], [-40,40,-50], [-40,-40,50], [40,-40,50], [40,40,50], [-40,40,50]])
    edges = [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)]
    for e in edges:
        fig.add_trace(go.Scatter3d(x=[v[e[0]][0], v[e[1]][0]], y=[v[e[0]][1], v[e[1]][1]], z=[v[e[0]][2], v[e[1]][2]], mode='lines', line=dict(color='black', width=2), showlegend=False, hoverinfo='skip'))

    # 4. PLANO CORRIGIDO
    # Gerando o plano perpendicular à 'norm' calculada
    p_pts = np.array([[-40,-40,0], [40,-40,0], [40,40,0], [-40,40,0]])
    # Aplicando a mesma rotação da Normal aos pontos do plano
    # Plano deve ser ortogonal a Sn
    size = 40
    if reg == 'Transcorrente': # Rotação em Z
        px = np.array([-size, size, size, -size]) * np.cos(ang_rad)
        py = np.array([-size, -size, size, size]) # Eixo fixo
        pz = np.array([-50, -50, 50, 50])
        fig.add_trace(go.Mesh3d(x=px, y=py, z=pz, color='lightblue', opacity=0.8, showlegend=False))
    else: # Rotação em Y (Normal/Reverso)
        px = np.array([-size, size, size, -size])
        py = np.array([-size, -size, size, size])
        pz = px * np.tan(ang_rad) # Inclinação alfa
        # Clipagem simples no eixo Z
        pz = np.clip(pz, -50, 50)
        fig.add_trace(go.Mesh3d(x=px, y=py, z=pz, color='lightblue', opacity=0.8, showlegend=False))

    # 5. VETORES
    def add_full_arrow(direction, color, name, magnitude, inward=True):
        scale = 0.2
        d = direction / np.linalg.norm(direction)
        if inward: # S1, S2, S3
            end_p = d * 55
            start_p = d * (55 + magnitude * scale)
            arrow_d = -d
        else: # Sn, Tau (partindo da origem)
            start_p = np.array([0,0,0])
            end_p = d * (magnitude * scale + 10)
            arrow_d = d

        fig.add_trace(go.Scatter3d(x=[start_p[0], end_p[0]], y=[start_p[1], end_p[1]], z=[start_p[2], end_p[2]], mode='lines', line=dict(color=color, width=6), showlegend=False))
        fig.add_trace(go.Cone(x=[end_p[0]], y=[end_p[1]], z=[end_p[2]], u=[arrow_d[0]], v=[arrow_d[1]], w=[arrow_d[2]], colorscale=[[0, color], [1, color]], showscale=False, sizemode="absolute", sizeref=12))
        fig.add_trace(go.Scatter3d(x=[start_p[0]*1.1 if inward else end_p[0]*1.2], y=[start_p[1]*1.1 if inward else end_p[1]*1.2], z=[start_p[2]*1.1 if inward else end_p[2]*1.2], mode='text', text=[f"<b>{name}</b>"], textfont=dict(color=color, size=13), showlegend=False))

    add_full_arrow(v1, "blue", "S1", s1, inward=True)
    add_full_arrow(v2, "green", "S2", s2, inward=True)
    add_full_arrow(v3, "red", "S3", s3, inward=True)
    
    sn_val = s1*np.cos(ang_rad)**2 + s3*np.sin(ang_rad)**2
    tau_val = abs(s1-s3)/2 * np.sin(2*ang_rad)
    
    add_full_arrow(norm, "black", "Sn", sn_val, inward=False)
    if tau_val > 0.5:
        add_full_arrow(tau_dir, "orange", "Tau", tau_val, inward=False)

    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode='data', camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))), height=500, margin=dict(l=0, r=0, t=0, b=0))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
