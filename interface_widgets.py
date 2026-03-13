import streamlit as st

DEFAULTS = {'s1': 120.0, 's3': 40.0, 'pp': 20.0, 'alpha': 1.0, 'c': 15.0, 'phi': 30.0, 'ts': 10.0, 'pc': 180.0, 'ang': 30.0, 'regime': 'Normal'}

def sync_widgets(s, t, c):
    st.session_state[c] = st.session_state[t] = st.session_state[s]

def sync_angles(source_key):
    """Sincroniza Ângulo com S1 e Mergulho (90 - ang). Trava se for Transcorrente."""
    if st.session_state.regime_sel == "Transcorrente":
        # No transcorrente, o mergulho é sempre 90 (vertical), não altera o ang_s1
        st.session_state.val_mergulho = 90.0
        return

    if source_key == "ang":
        st.session_state.val_mergulho = 90.0 - st.session_state.val_ang
    else:
        st.session_state.val_ang = 90.0 - st.session_state.val_mergulho

def reset_section(keys):
    for k in keys:
        for pfx in ['val_', 'slide_', 'num_']:
            st.session_state[pfx + k] = float(DEFAULTS[k])
    if 'ang' in keys:
        st.session_state.path_x, st.session_state.path_y, st.session_state.ponto_fisico = [], [], {'sn': 0.0, 'tn': 0.0}
        st.session_state.val_mergulho = 90.0 - DEFAULTS['ang']

def dual_input(label, min_v, max_v, key_p, step=1.0, on_change_func=None):
    s_key, n_key, base_key = f"slide_{key_p}", f"num_{key_p}", f"val_{key_p}"
    
    if base_key not in st.session_state:
        st.session_state[base_key] = st.session_state[s_key] = st.session_state[n_key] = float(DEFAULTS.get(key_p, min_v))
    
    def internal_on_change():
        sync_widgets(s_key, n_key, base_key)
        if on_change_func:
            on_change_func(key_p)

    c_l, c_s, c_n = st.columns([1, 2, 1])
    c_l.markdown(f"<p style='font-size:0.85em; margin-top:5px;'>{label}</p>", unsafe_allow_html=True)
    c_s.slider(label, float(min_v), float(max_v), step=float(step), key=s_key, on_change=internal_on_change, label_visibility="collapsed")
    c_n.number_input(label, float(min_v), float(max_v), step=float(step), key=n_key, on_change=internal_on_change, label_visibility="collapsed")
    return st.session_state[base_key]

def render_bottom_interface():
    """Renderiza a interface com as novas nomenclaturas e vínculo de ângulos."""
    if 'val_mergulho' not in st.session_state:
        st.session_state.val_mergulho = 90.0 - float(DEFAULTS['ang'])

    with st.container(border=True):
        c1, c2, c3 = st.columns(3)
        
        with c1:
            hdr_col1, btn_col1 = st.columns([2, 1])
            hdr_col1.markdown("<b style='font-size:0.8em;'>1. TENSÕES (MPa)</b>", unsafe_allow_html=True)
            if btn_col1.button("Reiniciar", key="res_tens"): reset_section(['s1', 's3', 'pp'])
            
            dual_input("S1 (MPa)", 0, 250, 's1')
            dual_input("S3 (MPa)", 0, 250, 's3')
            dual_input("P. Poros (MPa)", 0, 100, 'pp')
            
        with c2:
            hdr_col2, btn_col2 = st.columns([2, 1])
            hdr_col2.markdown("<b style='font-size:0.8em;'>2. ROCHA</b>", unsafe_allow_html=True)
            if btn_col2.button("Reiniciar", key="res_roc"): reset_section(['c', 'phi', 'ts', 'pc', 'alpha'])
            
            dual_input("Coesão (MPa)", 0, 100, 'c')
            dual_input("Ângulo Atrito (°)", 0, 90, 'phi') # Nome atualizado
            dual_input("Tração (MPa)", 0, 50, 'ts')
            dual_input("Colapso (MPa)", 0, 500, 'pc')
            dual_input("Biot (adim.)", 0.0, 1.0, 'alpha', step=0.01)
            
        with c3:
            hdr_col3, btn_col3 = st.columns([2, 1])
            hdr_col3.markdown("<b style='font-size:0.8em;'>3. PLANO</b>", unsafe_allow_html=True)
            if btn_col3.button("Reiniciar", key="res_pla"): reset_section(['ang'])
            
            regime = st.selectbox("Regime Tectônico", ["Normal", "Transcorrente", "Reverso"], index=0, key='regime_sel')
            
            # Ângulo com S1
            dual_input("Ângulo com S1 (°)", 0, 90, 'ang', on_change_func=sync_angles)
            
            # Mergulho vinculado
            is_transcorrente = (regime == "Transcorrente")
            if is_transcorrente:
                st.session_state.val_mergulho = 90.0
                
            dual_input("Mergulho (°)", 0, 90, 'mergulho', on_change_func=sync_angles)
            
            st.write("") 
            if st.button("Limpar Trajetória", use_container_width=True): 
                st.session_state.path_x, st.session_state.path_y = [], []
