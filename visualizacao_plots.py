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
    """Renderiza o bloco 3D com wireframe do cubo, plano inclinado e vetores coloridos."""
    ang_rad = np.radians(params['ang_s1'])
    reg = params['regime']
    s1, s3 = params['s1'], params['s3']
    s2 = (s1 + s3) / 2 # Tensão intermediária teórica

    # Lógica de eixos original por regime tectônico
    # Normal: S1 vertical, Transcorrente: S2 vertical, Reverso: S3 vertical
    v1, v2, v3 = ([0,0,1],[1,0,0],[0,1,0]) if reg=='Normal' else (([0,1,0],[0,0,1],[1,0,0]) if reg=='Transcorrente' else ([1,0,0],[0,1,0],[0,0,1]))
    
    # Vetor Normal ao plano inclinado de theta em relação a S1
    norm = np.array(v1)*np.cos(ang_rad) + np.array(v3)*np.sin(ang_rad)
    
    fig = go.Figure()

    # 1. DESENHO DO CUBO (Wireframe manual das 12 arestas)
    # Definindo as coordenadas dos 8 vértices
    vertices = np.array([[-40,-40,-50], [40,-40,-50], [40,40,-50], [-40,40,-50],
                         [-40,-40,50], [40,-40,50], [40,40,50], [-40,40,50]])
    # Definindo as 12 arestas que conectam os vértices
    edges = [(0,1), (1,2), (2,3), (3,0), # Base inferior
             (4,5), (5,6), (6,7), (7,4), # Base superior
             (0,4), (1,5), (2,6), (3,7)] # Colunas verticais
    
    for edge in edges:
        fig.add_trace(go.Scatter3d(
            x=[vertices[edge[0]][0], vertices[edge[1]][0]],
            y=[vertices[edge[0]][1], vertices[edge[1]][1]],
            z=[vertices[edge[0]][2], vertices[edge[1]][2]],
            mode='lines', line=dict(color='black', width=2.5), showlegend=False, hoverinfo='skip'))

    # 2. PLANO DE FRATURA (Mesh3d inclinado)
    # Criando um plano que rotaciona no eixo intermediário (v2)
    p_size = 60 # Tamanho do plano para garantir que clipa o bloco
    
    # Rotação baseada no ângulo crítico (ang_rad) e no eixo intermediário do regime
    # Simplificado: plano rotaciona em Y no regime Normal e Reverso, e em Z no Transcorrente
    x_p = np.array([[-p_size, p_size, p_size, -p_size]])
    y_p = np.array([[-p_size, -p_size, p_size, p_size]])
    
    if reg == 'Transcorrente':
        # Rotaciona em Z
        z_p = np.zeros_like(x_p)
        x_p_r = x_p*np.cos(ang_rad) - y_p*np.sin(ang_rad)
        y_p_r = x_p*np.sin(ang_rad) + y_p*np.cos(ang_rad)
        fig.add_trace(go.Mesh3d(x=x_p_r[0], y=y_p_r[0], z=z_p[0], 
                                color='lightblue', opacity=0.7, name="Plano", showlegend=False))
    else:
        # Rotaciona em Y (Normal e Reverso)
        z_p = x_p * np.tan(ang_rad) 
        fig.add_trace(go.Mesh3d(x=x_p[0], y=y_p[0], z=z_p[0], 
                                color='lightblue', opacity=0.7, name="Plano", showlegend=False))

    # 3. VETORES DE TENSÃO (Cones coloridos: S1 Azul, S2 Verde, S3 Vermelho)
    def add_arrow(direction, color, name, scale):
        # Direção normalizada * 60 para posicionar a ponta fora do bloco
        pos = direction / np.linalg.norm(direction) * 60 
        fig.add_trace(go.Cone(x=[pos[0]], y=[pos[1]], z=[pos[2]],
                              u=[direction[0]*scale], v=[direction[1]*scale], w=[direction[2]*scale],
                              colorscale=[[0, color], [1, color]], showscale=False, name=name))

    # Escala baseada na magnitude das tensões (s1 e s3)
    max_s = max(s1, s3)
    scale_factor = 30 / max_s if max_s > 0 else 1
    
    add_arrow(np.array(v1)*s1, "blue", "S1", scale_factor)
    add_arrow(np.array(v2)*s2, "green", "S2", scale_factor)
    add_arrow(np.array(v3)*s3, "red", "S3", scale_factor)

    # 4. COMPONENTES LOCAIS (Sn Preto, Tau Laranja)
    sn_v = s1*np.cos(ang_rad)**2 + s3*np.sin(ang_rad)**2
    tau_v = abs(s1-s3)/2 * np.sin(2*ang_rad)
    # Direção de Tau é perpendicular à Normal no plano S1-S3
    tau_dir = -np.array(v1)*np.sin(ang_rad) + np.array(v3)*np.cos(ang_rad)
    
    # Posicionando Sn e Tau na superfície do bloco para clareza
    add_arrow(norm*sn_v, "black", "Sn", scale_factor)
    add_arrow(tau_dir*tau_v, "orange", "Tau", scale_factor)

    # 5. CONFIGURAÇÃO DE LAYOUT 3D
    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False,
                                 aspectmode='data', # Mantém a proporção real 1:1:1
                                 camera=dict(eye=dict(x=1.3, y=1.3, z=1.3))), # Câmera isométrica
                      height=500, margin=dict(l=0, r=0, t=0, b=0))
    
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
