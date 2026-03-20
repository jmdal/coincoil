import math
from math import sqrt, log10



max_mgt = 240 # celsius
awg15 = 3257 # sqmils

awg = {
    "4/0":11.68, 
    10:2.59, 
    12:2.06,
    14:1.57,
    15:1.45,
    20:0.81,
    24:0.511,
    30:0.254
    }

def onderdonk_i(a, tm, ta, t):
    return a*sqrt(log10((tm-ta)/(234+ta)+1)/(33*t))

def coilturnlayered(wrd, cld, trn, len, generate): # wire dia, coil dia, turns, coil length, whether to generate LTSpice parameters ; all units in mm
    copperres = 1.71*10**-8
    tpl = len // wrd # turns per layer
    ttl = 0 # total wire length
    for cur in range(0,trn): # cur - current turn
        ttl += math.pi*(cld+(wrd * (cur // tpl + 1)))
    print(f"""Total wire length {ttl:.4f}mm over {math.ceil(trn/tpl):.0f} layers, {tpl:.0f} turns per layer, {math.pi*(cld+(wrd * (cur // tpl + 1))):.2f}mm length per turn (final layer); 
final coil width {math.ceil(trn/tpl)*wrd+cld:.2f}mm; total resistance {(ttl*copperres)/((wrd/1000)**2*math.pi):.4f}mΩ""")
    if generate:
        print(f".param slen={len/1000:.2f}\n.param turns={trn}\n.param cdia={math.ceil(trn/tpl)*wrd+cld:.2f}m\n.param cres={(ttl*copperres)/((wrd/2000)**2*math.pi):.4f}m")
    return ttl

def tableout(lst, sfx=""):
    st = ""
    for s in range(len(lst)):
        st += f"{s+1}, {lst[s]:.4f}{sfx}{"," if s < len(lst)-1 else ""} "
    return st


def coilturnlayeredtable(params): # arrays with 4 params; wire dia, coil/barrel dia, turns, coil length; all units in mm
    copperres = 1.71*10**-8
    lens = []
    trns = []
    dias = []
    ress = []
    inds = []
    for pm in params:
        tpl = pm[3] // pm[0] # turns per layer
        ttl = 0 # total wire length
        lay = math.ceil(pm[2]/tpl) # layers
        
        for cur in range(0,pm[2]): # cur - current turn
            ttl += math.pi*(pm[1]+(pm[0] * (cur // tpl + 1)))
        ptn = math.pi*(pm[1]+(pm[0] * (cur // tpl + 1))) # final layer turn length
        dia = math.ceil(pm[2]/tpl)*pm[0]+pm[1]
        res = (ttl*copperres)/((pm[0]/2000)**2*math.pi)
        ind = ((4*math.pi * 10**-7)*(pm[2]**2)*(math.pi*((dia/2000)**2))/(pm[3]/1000)) * 1000000
        print(f"""Total wire length {ttl:.4f}mm over {lay:.0f} layers, {tpl:.0f} turns per layer, {ptn:.2f}mm length per turn (final layer); final coil width {dia:.2f}mm; total resistance {res:.4f}mΩ, total inductance {ind:.4f}µH""")
        lens.append(pm[3])
        trns.append(pm[2])
        dias.append(dia)
        ress.append(res)
        inds.append(ind)
    print("TNum (xx)\tWDia (mm)\tBdia (mm)\tTurn (xx)\tClen (mm)\tCdia (mm)\tCrad (mm)\tCres (mΩ)\tCind (µH)")
    for i in range(len(params)):
        print(f"{i+1}\t\t{params[i][0]:.2f}\t\t{params[i][1]:.2f}\t\t{params[i][2]:.0f}\t\t{params[i][3]:.2f}\t\t{dias[i]:.2f}\t\t{dias[i]/2:.2f}\t\t{ress[i]:.5f}\t{inds[i]}")
    print(f".step param n 1 {len(params)} 1")
    print(f".param slen=table( n, {tableout(lens,"m")})")
    print(f".param turns=table( n, {tableout(trns)})")
    print(f".param cdia=table( n, {tableout(dias,"m")})")
    print(f".param cres=table( n, {tableout(ress,"m")})")
    
    return ttl


def stageaccel(acc, len, stg): # coilgun stage accel; acceleration, stage length, stage count
    pt = 0
    for s in range(1,stg+1):
        t = sqrt(2*(s*len)/acc)
        print(f"Stage {s} ({s*len:.3f}m)\t -- {0.0+t:.6f}s Total\t <- {t-pt:.6f}s Stage Contact")
        #print(f"Stage {s} ({s*len:.3f}m)\t -- {0.0+t:.6f}s Total\t <- {t-pt:.6f}s Stage Contact\t <- LTSpice Timing Pair {pt*10**6 - 0:.0f}u, {((t-pt)*10**6):.0f}u\t[S{s}]")
        #print(f"Stage [S{s}]\tPULSE(0 3.3 {pt*10**6 - 10000:.0f}u 1n 1n {((t-pt)*10**6) + 10000:.0f}u 10)")
        pt = t
    print(f"Final exit velocity: {pt*acc:.3f} m/s")

#stageaccel(345,0.08,20)

def stageaccel2(acc, len, stg): # acce, stage len, stage con
    pt = 0
    for s in range(1, stg+1):
        t = sqrt(2*(s*len)/acc)
        print(f"{t*10**6:.0f}")
        pt = t
#coilturnlayered(2.06, 33.4, 50, 30, "mm")



def ltscoilparams(n): # delay in microseconds
    for i in range(0,n+1):
        print(f".param t{i}=sqrt(2*({i}*slen)/acc)+{{delay}}")

def ltscoilpulse(n):
    for i in range(1,n+1):
        #print(f"[{i}]\t PULSE(0 20 {{-overlap+t{i-1}}} 1n 1n {{+overlap+t{i}-t{i-1}}} 3600)")
        print(f"[{i}]\t PULSE(0 20 {{-overlap+t{i-1}}} 1n 1n 1m 3600)")

# 0 3.3 prev_time-overlap 1n 1n time_elapsed+overlap 3600
"""



#coilturnlayered(awg[15], 33.40, 100, 40, True)

coilturnlayeredtable(
    [[awg[12], 33.40, x, 40] for x in range(100,200+1,10)]
)
#stageaccel(345,0.04,20)

"""
coilturnlayered(awg[15], 33.40, 100, 40, False)
#stageaccel2(600, 0.04, 20) # safe assumption -- 600 m/s
#stageaccel(600, 0.04, 20) # safe assumption -- 600 m/s

#ltscoilparams(20)
#ltscoilpulse(20)
