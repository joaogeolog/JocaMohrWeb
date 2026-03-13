import streamlit as st

DEFAULTS = {'s1': 120.0, 's3': 40.0, 'pp': 20.0, 'alpha': 1.0, 'c': 15.0, 'phi': 30.0, 'ts': 10.0, 'pc': 180.0, 'ang': 30.0, 'regime': 'Normal'}

def sync_widgets(s, t, c):
    st.session_state[c] = st.session_state[t] = st.session_state[s]

def update_from_ang():
    """Calcula Mergulho a partir do Ângulo com S1."""
    st.session_state['val_ang'] = st.session_state['slide_ang']
    st.session_state['num_ang'] = st.session_state['slide_ang']
    
    # No Transcorrente, o mergulho não muda (travado em 90)
    if st.session_state.regime_sel != "Transcorrente":
        novo_mergulho = 90.0 - st.session_state['val_ang']
        st.session_state['val_mergulho'] = novo_mergulho
        st.session_state['slide_mergulho'] = novo_mergulho
        st.session_state['num_mergulho'] = novo_mergulho

def update_from_mergulho():
    """Calcula Ângulo com S1 a partir do Mergulho."""
    st.session_state['val_mergulho'] = st.session_state['slide_mergulho']
    st.session_state['num_mergulho'] = st.session_state['slide_mergulho']
    
    novo_ang = 90.0 - st.session_state['val_mergulho']
    st.session_state['val_ang'] = novo_ang
    st.session_state['slide_ang'] = novo_ang
    st.session_state['num_ang'] = novo_ang

def reset_angles_on_regime():
    """Reinicia os ângulos para o padrão e aplica trava se necessário."""
    reset_section(['ang'])
    if st.session_state.regime_sel == "Transcorrente":
        st.session_state['val_mergulho'] = 90.0
        st.session_state['slide_mergulho'] = 90.0
        st.session_state['num_mergulho'] = 90.0

def reset_section(keys):
    for k in keys:
        for pfx in ['val_', 'slide_', 'num_']:
            st.session_state[pfx + k] = float(DEFAULTS[k])
    if 'ang' in keys:
        st.session_state.path_x, st.session_state.path_y, st.session_state.ponto_fisico = [], [], {'sn': 0.0, 'tn': 0.0}
        m_val = 90.0 - DEFAULTS['ang']
        st.session_state['val_mergulho'] = st.session_state['slide_mergulho'] = st.session_state['num_mergulho'] = m_val

def dual_input_custom(label, min_v, max_v, key_p, on_change_callback, disabled=False):
    """Versão customizada com suporte a desabilitação."""
    s_key, n_key = f"slide_{key_p}", f"num_{key_p}"
    
    c_l, c_s, c_n = st.columns([1, 2, 1])
    c_l.markdown(f"<p style='font-size:0.85em; margin-top:5px;'>{label}</p>", unsafe_allow_html=True)
    c_s.slider(label, float(min_v), float(max_v), key=s_key, on_change=on_change_callback, label_visibility="collapsed", disabled=disabled)
    c_n.number_input(label, float(min_v), float(max_v), key=n_key, on_change=on_change_callback, label_visibility="collapsed", disabled=disabled)

def dual_input(label, min_v, max_v, key_p, step=1.0):
    s_key, n_key, base_key = f"slide_{key_p}", f"num_{key_p}", f"val_{key_p}"
    if base_key not in st.session_state:
        st.session_state[base_key] = st.session_state[s_key] = st.session_state[n_key] = float(DEFAULTS[key_p])
    
    c_l, c_s, c_n = st.columns([1, 2, 1])
    c_l.markdown(f"<p style='font-size:0.85em; margin-top:5px;'>{label}</p>", unsafe_allow_html=True)
    c_s.slider(label, float(min_v), float(max_v), step=float(step), key=s_key, on_change=sync_widgets, args=(s_key, n_key, base_key), label_visibility="collapsed")
    c_n.number_input(label, float(min_v), float(max_v), step=float(step), key=n_key, on_change=sync_widgets, args=(n_key, s_key, base_key), label_visibility="collapsed")
    return st.session_state[base_key]

def render_bottom_interface():
    if 'val_ang' not in st.session_state:
        reset_section(['ang'])

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
            dual_input("Ângulo Atrito (°)", 0, 90, 'phi')
            dual_input("Tração (MPa)", 0, 50, 'ts')
            dual_input("Colapso (MPa)", 0, 500, 'pc')
            dual_input("Biot (adim.)", 0.0, 1.0, 'alpha', step=0.01)
            
        with c3:
            hdr_col3, btn_col3 = st.columns([2, 1])
            hdr_col3.markdown("<b style='font-size:0.8em;'>3. PLANO</b>", unsafe_allow_html=True)
            if btn_col3.button("Reiniciar", key="res_pla"): reset_section(['ang'])
            
            st.selectbox("Regime Tectônico", ["Normal", "Transcorrente", "Reverso"], 
                         index=0, key='regime_sel', on_change=reset_angles_on_regime)
            
            is_trans = (st.session_state.regime_sel == "Transcorrente")
            
            # Ângulo com S1: Sempre editável
            dual_input_custom("Ângulo com S1 (°)", 0, 90, 'ang', update_from_ang)
            
            # Mergulho: Travado em 90 se for Transcorrente
            if is_trans:
                st.session_state['slide_mergulho'] = 90.0
                st.session_state['num_mergulho'] = 90.0
                st.session_state['val_mergulho'] = 90.0
            
            dual_input_custom("Mergulho (°)", 0, 90, 'mergulho', update_from_mergulho, disabled=is_trans)
            
            if is_trans:
                st.caption("ℹ️ No regime Transcorrente, o mergulho é fixo em 90°.")

            st.write("") 
            if st.button("Limpar Trajetória", use_container_width=True): 
                st.session_state.path_x, st.session_state.path_y = [], []
