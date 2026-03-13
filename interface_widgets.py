import streamlit as st

DEFAULTS = {'s1': 120.0, 's3': 40.0, 'pp': 20.0, 'alpha': 1.0, 'c': 15.0, 'phi': 30.0, 'ts': 10.0, 'pc': 180.0, 'ang': 30.0, 'regime': 'Normal'}

def sync_widgets(s, t, c):
    val = st.session_state[s]
    if c == 'val_s1':
        s3_at = st.session_state.get('val_s3', DEFAULTS['s3'])
        if val < s3_at: val = s3_at
    elif c == 'val_s3':
        s1_at = st.session_state.get('val_s1', DEFAULTS['s1'])
        if val > s1_at: val = s1_at
    st.session_state[c] = st.session_state[t] = st.session_state[s] = val

def reset_section(keys):
    for k in keys:
        for pfx in ['val_', 'slide_', 'num_']:
            st.session_state[pfx + k] = float(DEFAULTS[k])
    if 'ang' in keys:
        st.session_state.path_x, st.session_state.path_y, st.session_state.ponto_fisico = [], [], {'sn': 0.0, 'tn': 0.0}

def dual_input(label, min_v, max_v, key_p, step=1.0):
    s_key, n_key, base_key = f"slide_{key_p}", f"num_{key_p}", f"val_{key_p}"
    if base_key not in st.session_state:
        st.session_state[base_key] = st.session_state[s_key] = st.session_state[n_key] = float(DEFAULTS[key_p])
    
    c_l, c_s, c_n = st.columns([1, 2, 1])
    c_l.markdown(f"<p style='font-size:0.8em; margin-bottom: -15px;'>{label}</p>", unsafe_allow_html=True)
    c_s.slider(label, float(min_v), float(max_v), step=float(step), key=s_key, on_change=sync_widgets, args=(s_key, n_key, base_key), label_visibility="collapsed")
    c_n.number_input(label, float(min_v), float(max_v), step=float(step), key=n_key, on_change=sync_widgets, args=(n_key, s_key, base_key), label_visibility="collapsed")
    return st.session_state[base_key]

def render_bottom_interface():
    # Estilo CSS para subir os elementos e remover espaços inúteis
    st.markdown("""
        <style>
            .stSlider { margin-bottom: -20px; }
            .stNumberInput { margin-bottom: -20px; }
            [data-testid="stVerticalBlock"] > div { padding-top: 0.1rem; padding-bottom: 0.1rem; }
            div[data-testid="stForm"] { padding: 0.5rem; }
        </style>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        
        with c1:
            hdr, btn = st.columns([2, 1])
            hdr.markdown("<b style='font-size:0.8em;'>1. TENSÕES (MPa)</b>", unsafe_allow_html=True)
            if btn.button("Reiniciar", key="res_tens"): reset_section(['s1', 's3', 'pp'])
            dual_input("S1 (MPa)", 0, 250, 's1')
            dual_input("S3 (MPa)", 0, 250, 's3')
            dual_input("P. Poros (MPa)", 0, 100, 'pp')
            
        with c2:
            hdr, btn = st.columns([2, 1])
            hdr.markdown("<b style='font-size:0.8em;'>2. ROCHA</b>", unsafe_allow_html=True)
            if btn.button("Reiniciar", key="res_roc"): reset_section(['c', 'phi', 'ts', 'pc', 'alpha'])
            dual_input("Coesão (MPa)", 0, 100, 'c')
            dual_input("Atrito (°)", 0, 90, 'phi')
            dual_input("Tração (MPa)", 0, 50, 'ts')
            dual_input("Colapso (MPa)", 0, 500, 'pc')
            dual_input("Biot (adim.)", 0.0, 1.0, 'alpha', step=0.01)
            
        with c3:
            hdr, btn = st.columns([2, 1])
            hdr.markdown("<b style='font-size:0.8em;'>3. PLANO</b>", unsafe_allow_html=True)
            if btn.button("Reiniciar", key="res_pla"): reset_section(['ang'])
            st.selectbox("Regime Tectônico", ["Normal", "Transcorrente", "Reverso"], index=0, key='regime_sel', label_visibility="collapsed")
            dual_input("Ang/S1 (°)", 0, 90, 'ang')
            st.markdown("<div style='margin-bottom: 5px;'></div>", unsafe_allow_html=True) 
            if st.button("Limpar Trajetória", use_container_width=True): 
                st.session_state.path_x, st.session_state.path_y = [], []
