import streamlit as st

DEFAULTS = {'s1': 120.0, 's3': 40.0, 'pp': 20.0, 'alpha': 1.0, 'c': 15.0, 'phi': 30.0, 'ts': 10.0, 'pc': 180.0, 'ang': 30.0, 'mergulho': 60.0}

def sync_angles(source_key):
    # Se for Transcorrente, o mergulho não segue a conta 90-ang, ele é fixo em 90.
    if st.session_state.get('regime_sel') == 'Transcorrente':
        st.session_state['val_mergulho'] = 90.0
    else:
        if source_key == 'val_ang':
            st.session_state['val_mergulho'] = 90.0 - st.session_state['val_ang']
        else:
            st.session_state['val_ang'] = 90.0 - st.session_state['val_mergulho']
    
    st.session_state['slide_ang'] = st.session_state['num_ang'] = st.session_state['val_ang']
    st.session_state['slide_mergulho'] = st.session_state['num_mergulho'] = st.session_state['val_mergulho']

def sync_widgets(s, t, c):
    val = st.session_state[s]
    if c == 'val_s1' and val < st.session_state.get('val_s3', 0): val = st.session_state['val_s3']
    if c == 'val_s3' and val > st.session_state.get('val_s1', 250): val = st.session_state['val_s1']
    st.session_state[c] = st.session_state[t] = st.session_state[s] = val
    if c in ['val_ang', 'val_mergulho'] or s == 'regime_sel':
        sync_angles(c)

def reset_section(keys):
    for k in keys:
        v = float(DEFAULTS[k])
        st.session_state[f'val_{k}'] = st.session_state[f'slide_{k}'] = st.session_state[f'num_{k}'] = v
    if 'ang' in keys:
        sync_angles('val_ang')
        st.session_state.path_x, st.session_state.path_y = [], []

def dual_input(label, min_v, max_v, key_p, step=1.0, disabled=False):
    s_key, n_key, base_key = f"slide_{key_p}", f"num_{key_p}", f"val_{key_p}"
    if base_key not in st.session_state:
        v = float(DEFAULTS.get(key_p, 30.0))
        st.session_state[base_key] = st.session_state[s_key] = st.session_state[n_key] = v
    
    c_l, c_s, c_n = st.columns([1, 2, 1])
    c_l.markdown(f"<p style='font-size:0.8em; margin-bottom: -15px;'>{label}</p>", unsafe_allow_html=True)
    c_s.slider(label, float(min_v), float(max_v), step=float(step), key=s_key, on_change=sync_widgets, args=(s_key, n_key, base_key), label_visibility="collapsed", disabled=disabled)
    c_n.number_input(label, float(min_v), float(max_v), step=float(step), key=n_key, on_change=sync_widgets, args=(n_key, s_key, base_key), label_visibility="collapsed", disabled=disabled)
    return st.session_state[base_key]

def render_ui():
    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        with c1:
            h, b = st.columns([3, 1]); h.markdown("<b>1. TENSÕES (MPa)</b>", unsafe_allow_html=True)
            if b.button("Reiniciar", key="r1"): reset_section(['s1', 's3', 'pp'])
            dual_input("S1 (MPa)", 0, 250, 's1'); dual_input("S3 (MPa)", 0, 250, 's3'); dual_input("P. Poros (MPa)", 0, 100, 'pp')
        with c2:
            h, b = st.columns([3, 1]); h.markdown("<b>2. ROCHA</b>", unsafe_allow_html=True)
            if b.button("Reiniciar", key="r2"): reset_section(['c', 'phi', 'ts', 'pc', 'alpha'])
            dual_input("Coesão", 0, 100, 'c'); dual_input("Atrito", 0, 90, 'phi'); dual_input("Tração", 0, 50, 'ts'); dual_input("Colapso", 0, 500, 'pc'); dual_input("Biot", 0.0, 1.0, 'alpha', 0.01)
        with c3:
            h, b = st.columns([3, 1]); h.markdown("<b>3. PLANO</b>", unsafe_allow_html=True)
            if b.button("Reiniciar", key="r3"): reset_section(['ang', 'mergulho'])
            
            # Regime Tectônico dispara a sincronia ao mudar
            st.selectbox("Regime Tectônico", ["Normal", "Transcorrente", "Reverso"], key='regime_sel', on_change=sync_angles, args=('val_mergulho',))
            
            is_trans = st.session_state.get('regime_sel') == 'Transcorrente'
            dual_input("Ângulo com S1", 0, 90, 'ang')
            dual_input("Mergulho (°)", 0, 90, 'mergulho', disabled=is_trans)
            
            if st.button("Limpar Trajetória", use_container_width=True): st.session_state.path_x, st.session_state.path_y = [], []
