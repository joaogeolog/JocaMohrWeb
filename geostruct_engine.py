import numpy as np

def calcular_envoltoria(ts, pc, c, phi):
    phi_rad = np.radians(phi)
    xt_coll = pc * 0.6 
    sn_range = np.linspace(-ts, pc + 50, 500)
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

def calcular_ponto_com_trava(s1_eff, s3_eff, ang, x_env, y_env, last_ponto):
    """Calcula a posição no círculo e aplica a interseção se houver falha."""
    # Ponto teórico no círculo
    sn_target = (s1_eff + s3_eff)/2 + (s1_eff - s3_eff)/2 * np.cos(np.radians(2 * ang))
    tn_target = abs((s1_eff - s3_eff)/2 * np.sin(np.radians(2 * ang)))
    
    sn_old = last_ponto.get('sn', sn_target)
    tn_old = last_ponto.get('tn', 0.0)
    
    limite = np.interp(sn_target, x_env, y_env)
    
    if tn_target <= limite:
        return sn_target, tn_target, False # Estável
    
    # Bisseção para achar a interseção com a borda
    t_min, t_max = 0.0, 1.0
    sn_res, tn_res = sn_old, tn_old
    for _ in range(15):
        t = (t_min + t_max) / 2
        sn_t = sn_old + t * (sn_target - sn_old)
        tn_t = tn_old + t * (tn_target - tn_old)
        if tn_t > np.interp(sn_t, x_env, y_env):
            t_max = t
        else:
            t_min = t
            sn_res, tn_res = sn_t, tn_t
    return sn_res, tn_res, True

def obter_geometria_v18(centro, raio, x_env, y_env):
    """Separa o círculo em parte estável e parte em falha (tracejada)."""
    ang = np.linspace(0, np.pi, 300)
    xc = centro + raio * np.cos(ang)
    yc = raio * np.sin(ang)
    res_env = np.interp(xc, x_env, y_env)
    
    # Máscara para pontos estáveis
    mask_stable = yc <= res_env + 0.1
    xc_stable = np.where(mask_stable, xc, np.nan)
    yc_stable = np.where(mask_stable, yc, np.nan)
    
    # Máscara para pontos em falha
    xc_fail = np.where(~mask_stable, xc, np.nan)
    yc_fail = np.where(~mask_stable, yc, np.nan)
    
    return xc_stable, yc_stable, res_env, xc_fail, yc_fail
