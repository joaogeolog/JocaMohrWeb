import numpy as np

def calcular_envoltoria(ts, pc, c, phi):
    """Gera a geometria da envoltória limitada ao semiplano superior positivo."""
    phi_rad = np.radians(phi)
    xt_coll = pc * 0.6 
    # Aumentamos a densidade de pontos para garantir fechamento suave
    sn_range = np.linspace(-ts, pc, 1000) 
    sn_final, tn_final = [], []
    
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
        
        # SÓ ADICIONA SE TN FOR MAIOR QUE ZERO
        if tn > 0.01: 
            sn_final.append(sn)
            tn_final.append(tn)
    
    return np.array(sn_final), np.array(tn_final), xt_coll

def calcular_ponto_com_trava(s1_eff, s3_eff, ang, x_env, y_env, last_ponto):
    """Calcula a posição no círculo e trava na interseção se houver falha."""
    sn_target = (s1_eff + s3_eff)/2 + (s1_eff - s3_eff)/2 * np.cos(np.radians(2 * ang))
    tn_target = abs((s1_eff - s3_eff)/2 * np.sin(np.radians(2 * ang)))
    
    # Interpolação segura: se sn_target estiver fora do range da env, usamos o último tn da env
    if sn_target < np.min(x_env):
        limite = y_env[0]
    elif sn_target > np.max(x_env):
        limite = 0
    else:
        limite = np.interp(sn_target, x_env, y_env)

    if tn_target <= limite:
        return sn_target, tn_target, False 
    
    sn_old = last_ponto.get('sn', sn_target)
    tn_old = last_ponto.get('tn', 0.0)
    t_min, t_max = 0.0, 1.0
    sn_res, tn_res = sn_old, tn_old
    for _ in range(15):
        t = (t_min + t_max) / 2
        sn_t = sn_old + t * (sn_target - sn_old)
        tn_t = tn_old + t * (tn_target - tn_old)
        
        lim_t = np.interp(sn_t, x_env, y_env, left=y_env[0], right=0)
        if tn_t > lim_t:
            t_max = t
        else:
            t_min = t
            sn_res, tn_res = sn_t, tn_t
    return sn_res, tn_res, True

def obter_geometria_v18(centro, raio, x_env, y_env):
    """Separa o círculo em sólido/tracejado e define o realce da envoltória."""
    ang = np.linspace(0, np.pi, 500)
    xc = centro + raio * np.cos(ang)
    yc = raio * np.sin(ang)
    
    # Interpolação do limite da envoltória para cada sn do círculo
    res_env_circ = np.interp(xc, x_env, y_env, left=0, right=0)
    
    mask_fail = yc > res_env_circ + 0.05
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
