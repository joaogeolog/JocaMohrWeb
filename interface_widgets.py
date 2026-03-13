import streamlit as st

DEFAULTS = {'s1': 120.0, 's3': 40.0, 'pp': 20.0, 'alpha': 1.0, 'c': 15.0, 'phi': 30.0, 'ts': 10.0, 'pc': 180.0, 'ang': 30.0, 'mergulho': 60.0, 'regime': 'Normal'}

def sync_angles(source_key):
    """Sincronia: Mergulho = 90 - Ang S1."""
    if source_key == 'val_ang':
        new_val = 90.0 - st.session_state['val_ang']
        st.session_state['val_mergulho'] = new_val
    else:
        new_val = 90.0 - st.session_state['val_mergulho']
        st.session_state['val_ang'] = new_val
    
    # Atualiza widgets visuais
    st.session_state['slide_ang'] = st.session_state['num_ang'] = st.session_state['val_ang']
    st.session_state['slide_mergulho'] = st.session_state['num_mergulho'] = st.session_state['val_mergulho']

def sync_widgets(s, t, c):
    val = st.session_state[s]
    if c == 'val_s1':
        s3_at = st.session_state.get('val_s3', DEFAULTS['s3'])
        if val < s3_at: val = s3_at
    elif c == 'val_s3':
        s1_at = st.session_state.get('val_s1', DEFAULTS['s1'])
        if val > s1_at: val = s1_at
    
    st.session_state[c] = st.session_state[t] = st.session_state[s] = val
    if c in ['val_ang', 'val_mergulho']:
        sync_angles(c)

def dual_input(label, min_v, max_v, key_p, step=1.0):
    s_key, n_key, base_key = f"slide_{key_p}", f"num_{key_p}", f"val_{key_p}"
    if base_key not in st.session_state:
        st.session_state[base_key] = float(DEFAULTS.get(key_p, 30.0))
    
    c_l, c_s, c_n = st.columns([1, 2, 1])
    c_l.markdown(f"<p style='font-size:0.8em; margin-bottom: -15px;'>{label}</p>", unsafe_allow_html=True)
    c_s.slider(label, float(min_v), float(max_v), value=st.session_state[base_key], step=float(step), key=s_key, on_change=sync_widgets, args=(s_key, n_key, base_key), label_visibility="collapsed")
    c_n.number_input(label, float(min_v), float(max_v), value=st.session_state[base_key], step=float(step), key=n_key, on_change=sync_widgets, args=(n_key, s_key, base_key), label_visibility="collapsed")
    return st.session_state[base_key]

def render_bottom_interface():
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("<b>1. TENSÕES (MPa)</b>", unsafe_allow_html=True)
            dual_input("S1 (MPa)", 0, 250, 's1')
            dual_input("S3 (MPa)", 0, 250, 's3')
            dual_input("P. Poros (MPa)", 0, 100, 'pp')
        with c2:
            st.markdown("<b>2. ROCHA</b>", unsafe_allow_html=True)
            dual_input("Coesão (MPa)", 0, 100, 'c')
            dual_input("Atrito (°)", 0, 90, 'phi')
            dual_input("Colapso (MPa)", 0, 500, 'pc')
        with c3:
            st.markdown("<b>3. PLANO</b>", unsafe_allow_html=True)
            st.selectbox("Regime Tectônico", ["Normal", "Transcorrente", "Reverso"], key='regime_sel')
            dual_input("Ângulo com S1 (°)", 0, 90, 'ang')
            dual_input("Mergulho (°)", 0, 90, 'mergulho')
            if st.button("Limpar Trajetória", use_container_width=True): 
                st.session_state.path_x, st.session_state.path_y = [], []
