import plotly.graph_objects as go
import streamlit as st
import numpy as np

def render_3d_block(params):
    with st.container(border=True):
        st.markdown('<div style="position: relative; height: 0px;"><div style="position: absolute; top: -5px; left: 0px; z-index: 10;"><span style="font-family: sans-serif; font-size: 1.1em; font-weight: bold; color: #333;">JocaMohr</span></div></div>', unsafe_allow_html=True)
        
        mergulho = params.get('val_mergulho', 60.0)
        ang_s1 = params.get('ang_s1', 30.0)
        reg = params.get('regime', 'Normal')
        s1, s3 = params.get('s1', 120.0), params.get('s3', 40.0)
        s2 = (s1 + s3) / 2
        
        rad_m = np.radians(mergulho)
        
        # Definição dos eixos conforme o regime tectônico
        if reg == 'Normal':
            n_vec = np.array([0, np.sin(rad_m), np.cos(rad_m)])
            f_dir = np.array([0, np.cos(rad_m), -np.sin(rad_m)])
            e1, e2, e3 = np.array([0,0,1]), np.array([1,0,0]), np.array([0,1,0])
        elif reg == 'Transcorrente':
            n_vec = np.array([np.cos(np.radians(ang_s1)), np.sin(np.radians(ang_s1)), 0])
            f_dir = np.array([-np.sin(np.radians(ang_s1)), np.cos(np.radians(ang_s1)), 0])
            e1, e2, e3 = np.array([0,1,0]), np.array([0,0,1]), np.array([1,0,0])
        else: # Reverso
            n_vec = np.array([np.sin(rad_m), 0, np.cos(rad_m)])
            f_dir = np.array([np.cos(rad_m), 0, -np.sin(rad_m)])
            e1, e2, e3 = np.array([1,0,0]), np.array([0,1,0]), np.array([0,0,1])

        fig = go.Figure()
        
        # Geometria do Bloco (X:80, Y:80, Z:100)
        v = np.array([[-40,-40,-50], [40,-40,-50], [40,40,-50], [-40,40,-50], 
                      [-40,-40,50], [40,-40,50], [40,40,50], [-40,40,50]])
        edges = [(0,1), (1,2), (2,3), (3,0), (4,5), (5,6), (6,7), (7,4), (0,4), (1,5), (2,6), (3,7)]
        
        for e in edges:
            fig.add_trace(go.Scatter3d(
                x=[v[e[0]][0], v[e[1]][0]], 
                y=[v[e[0]][1], v[e[1]][1]], 
                z=[v[e[0]][2], v[e[1]][2]], 
                mode='lines', line=dict(color='black', width=2), showlegend=False))

        # Geometria do Plano (Ajustado para sz=40 para não vazar do bloco de largura 80)
        sz = 40 
        cp = np.array([1, 0, 0]) if abs(n_vec[0]) < 0.9 else np.array([0, 1, 0])
        v1 = np.cross(n_vec, cp); v1 /= np.linalg.norm(v1)
        v2 = np.cross(n_vec, v1)
        pts = np.array([-sz*v1-sz*v2, sz*v1-sz*v2, sz*v1+sz*v2, -sz*v1+sz*v2])
        
        fig.add_trace(go.Mesh3d(
            x=pts[:,0], y=pts[:,1], z=pts[:,2], 
            i=[0,0], j=[1,2], k=[2,3], 
            color='lightblue', opacity=0.6, name="Plano de Fraqueza"))

        def add_arrow(direction, color, name, magnitude, inward=True):
            if np.linalg.norm(direction) < 0.01: return
            sc, d = 0.22, direction / np.linalg.norm(direction)
            if inward: 
                ep, sp, ar_d = d*55, d*(55+magnitude*sc), -d
            else: 
                sp, ep, ar_d = np.array([0,0,0]), d*(magnitude*sc+20), d
            
            fig.add_trace(go.Scatter3d(
                x=[sp[0], ep[0]], y=[sp[1], ep[1]], z=[sp[2], ep[2]], 
                mode='lines', line=dict(color=color, width=6), showlegend=False))
            
            fig.add_trace(go.Cone(
                x=[ep[0]], y=[ep[1]], z=[ep[2]], 
                u=[ar_d[0]], v=[ar_d[1]], w=[ar_d[2]], 
                colorscale=[[0, color], [1, color]], showscale=False, 
                sizemode="absolute", sizeref=12))
            
            fig.add_trace(go.Scatter3d(
                x=[ep[0]+d[0]*12], y=[ep[1]+d[1]*12], z=[ep[2]+d[2]*12], 
                mode='text', text=[f"<b>{name}</b>"], 
                textfont=dict(color=color, size=14), showlegend=False))

        # Adição das setas de tensão
        add_arrow(e1, "blue", "S1", s1)
        add_arrow(e2, "green", "S2", s2)
        add_arrow(e3, "red", "S3", s3)
        add_arrow(n_vec, "black", "Sn", s1, False)
        
        t_mag = abs(s1-s3)/2 * np.sin(2 * np.radians(ang_s1))
        if t_mag > 0.1: 
            add_arrow(f_dir, "orange", "Tau", t_mag, False)
        
        # Configuração de layout com ESCALA 1:1 (aspectmode='data')
        fig.update_layout(
            scene=dict(
                xaxis=dict(visible=False), 
                yaxis=dict(visible=False), 
                zaxis=dict(visible=False), 
                aspectmode='data', # Mantém proporções físicas reais dos eixos
                camera=dict(projection=dict(type='orthographic'))
            ), 
            height=500, 
            margin=dict(l=0, r=0, t=0, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
