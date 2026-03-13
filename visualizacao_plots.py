import plotly.graph_objects as go
import streamlit as st
import numpy as np

def plot_mohr(x_env, y_env, xt_coll, xc_f, yc_f, res_c, xc_o, yc_o, sn_p, tn_p, p_x, p_y, falhou, params):
    # (Mantido o código anterior do Mohr, que você confirmou estar correto)
    fig = go.Figure()
    fig.add_shape(type="line", x0=-50, y0=0, x1=250, y1=0, line=dict(color="black", width=2))
    for x, y, c in [(x_env[x_env<=0], y_env[x_env<=0], 'blue'), 
                    (x_env[(x_env>0) & (x_env<=xt_coll)], y_env[(x_env>0) & (x_env<=xt_coll)], 'red'), 
                    (x_env[x_env>xt_coll], y_env[x_env>xt_coll], 'green')]:
        fig.add_trace(go.Scatter(x=x, y=y, line=dict(color=c, width=1.5), showlegend=False))
    
    m_s = (yc_o < res_c - 1e-3); m_f = ~m_s & (yc_o > 0.05)
    fig.add_trace(go.Scatter(x=np.where(m_s, xc_o, np.nan), y=np.where(m_s, yc_o, np.nan), line=dict(color='#1f77b4', width=2.5), name="Estável"))
    fig.add_trace(go.Scatter(x=np.where(~m_s, xc_o, np.nan), y=np.where(~m_s, yc_o, np.nan), line=dict(color='black', width=1, dash='dash'), name="Teórico"))
    
    for cond, c in [(m_f & (xc_f < 0), 'blue'), (m_f & (xc_f >= 0) & (xc_f <= xt_coll), 'red'), (m_f & (xc_f > xt_coll), 'green')]:
        fig.add_trace(go.Scatter(x=np.where(cond, xc_f, np.nan), y=np.where(cond, yc_f, np.nan), line=dict(color=c, width=4), showlegend=False))
    
    fig.add_trace(go.Scatter(x=p_x, y=p_y, line=dict(color='orange', width=1.5, dash='dash'), name="Trajetória"))
    fig.add_trace(go.Scatter(x=[sn_p], y=[tn_p], mode='markers', marker=dict(size=14, color='yellow' if falhou else '#2ca02c', line=dict(width=2, color='black')), showlegend=False))
    
    fig.update_layout(xaxis=dict(range=[-50, 250]), yaxis=dict(range=[0, 100], scaleanchor="x", scaleratio=1), template="plotly_white", height=500)
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

def plot_3d_block(params):
    # AQUI ESTÁ A CORREÇÃO: ang_s1 é o ângulo com o eixo de S1
    ang_s1_rad = np.radians(params['ang_s1'])
    reg = params['regime']
    s1, s3 = params['s1'], params['s3']
    s2 = (s1 + s3) / 2

    # Definição dos eixos principais (Anderson)
    if reg == 'Normal':
        # S1 é Vertical (Z), S2 e S3 Horizontais (X, Y)
        e1, e2, e3 = np.array([0,0,1]), np.array([1,0,0]), np.array([0,1,0])
    elif reg == 'Transcorrente':
        # S2 é Vertical (Z), S1 e S3 Horizontais (Y, X)
        e1, e2, e3 = np.array([0,1,0]), np.array([0,0,1]), np.array([1,0,0])
    else: # Reverso
        # S3 é Vertical (Z), S1 e S2 Horizontais (X, Y)
        e1, e2, e3 = np.array([1,0,0]), np.array([0,1,0]), np.array([0,0,1])

    # O vetor normal (Sn) deve estar a 'ang_s1' do eixo e1, no plano e1-e3
    norm = e1 * np.cos(ang_s1_rad) + e3 * np.sin(ang_s1_rad)
    tau_dir = -e1 * np.sin(ang_s1_rad) + e3 * np.cos(ang_s1_rad)
    
    fig = go.Figure()

    # Cubo Wireframe
    v = np.array([[-40,-40,-50], [40,-40,-50], [40,40,-50], [-40,40,-50], [-40,-40,50], [40,-40,50], [40,40,50], [-40,40,50]])
    for e in [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)]:
        fig.add_trace(go.Scatter3d(x=[v[e[0]][0], v[e[1]][0]], y=[v[e[0]][1], v[e[1]][1]], z=[v[e[0]][2], v[e[1]][2]], mode='lines', line=dict(color='black', width=2), showlegend=False))

    # Construção do Plano: agora o plano é ortogonal à 'norm' calculada
    # Usamos e2 e tau_dir como vetores diretores da face do plano
    size = 42
    p1 = -size * e2 - size * tau_dir
    p2 =  size * e2 - size * tau_dir
    p3 =  size * e2 + size * tau_dir
    p4 = -size * e2 + size * tau_dir
    
    pts = np.array([p1, p2, p3, p4])
    fig.add_trace(go.Mesh3d(x=pts[:,0], y=pts[:,1], z=np.clip(pts[:,2],-50,50), i=[0,0], j=[1,2], k=[2,3], color='lightblue', opacity=0.8, showlegend=False))

    # Vetores (Sn e Tau)
    def arrow(dir, col, name, mag, inv=True):
        d = dir / (np.linalg.norm(dir) + 1e-9); sc = 0.25
        st_p, en_p, ar_d = (d*(55+mag*sc), d*55, -d) if inv else ([0,0,0], d*(mag*sc+15), d)
        fig.add_trace(go.Scatter3d(x=[st_p[0], en_p[0]], y=[st_p[1], en_p[1]], z=[st_p[2], en_p[2]], mode='lines', line=dict(color=col, width=6), showlegend=False))
        fig.add_trace(go.Cone(x=[en_p[0]], y=[en_p[1]], z=[en_p[2]], u=[ar_d[0]], v=[ar_d[1]], w=[ar_d[2]], colorscale=[[0, col], [1, col]], showscale=False, sizemode="absolute", sizeref=12))

    arrow(e1, "blue", "S1", s1); arrow(e2, "green", "S2", s2); arrow(e3, "red", "S3", s3)
    arrow(norm, "black", "Sn", s1*np.cos(ang_s1_rad)**2 + s3*np.sin(ang_s1_rad)**2, False)
    arrow(tau_dir, "orange", "Tau", abs(s1-s3)/2*np.sin(2*ang_s1_rad), False)

    fig.update_layout(scene=dict(xaxis_visible=False, yaxis_visible=False, zaxis_visible=False, aspectmode='data', camera=dict(eye=dict(x=1.5, y=1.5, z=1.5))), height=500, margin=dict(l=0,r=0,t=0,b=0))
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
