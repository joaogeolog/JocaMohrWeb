import plotly.graph_objects as go
import streamlit as st
import numpy as np

def plot_mohr(x_env, y_env, xt_coll, xc_s, yc_s, xc_f, yc_f, env_high, sn_p, tn_p, p_x, p_y, falhou, params):
    with st.container(border=True):
        fig = go.Figure()
        fig.add_shape(type="line", x0=-50, y0=0, x1=250, y1=0, line=dict(color="black", width=2))
        fig.add_shape(type="line", x0=0, y0=0, x1=0, y1=100, line=dict(color="black", width=2))
        m_tra, m_cis, m_col = x_env <= 0, (x_env > 0) & (x_env <= xt_coll), x_env > xt_coll
        fig.add_trace(go.Scatter(x=x_env[m_tra], y=y_env[m_tra], line=dict(color='blue', width=2.5), name="Tração"))
        fig.add_trace(go.Scatter(x=x_env[m_cis], y=y_env[m_cis], line=dict(color='red', width=2.5), name="Cisalhamento"))
        fig.add_trace(go.Scatter(x=x_env[m_col], y=y_env[m_col], line=dict(color='green', width=2.5), name="Colapso"))
        try:
            if env_high is not None and any(env_high):
                fig.add_trace(go.Scatter(x=x_env[env_high], y=y_env[env_high], line=dict(color='yellow', width=5, opacity=0.3), showlegend=False))
        except: pass
        fig.add_trace(go.Scatter(x=xc_s, y=yc_s, line=dict(color='#1f77b4', width=2.5), name="Estável"))
        fig.add_trace(go.Scatter(x=xc_f, y=yc_f, line=dict(color='black', width=1.2, dash='dash'), name="Falha"))
        fig.add_trace(go.Scatter(x=p_x, y=p_y, line=dict(color='orange', width=1.5, dash='dot'), name="Trajetória"))
        fig.add_trace(go.Scatter(x=[sn_p], y=[tn_p], mode='markers', marker=dict(size=14, color='yellow' if falhou else 'lime', line=dict(width=2, color='black')), showlegend=False))
        fig.update_layout(xaxis=dict(range=[-50, 250], title="Tensão Normal Efetiva, σ'n (MPa)"), yaxis=dict(range=[0, 100], scaleanchor="x", scaleratio=1, title="Tensão Cisalhante, τ (MPa)"), template="plotly_white", height=500, margin=dict(l=10, r=10, t=10, b=10), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
        st.plotly_chart(fig, use_container_width=True)

def plot_3d_block(params):
    with st.container(border=True):
        st.markdown('<div style="position: relative; height: 0px;"><div style="position: absolute; top: -5px; left: 0px; z-index: 10;"><span style="font-family: sans-serif; font-size: 1.1em; font-weight: bold; color: #333;">JocaMohr</span></div></div>', unsafe_allow_html=True)
        mergulho = params.get('val_mergulho', 60.0)
        ang_s1 = params.get('ang_s1', 30.0)
        reg = params.get('regime', 'Normal')
        s1, s3 = params.get('s1', 120.0), params.get('s3', 40.0)
        s2 = (s1 + s3) / 2
        rad_m = np.radians(mergulho)
        rad_s1 = np.radians(ang_s1)

        if reg == 'Normal':
            n_vec = np.array([0, np.sin(rad_m), np.cos(rad_m)])
            f_dir = np.array([0, np.cos(rad_m), -np.sin(rad_m)])
            e1, e2, e3 = np.array([0,0,1]), np.array([1,0,0]), np.array([0,1,0])
        elif reg == 'Transcorrente':
            n_vec = np.array([np.cos(rad_m), np.sin(rad_m), 0])
            f_dir = np.array([-np.sin(rad_m), np.cos(rad_m), 0])
            e1, e2, e3 = np.array([0,1,0]), np.array([0,0,1]), np.array([1,0,0])
        else:
            n_vec = np.array([np.sin(rad_m), 0, np.cos(rad_m)])
            f_dir = np.array([np.cos(rad_m), 0, -np.sin(rad_m)])
            e1, e2, e3 = np.array([1,0,0]), np.array([0,1,0]), np.array([0,0,1])

        fig = go.Figure()
        v = np.array([[-40,-40,-50], [40,-40,-50], [40,40,-50], [-40,40,-50], [-40,-40,50], [40,-40,50], [40,40,50], [-40,40,50]])
        edges = [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)]
        for e in edges: fig.add_trace(go.Scatter3d(x=[v[e[0]][0], v[e[1]][0]], y=[v[e[0]][1], v[e[1]][1]], z=[v[e[0]][2], v[e[1]][2]], mode='lines', line=dict(color='black', width=2), showlegend=False))

        sz = 45
        cp = np.array([1, 0, 0]) if abs(n_vec[0]) < 0.9 else np.array([0, 1, 0])
        v1 = np.cross(n_vec, cp)
        v1 /= np.linalg.norm(v1)
        v2 = np.cross(n_vec, v1)
        p_pts = np.array([-sz*v1-sz*v2, sz*v1-sz*v2, sz*v1+sz*v2, -sz*v1+sz*v2])
        fig.add_trace(go.Mesh3d(x=p_pts[:,0], y=p_pts[:,1], z=p_pts[:,2], i=[0,0], j=[1,2], k=[2,3], color='lightblue', opacity=0.6))

        def add_arrow(direction, color, name, magnitude, inward=True):
            if np.linalg.norm(direction) < 0.01: return
            scale, d = 0.22, direction / np.linalg.norm(direction)
            if inward: ep, sp, ar_d = d*55, d*(55+magnitude*scale), -d
            else: sp, ep, ar_d = np.array([0,0,0]), d*(magnitude*scale+20), d
            fig.add_trace(go.Scatter3d(x=[sp[0], ep[0]], y=[sp[1], ep[1]], z=[sp[2], ep[2]], mode='lines', line=dict(color=color, width=6), showlegend=False))
            fig.add_trace(go.Cone(x=[ep[0]], y=[ep[1]], z=[ep[2]], u=[ar_d[0]], v=[ar_d[1]], w=[ar_d[2]], colorscale=[[0, color], [1, color]], showscale=False, sizemode="absolute", sizeref=12))
            fig.add_trace(go.Scatter3d(x=[ep[0]+d[0]*12], y=[ep[1]+d[1]*12], z=[ep[2]+d[2]*12], mode='text', text=[f"<b>{name}</b>"], textfont=dict(color=color, size=14), showlegend=False))

        add_arrow(e1, "blue", "S1", s1); add_arrow(e2, "green", "S2", s2); add_arrow(e3, "red", "S3", s3)
        add_arrow(n_vec, "black", "Sn", s1, False)
        t_mag = abs(s1-s3)/2 * np.sin(2 * rad_s1)
        if t_mag > 0.1: add_arrow(f_dir, "orange", "Tau", t_mag, False)

        fig.update_layout(scene=dict(xaxis=dict(visible=False), yaxis=dict(visible=False), zaxis=dict(visible=False), aspectmode='cube', camera=dict(projection=dict(type='orthographic'))), height=500, margin=dict(l=0, r=0, t=0, b=0))
        st.plotly_chart(fig, use_container_width=True)
