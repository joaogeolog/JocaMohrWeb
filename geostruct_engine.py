import numpy as np

def obter_geometria_v18(centro, raio, x_env, y_env):
    """Separa o círculo em estável/falha e identifica o realce na envoltória."""
    ang = np.linspace(0, np.pi, 300)
    xc = centro + raio * np.cos(ang)
    yc = raio * np.sin(ang)
    res_env_no_circulo = np.interp(xc, x_env, y_env)
    
    # Segmentação do Círculo
    mask_fail = yc > res_env_no_circulo + 0.05
    xc_stable = np.where(~mask_fail, xc, np.nan)
    yc_stable = np.where(~mask_fail, yc, np.nan)
    xc_fail = np.where(mask_fail, xc, np.nan)
    yc_fail = np.where(mask_fail, yc, np.nan)
    
    # Identificação do Realce na Envoltória (Onde Sn do círculo intercepta Sn da envoltória)
    # Procuramos o range de Sn onde o círculo está em falha
    sn_fail_range = xc[mask_fail]
    if len(sn_fail_range) > 0:
        sn_min, sn_max = np.min(sn_fail_range), np.max(sn_fail_range)
        mask_env_highlight = (x_env >= sn_min) & (x_env <= sn_max)
    else:
        mask_env_highlight = np.zeros_like(x_env, dtype=bool)
        
    return xc_stable, yc_stable, xc_fail, yc_fail, mask_env_highlight
