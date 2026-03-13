import plotly.graph_objects as go
import streamlit as st
import numpy as np

def plot_mohr(x_env, y_env, xt_coll, xc_s, yc_s, xc_f, yc_f, env_high, sn_p, tn_p, p_x, p_y, falhou, params):
    """Interface do Diagrama de Mohr restaurada."""
    with st.container(border=True):
        fig = go.Figure()
        fig.add_shape(type="line", x0=-50, y0=0, x1=250, y1=0, line=dict(color="black", width=2))
        fig.add_shape(type="line", x0=0, y0=0, x1=0, y1=100, line=dict(color="black", width=2))
        
        # Envoltórias
        fig.add_trace(go.Scatter(x=x_env[x_env<=0], y=y_env[x_env<=0], line=dict(color='blue', width=2), name="Ruptura por tração"))
        fig.add_trace(go.Scatter(x=x_env[(x_env>0) & (x_env<=xt_coll)], y=y_env[(x_env>0) & (x_env<=xt_coll)], line=dict(color='red', width=2), name="Ruptura por cisalhamento"))
        fig.add_trace(go.Scatter(x=x_env[x_env>xt_coll], y=y_env[x_env>xt_coll], line=dict(color='green', width=2), name="Colapso de poros"))
        
        # Círculo: Azul para estável, Tracejado Preto para o que 'passou' da borda
        fig.add_trace(go.Scatter(x=xc_s, y=yc_s, line=dict(color='#1f77b4', width=2.5), name="Estado Estável"))
        fig.add_trace(go.Scatter(x=xc_f, y=yc_f, line=dict(color='black', width=1.2, dash='dash'), name="Círculo (Falha)"))
        
        # Trajetória (Caminho)
        fig.add_trace(go.Scatter(x=p_x, y=p_y, line=dict(color='orange', width=1.5, dash='dot'), name="Trajetória"))
        
        # Ponto do Plano (sempre no círculo ou travado na borda)
        fig.add_trace(go.Scatter(x=[sn_p], y=[tn_p], mode='markers', 
                                 marker=dict(size=14, color='yellow' if falhou else 'lime', 
                                 line=dict(width=2, color='black')), showlegend=False))
        
        fig.update_layout(
            xaxis=dict(range=[-50, 250], title="σ'n (MPa)"),
            yaxis=dict(range=[0, 100], scaleanchor="x", scaleratio=1, title="τ (MPa)"),
            template="plotly_white", height=500, margin=dict(l=10, r=10, t=10, b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig, use_container_width=True)

def plot_3d_block(params):
    """Visualização 3D blindada contra KeyError/AttributeError com título interno."""
    with st.container(border=True):
        # Título no canto superior esquerdo dentro do container
        st.markdown("<h3 style='margin: -5px 0px 5px 0px; font-size: 1.1em; color: #333;'>JocaMohr</h3>", unsafe_allow_html=True)
        
        # Fallbacks seguros
        a_s1 = params.get('ang_s1', params.get('ang', 30.0))
        reg = params.get('regime', 'Normal')
        s1 = params.get('s1', 100.0)
        s3 = params.get('s3', 40.0)
        
        theta_rad = np.radians(a_s1)
        merg_rad = np.radians(90 - a_s1)
        s2, lim = (s1 + s3) / 2, 120 

        if reg == 'Normal': e1, e2, e3 = np.array([0,0,1]), np.array([1,0,0]), np.array([0,1,0])
        elif reg == 'Transcorrente': e1, e2, e3 = np.array([0,1,0]), np.array([0,0,1]), np.array([1,0,0])
        else: e1, e2, e3 = np.array([1,0,0]), np.array([0,1,0]), np.array([0,0,1])

        f_dir = -e1 * np.sin(merg_rad) + e3 * np.cos(merg_rad)
        n_vec = e1 * np.cos(merg_rad) + e3 * np.sin(merg_rad)
        
        fig = go.Figure()

        box_v = np.array([[-lim,-lim,-lim], [lim,-lim,-lim], [lim,lim,-lim], [-lim,lim,-lim], [-lim,-lim,lim], [lim,-lim,lim], [lim,lim,lim], [-lim,lim,lim]])
        edges = [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)]
        for e in edges:
            fig.add_trace(go.Scatter3d(x=[box_v[e[0]][0], box_v[e[1]][0]], y=[box_v[e[0]][1], box_v[e[1]][1]], z=[box_v[e[0]][2], box_v[e[1]][2]], 
                                     mode='lines', line=dict(color='rgba(200,200,200,0.3)', width=1, dash='dash'), showlegend=False))
        
        v = np.array([[-40,-40,-50], [40,-40,-50], [40,40,-50], [-40,40,-50], [-40,-40,50], [40,-40,50], [40,40,50], [-40,40,50]])
        for e in edges:
            fig.add_trace(go.Scatter3d(x=[v[e[0]][0], v[e[1]][0]], y=[v[e[0]][1], v[e[1]][1]], z=[v[e[0]][2], v[e[1]][2]], 
                                     mode='lines', line=dict(color='black', width=2), showlegend=False))

        sz = 42
        pts = np.array([-sz*e2-sz*f_dir, sz*e2-sz*f_dir, sz*e2+sz*f_dir, -sz*e2+sz*f_dir])
        fig.add_trace(go.Mesh3d(x=pts[:,0], y=pts[:,1], z=np.clip(pts[:,2], -50, 50), i=[0,0], j=[1,2], k=[2,3], color='lightblue', opacity=0.8))

        def add_arrow(direction, color, name, magnitude, inward=True):
            scale, d = 0.22, direction / (np.linalg.norm(direction) + 1e-9)
            if inward: ep, sp, ar_d, off = d*55, d*(55+magnitude*scale), -d, 15
            else: sp, ep, ar_d, off = np.array([0,0,0]), d*(magnitude*scale+15), d, 12
            fig.add_trace(go.Scatter3d(x=[sp[0], ep[0]], y=[sp[1], ep[1]], z=[sp[2], ep[2]], mode='lines', line=dict(color=color, width=6), showlegend=False))
            fig.add_trace(go.Cone(x=[ep[0]], y=[ep[1]], z=[ep[2]], u=[ar_d[0]], v=[ar_d[1]], w=[ar_d[2]], 
                                 colorscale=[[0, color], [1, color]], showscale=False, sizemode="absolute", sizeref=12))
            fig.add_trace(go.Scatter3d(x=[(sp if inward else ep)[0]+d[0]*off], y=[(sp if inward else ep)[1]+d[1]*off], z=[(sp if inward else ep)[2]+d[2]*off], 
                                     mode='text', text=[f"<b>{name}</b>"], textfont=dict(color=color, size=14), showlegend=False))

        add_arrow(e1, "blue", "S1", s1)
        add_arrow(e2, "green", "S2", s2)
        add_arrow(e3, "red", "S3", s3)
        add_arrow(n_vec, "black", "Sn", s1, False)
        
        t_val = abs(s1-s3)/2*np.sin(2*theta_rad)
        if t_val > 0.1: add_arrow(f_dir, "orange", "Tau", t_val, False)

        fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), aspectmode='cube'),
                          height=500, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)
