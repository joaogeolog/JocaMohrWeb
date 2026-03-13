import numpy as np

def calcular_envoltoria(ts, pc, c, phi):
    """Gera a envoltória do limite de tração ao colapso com fechamento virtual no zero."""
    phi_rad = np.radians(phi)
    xt_coll = pc * 0.6 
    
    # Criamos o range de Sn garantindo que comece em -ts e termine em pc
    sn_range = np.linspace(-ts, pc, 1200) 
    sn_final, tn_final = [], []
    
    for sn in sn_range:
        if sn < 0:
            # Tração
            tn = c * np.sqrt(max(0, 1 - (sn / -ts)))
        elif sn <= xt_coll:
            # Mohr-Coulomb linear
            tn = c + sn * np.tan(phi_rad)
        else:
            # Colapso (Elipsoide)
            a = pc - xt_coll
            b = c + xt_coll * np.tan(phi_rad)
            val = 1 - ((sn - xt_coll)**2 / a**2)
            tn = b * np.sqrt(max(0, val))
        
        # Aplicamos o seu truque: se for quase zero, mantemos em 0.001
        # Isso garante que o ponto exista no gráfico mas não pinte o eixo
        tn_display = max(tn, 0.001)
        
        sn_final.append(sn)
        tn_final.append(tn_display)
    
    return np.array(sn_final), np.array(tn_final), xt_coll

def calcular_ponto_com_trava(s1_eff, s3_eff, ang, x_env, y_env, last_ponto):
    """Calcula a posição e trava na borda usando a nova lógica de limites."""
    sn_target = (s1_eff + s3_eff)/2 + (s1_eff - s3_eff)/2 * np.cos(np.radians(2 * ang))
    tn_target = abs((s1_eff - s3_eff)/2 * np.sin(np.radians(2 * ang)))
    
    # Verificação de limites horizontais
    if sn_target < np.min(x_env) or sn_target > np.max(x_env):
        limite = 0.001
    else:
        limite = np.interp(sn_target, x_env, y_env)

    if tn_target <= limite:
        return sn_target, tn_target, False 
    
    sn_old = last_ponto.get('sn', sn_target)
    tn_old = last_ponto.get('tn', 0.001)
    t_min, t_max = 0.0, 1.0
    sn_res, tn_res = sn_old, tn_old
    
    for _ in range(15):
        t = (t_min + t_max) / 2
        sn_t = sn_old + t * (sn_target - sn_old)
        tn_t = tn_old + t * (tn_target - tn_old)
        
        lim_t = np.interp(sn_t, x_env, y_env, left=0.001, right=0.001)
        if tn_t > lim_t: t_max = t
        else: t_min = t; sn_res, tn_res = sn_t, tn_t
            
    return sn_res, tn_res, True

def obter_geometria_v18(centro, raio, x_env, y_env):
    """Gera a geometria do círculo respeitando o offset de 0.001."""
    ang = np.linspace(0, np.pi, 600)
    xc = centro + raio * np.cos(ang)
    yc = raio * np.sin(ang)
    
    res_env_circ = np.interp(xc, x_env, y_env, left=0.001, right=0.001)
    
    mask_fail = yc > res_env_circ + 0.01 # Pequena folga para estabilidade visual
    xc_stable = np.where(~mask_fail, xc, np.nan)
    yc_stable = np.where(~mask_fail, yc, np.nan)
    xc_fail = np.where(mask_fail, xc, np.nan)
    yc_fail = np.where(mask_fail, yc, np.nan)
    
    sn_fail_range = xc[mask_fail]
    if len(sn_fail_range) > 0:
        mask_env_high = (x_env >= np.min(sn_fail_range)) & (x_env <= np.max(sn_fail_range))
    else:
        mask_env_high = np.zeros_like(x_env, dtype=bool)
        
    return xc_stable, yc_stable, xc_fail, yc_fail, mask_env_high
