import streamlit as st

DEFAULTS = {
    's1': 120.0, 's3': 40.0, 'pp': 20.0, 'alpha': 1.0, 
    'c': 15.0, 'phi': 30.0, 'ts': -10.0, 'pc': 180.0, 
    'ang': 30.0, 'regime': 'Normal'
}

def sync_widgets(s, t, c):
    val = st.session_state[s]
    if c == 'val_s1':
        s3_atual = st.session_state.get('val_s3', DEFAULTS['s3'])
        if val < s3_atual: val = s3_atual
    elif c == 'val_s3':
        s1_atual = st.session_state.get('val_s1', DEFAULTS['s1'])
        if val > s1_atual: val = s1_atual
    st.session_state[c] = st.session_state[t] = st.session_state[s] = val

def update_from_ang():
    st.session_state['val_ang'] = st.session_state['slide_ang']
    st.session_state['num_ang'] = st.session_state['slide_ang']
    if st.session_state.regime_sel != "Transcorrente":
        m_val = 90.0 - st.session_state['val_ang']
        st.session_state['val_mergulho'] = st.session_state['slide_mergulho'] = st.session_state['num_mergulho'] = m_val

def update_from_mergulho():
    st.session_state['val_mergulho'] = st.session_state['slide_mergulho']
    st.session_state['num_mergulho'] = st.session_state['slide_mergulho']
    a_val = 90.0 - st.session_state['val_mergulho']
    st.session_state['val_ang'] = st.session_state['slide_ang'] = st.session_state['num_ang'] = a_val

def reset_section(keys, clear_viz=False):
    for k in keys:
        for pfx in ['val_', 'slide_', 'num_']:
            st.session_state[pfx + k] = float(DEFAULTS[k])
    if clear_viz:
        st.session_state.path_x, st.session_state.path_y = [], []
        st.session_state.ponto_fisico = {'sn': 0.0, 'tn': 0.0}

def dual_input(label, min_v, max_v, key_p, step=1.0):
    s_key, n_key, base_key = f"slide_{key_p}", f"num_{key_p}", f"val_{key_p}"
    if base_key not in st.session_state:
        st.session_state[base_key] = st.session_state[s_key] = st.session_state[n_key] = float(DEFAULTS[key_p])
    
    # Reduzi o espaçamento lateral e vertical aqui
    c_l, c_s, c_n = st.columns([0.9, 2.2, 0.9])
    c_l.markdown(f"<p style='font-size:0.8em; margin-bottom: -10px;'>{label}</p>", unsafe_allow_html=True)
    c_s.slider(label, float(min_v), float(max_v), step=float(step), key=s_key, on_change=sync_widgets, args=(s_key, n_key, base_key), label_visibility="collapsed")
    c_n.number_input(label, float(min_v), float(max_v), step=float(step), key=n_key, on_change=sync_widgets, args=(n_key, s_key, base_key), label_visibility="collapsed")
    return st.session_state[base_key]

def dual_input_custom(label, min_v, max_v, key_p, on_change_callback, disabled=False):
    s_key, n_key = f"slide_{key_p}", f"num_{key_p}"
    c_l, c_s, c_n = st.columns([0.9, 2.2, 0.9])
    c_l.markdown(f"<p style='font-size:0.8em; margin-bottom: -10px;'>{label}</p>", unsafe_allow_html=True)
    c_s.slider(label, float(min_v), float(max_v), key=s_key, on_change=on_change_callback, label_visibility="collapsed", disabled=disabled)
    c_n.number_input(label, float(min_v), float(max_v), key=n_key, on_change=on_change_callback, label_visibility="collapsed", disabled=disabled)

def render_bottom_interface():
    # CSS injetado localmente para forçar a subida das barras
    st.markdown("""
        <style>
            .stSlider { margin-bottom: -15px; }
            .stNumberInput { margin-bottom: -15px; }
            [data-testid="stVerticalBlock"] > div { padding-top: 0rem; padding-bottom: 0rem; }
        </style>
    """, unsafe_allow_html=True)

    with st.container(border=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            hdr, btn = st.columns([2.5, 1])
            hdr.markdown("<b style='font-size:0.8em;'>1. TENSÕES (MPa)</b>", unsafe_allow_html=True)
            if btn.button("Reiniciar", key="res_t"): reset_section(['s1', 's3', 'pp'])
            dual_input("S1", 0, 250, 's1')
            dual_input("S3", 0, 250, 's3')
            dual_input("P. Poros", 0, 100, 'pp')

        with col2:
            hdr, btn = st.columns([2.5, 1])
            hdr.markdown("<b style='font-size:0.8em;'>2. ROCHA</b>", unsafe_allow_html=True)
            if btn.button("Reiniciar", key="res_r"): reset_section(['c', 'phi', 'ts', 'pc', 'alpha'])
            dual_input("Coesão", 0, 50, 'c')
            dual_input("Atrito", 0, 50, 'phi')
            dual_input("Tração", -50, 0, 'ts')
            dual_input("Colapso", 0, 250, 'pc')
            dual_input("Biot", 0.0, 1.0, 'alpha', step=0.01)

        with col3:
            hdr, btn = st.columns([2.5, 1])
            hdr.markdown("<b style='font-size:0.8em;'>3. PLANO</b>", unsafe_allow_html=True)
            if btn.button("Reiniciar", key="res_p"): reset_section(['ang'], clear_viz=True)
            st.selectbox("Regime", ["Normal", "Transcorrente", "Reverso"], key='regime_sel', label_visibility="collapsed")
            is_trans = (st.session_state.regime_sel == "Transcorrente")
            dual_input_custom("Ângulo S1", 0, 90, 'ang', update_from_ang)
            dual_input_custom("Mergulho", 0, 90, 'mergulho', update_from_mergulho, disabled=is_trans)
            st.button("Limpar Trajetória", on_click=lambda: reset_section(['ang'], clear_viz=True), use_container_width=True)
