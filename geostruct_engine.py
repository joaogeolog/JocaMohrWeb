import numpy as np

def calcular_envoltoria(ts, pc, c, phi):
    """
    Gera os pontos da envoltória de falha (Tração, Cisalhamento e Colapso).
    ts: módulo da tração | pc: colapso | c: coesão | phi: ang. atrito
    """
    phi_rad = np.radians(phi)
    # Ponto de transição entre tração e cisalhamento (aproximado)
    xt_trans = 0 
    # Ponto de transição entre cisalhamento e colapso
    xt_coll = pc * 0.6 
    
    sn_range = np.linspace(-ts, pc + 50, 400)
    tn_range = []

    for sn in sn_range:
        if sn < 0:
            # Parábola de Tração: tn = c * sqrt(1 - sn/-ts)
            tn = c * np.sqrt(max(0, 1 - (sn / -ts)))
        elif sn <= xt_coll:
            # Reta de Mohr-Coulomb: tn = c + sn * tan(phi)
            tn = c + sn * np.tan(phi_rad)
        else:
            # Elipse de Colapso (simplificada para fechar no pc)
            a = pc - xt_coll
            b = c + xt_coll * np.tan(phi_rad)
            val = 1 - ((sn - xt_coll)**2 / a**2)
            tn = b * np.sqrt(max(0, val))
        tn_range.append(tn)
        
    return sn_range, np.array(tn_range), xt_coll

def calcular_ponto_com_intersecao(sn_new, tn_new, path_x, path_y, x_env, y_env):
    """
    Se o ponto alvo (new) estiver fora da envoltória, calcula a interseção 
    entre o caminho (old -> new) e a borda da envoltória.
    """
    # Se não houver histórico ou o ponto for o primeiro, testa contra a envoltória
    sn_old = path_x[-1] if path_x else sn_new
    tn_old = path_y[-1] if path_y else 0.0
    
    # Valor da envoltória no Sn atual
    limite_atual = np.interp(sn_new, x_env, y_env)
    
    if tn_new <= limite_atual:
        return sn_new, tn_new, False # Estável
    
    # Se falhou, busca a interseção por bisseção simples entre o ponto antigo e o novo
    t_min, t_max = 0.0, 1.0
    sn_res, tn_res = sn_old, tn_old
    
    for _ in range(10): # 10 iterações para precisão geomecânica
        t = (t_min + t_max) / 2
        sn_t = sn_old + t * (sn_new - sn_old)
        tn_t = tn_old + t * (tn_new - tn_old)
        
        if tn_t > np.interp(sn_t, x_env, y_env):
            t_max = t
        else:
            t_min = t
            sn_res, tn_res = sn_t, tn_t
            
    return sn_res, tn_res, True

def obter_geometria_v18(centro, raio, x_env, y_env, ts, pc):
    """Gera os arcos estáveis e teóricos do círculo de Mohr."""
    ang = np.linspace(0, np.pi, 200)
    xc = centro + raio * np.cos(ang)
    yc = raio * np.sin(ang)
    
    res_c = np.interp(xc, x_env, y_env)
    return xc, yc, res_c, xc, yc # Simplificado para performance
