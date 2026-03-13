import numpy as np

def calcular_envoltoria(ts, pc, c, phi):
    """Gera os pontos da envoltória: Tração, Cisalhamento e Colapso."""
    phi_rad = np.radians(phi)
    xt_coll = pc * 0.6 
    
    sn_range = np.linspace(-ts, pc + 50, 400)
    tn_range = []

    for sn in sn_range:
        if sn < 0:
            tn = c * np.sqrt(max(0, 1 - (sn / -ts)))
        elif sn <= xt_coll:
            tn = c + sn * np.tan(phi_rad)
        else:
            a = pc - xt_coll
            b = c + xt_coll * np.tan(phi_rad)
            val = 1 - ((sn - xt_coll)**2 / a**2)
            tn = b * np.sqrt(max(0, val))
        tn_range.append(tn)
        
    return sn_range, np.array(tn_range), xt_coll

def calcular_ponto_com_trava(sn_new, tn_new, ang, x_env, y_env, ts, pc, last_ponto):
    """
    Calcula a interseção real entre o caminho e a envoltória.
    Substitui a lógica de 'congelar' o ponto.
    """
    sn_old = last_ponto.get('sn', sn_new)
    tn_old = last_ponto.get('tn', 0.0)
    
    limite_target = np.interp(sn_new, x_env, y_env)
    
    if tn_new <= limite_target:
        return sn_new, tn_new, False # Estável
    
    # Busca por bisseção o ponto exato na borda
    t_min, t_max = 0.0, 1.0
    sn_res, tn_res = sn_old, tn_old
    
    for _ in range(15):
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
    """Restaura a visualização detalhada dos arcos do círculo de Mohr."""
    ang = np.linspace(0, np.pi, 200)
    xc = centro + raio * np.cos(ang)
    yc = raio * np.sin(ang)
    
    res_c = np.interp(xc, x_env, y_env)
    
    # xc_f/yc_f são os pontos que falharam (estão acima da envoltória)
    # xc_o/yc_o são os pontos estáveis
    return xc, yc, res_c, xc, yc
