import PyLTSpice
import femm

import math
from math import sqrt, log10

import csv

CuRes = 1.71*10**-8 # Copper Resistivity
CuDense = 8960

class Coilsim:
    def __init__(self, wdia, bwid, bhei, lthi, turn, clen, capa, volt, scon):
        self.wdia = wdia # Wire Diameter
        self.bwid = bwid # Barrel Width
        self.bhei = bhei # Barrel Height
        self.lthi = lthi # Barrel Lining Thickness
        self.turn = turn # Turn Count
        self.clen = clen # Coil Length (Stage Length minus separators)
        self.capa = capa # Capacitance
        self.volt = volt # Voltage
        self.scon = scon # Stage Count

        self.tpll = clen//wdia # Turns Per Layer (theoretically possible levels list)
        self.ttll = wirelengthrect(wdia, bwid+2*lthi, bhei+2*lthi, turn, self.tpll) # Total Length
        self.flen = self.ttll/1000 # Total Length as meters

        self.lays = math.ceil(turn/self.tpll) # Layer Count
        self.fwid = self.bwid + 2*self.lthi + self.lays*(2*wdia) # Final Width
        self.fhei = self.bhei + 2*self.lthi + self.lays*(2*wdia) # Final Height


        self.fmas = self.ttll * ((wdia/2000)**2) * math.pi * CuDense# Total Mass (g)

        self.cres = (CuRes*self.ttll) / ((wdia/2000)**2 * math.pi) # Total Resistance (milli )

        # Final Inductance???

        # let's try to use this: https://www.allaboutcircuits.com/tools/rectangle-loop-inductance-calculator/
        self.cind = (turn**2) * (4 * 10**-7)*( -2*(self.fwid + self.fhei) + 2*math.sqrt(self.fwid**2 + self.fhei**2) - bhei*math.log((self.fhei + math.sqrt(self.fwid**2 + bhei**2))/self.fwid) - self.fwid*math.log((self.fwid + math.sqrt(self.fwid**2 + self.fhei**2))/self.fhei) + bhei*math.log(4*self.fhei/wdia) + self.fwid*math.log(4*self.fwid/wdia) ) * 1000 # x1000 correction factor

        # Total Inductance (micro-henry)

        self.curr = 0 # Current, to calculate later
        self.rise = 0 # Time to max current rise
        self.fall = 0 # Time to current final drop



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

def awg(n):
    return (0.005*(92**((36-n)/39)))*25.4

def tableout(lst, sfx=""):
    st = ""
    for s in range(len(lst)):
        st += f"{s+1}, {lst[s]:.4f}{sfx}{"," if s < len(lst)-1 else ""} "
    return st

def wirelength(wdia, bdia, turn, tpl):
    ttl = 0
    for cur in range(0,turn): # cur - current turn
        ttl += math.pi*(bdia+(wdia * (cur // tpl + 1)))
    return ttl

def wirelengthrect(wiredia, basewid, basehei, turns, turnperlayer):
    ttl = 0
    layer = 0
    #print(turnperlayer)
    for cur in range(0,turns): # cur - current turn
        ttl += (2*(basewid + (layer * 2*wiredia)) + 2*(basehei + (layer * 2*wiredia)))
        #print(f"{ttl:.5f}\t{2*(basewid + (layer * 2*wiredia)):.4f} \t {2*(basehei + (layer * 2*wiredia)):.4f} \t {layer:.0f}")
        if (cur + 1) % turnperlayer == 0:
            layer += 1
        #print(f"{ttl}\t{(2*(basewid + (layer * 2*wiredia)) + 2*(basehei + (layer * 2*wiredia)))}")
    return ttl

def get_current(raw_file, log_file):
    return PyLTSpice.LTSpiceLogReader(log_file)["current"][0]



def fullsim(parameters, spice_file=""):
    initialcount = len(parameters)

    # Parameter Information
    while True:
        prompt = input(f"About to run [{len(parameters)}] tests. \nV - View Tests // C - Cancel // S - Start\n> ")
        if prompt == "C":
            return 0
        elif prompt == "V":
            print("Test [xx]\tWdia [mm]\tBwid [mm]\tBhei [mm]\tLthi [mm]\tTurn [xx]\tTpll [xx]\tClen [mm]\tScon [xx]\tTlen [mm]\tCapa [µF]\tVolt [1V]\tFwid [mm]\tFhei [mm]\tFlen [1m]\tFmas [1g]\tCres [mΩ]\tCind [µH]")
            for i in range(len(parameters)):
                pm = parameters[i]
                print(f"{i+1:.0f}\t\t{pm.wdia:.2f}\t\t{pm.bwid:.2f}\t\t{pm.bhei:.2f}\t\t{pm.lthi:.2f}\t\t{pm.turn:.0f}\t\t{pm.tpll:.0f}\t\t{pm.clen:.2f}\t\t{pm.scon:.0f}\t\t{pm.clen*pm.scon:.2f}\t\t{pm.capa:.0f}\t\t{pm.volt:.2f}\t\t{pm.fwid:.2f}\t\t{pm.fhei:.2f}\t\t{pm.flen:.2f}\t\t{pm.fmas:.2f}\t\t{pm.cres:.2f}\t\t{pm.cind:.2f}")
        elif prompt == "S":
            break

    #wirelengthrect(awg(16), 26, 5, 200, 24)

    # Phase 1 // Coil Parameter Calculations [Change -- Rectangular Coils now] [Change 2 -- moved to inherent class calculations]
    # Lens -> Lengths "coillength"
    # Trns -> Turns "turncount"
    # Dias -> Final Diameter (final coil width/height based on layering)
    # Ress -> Final Resistance (based on used length)
    # Inds -> Final Inductance VERY HARD


    """
    for pm in parameters:
        tpl = pm["coillength"] // pm["wirediameter"]

        ttl = wirelengthrect(pm["wirediameter"], pm["barrelwidth"], pm["barrelheight"], pm["turncount"], tpl)

        lay = math.ceil(pm["turncount"]//tpl) # layers

        pm["finalwidth"] = pm["barrelwidth"] + (pm["wirediameter"])
        fhei = 0
    
        # TODO: port coil calculations with rectangular coils, stopped last night on final wid and hei
        # TODO: figure out rectangular coil inductance for use in LTSpice


    """


    print("Starting LTSpice...")

    sim = PyLTSpice.SimRunner(output_folder="pyscripts/output/ltspice",simulator="D:\\ProgramFiles\\LTspice\\LTspice.exe",parallel_sims=8,timeout=10.00)

    net = PyLTSpice.SpiceEditor(spice_file)

    #net.set_parameters(slen=tb_slen, turns=tb_trns, cdia=tb_cdia, cres=tb_cres, coil=tb_inds)
    #net.add_instructions(f".step PARAM n 1 {len(test_parameters)} 1")

    cnts = {} # currents
    prog = 0
    for i in parameters: # Run each simulation per generated parameter set
        prog += 1

        net.set_parameters(coil=i.cind*10**-6, cres=i.cres*10**-3, cap=i.capa*10**-6, involt=i.volt, testnum=prog-1)
        #net_name = f"coilgunauto_size{test_parameters[i][0]:.2f}_dia{test_parameters[i][1]:.2f}_turn{test_parameters[i][2]:.2f}_length{test_parameters[i][3]:.2f}.net"
        net_name = f"coilgunauto_{prog}.net"
        sim.run(net, run_filename=net_name)

        
        print(f"Finished sim {prog}/{len(parameters)}: \t[{i.capa:.4f}µF, {i.cind:.4f}µH, {i.cres:.4f}mΩ]")
        #print(sim.okSim, sim.runno)

    sim.wait_completion()
    for raw, log in sim:
            if log:
                data = PyLTSpice.LTSpiceLogReader(log)
                print(vars(data))
                print([data["current"][0], data["rise"][0], data["fall"][0], data["charge"][0]])
                #print(data["current"])
                parameters[data["test"][0]].curr = data["current"][0]
                parameters[data["test"][0]].rise = data["rise"][0]
                parameters[data["test"][0]].fall = data["fall"][0] - parameters[data["test"][0]].rise
                parameters[data["test"][0]].rech = data["charge"][0] - 1000
                
                #cnts[data["test"][0]] = data["current"][0]


    print("LTSpice simulation finished.")


    # P3 FEMM Simulation
    print("Starting FEMM...")
    #frcs = [] # forces
    #flds = [] # fields
    femm.openfemm()
    prog=0
    for i in parameters:

        
        #print(test_parameters[i][0])
        #print(dias)
        dim1 = [i.bwid/20 + i.lthi/10, -i.clen/20]
        dim2 = [i.fwid/20, i.clen/20]

        prog+=1
        print(f"Sim {prog}/{len(parameters)}, bounds x({dim1[0]:.2f},{dim2[0]:.2f}) y({dim1[1]:.2f},{dim2[1]:.2f})\t", end="")

        #print(f"{dim1} {dim2} ", end="")
        #print(dim1)
        #print(dim2)
        femm.opendocument("femm/coilgunauto.fem")
        femm.main_minimize()
        femm.mi_saveas(f"pyscripts/output/femm/coilgunauto_scriptsim.fem")
        femm.mi_seteditmode("segments")
        femm.mi_drawrectangle(dim1[0], dim1[1], dim2[0], dim2[1])
        femm.mi_addmaterial("Coilwire", 1, 1, 0, 0, 58, 0, 0, 1, 3, 0, 0, 1, i.wdia)
        femm.mi_modifycircprop("Coil",1,i.curr)
        femm.mi_seteditmode('blocks')
        femm.mi_addblocklabel(((i.bwid/20 + i.lthi/10)+i.fwid/20)/2,0)
        femm.mi_selectlabel(((i.bwid/20 + i.lthi/10)+i.fwid/20)/2,0)
        femm.mi_setblockprop("Coilwire",1,0,"Coil",0,0,i.turn)
        femm.mi_clearselected()
        femm.mi_addblocklabel((i.fwid/2+i.wdia/2)/10+0.1,0)
        femm.mi_selectlabel((i.fwid/2+i.wdia/2)/10+0.1,0)
        femm.mi_setblockprop("Air",1,0,"None",0,0,1)
        femm.mi_clearselected()
        femm.mi_seteditmode("group")
        femm.mi_selectgroup(1)
        femm.mi_movetranslate(0, -(i.clen/20))

        femm.mi_analyze(1)
        femm.mi_loadsolution()
        femm.mo_groupselectblock(1)
        fz=femm.mo_blockintegral(19)
        fl=femm.mo_getb(i.bwid/20-0.1,0)
        
        #frcs.append(fz)
        #flds.append(sqrt(fl[0]**2 + fl[1]**2))
        i.forc = fz
        i.fild = sqrt(fl[0]**2 + fl[1]**2)
        
        print(f"finished with parameters:\t[{i.wdia:.2f}mm, {i.turn:.0f}tu, {i.curr:.2f}A]")

        femm.mi_close()
        #print(fz)

    femm.closefemm()
        
        

        

    #for i in parameters:
    #    print(f"{i.forc} \t {i.fild}")


    #print(flds)
    print(f"FEMM simulation finished. Completed {len(parameters)}/{initialcount} tests.")
    
    
    # P4 Post-processing Data
    print("Calculating post-process data...")
    prog = 0
    accs = []
    spds = []
    tlns = []
    engs = []
    for pm in parameters:
        pm.tlen = pm.clen*pm.scon
        pm.acce = pm.forc/0.006
        pm.sped = sqrt(2*pm.acce*((pm.tlen/1000)))
        pm.engy = (0.5*0.006*(pm.sped**2))

        prog += 1
        
        print(f"Done data point {prog}/{len(parameters)}.")
    print("Post-process data calculated.")

    print()





    # P5 Results
    print(f"Completed [{len(parameters)}] tests.")
    print("Results ready. Writing to spreadsheet...")
    with open("pyscripts/output/output.csv", 'w', newline='') as file:
        writ = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for i in range(len(parameters)):
            pm = parameters[i]
            writ.writerow([
                i+1,
                pm.wdia,
                pm.bwid,
                pm.bhei,
                pm.lthi,
                pm.turn,
                pm.tpll,
                pm.clen,
                pm.scon,
                pm.tlen,
                pm.capa,
                pm.volt,
                pm.fwid,
                pm.fhei,
                pm.flen,
                pm.fmas,
                pm.cres,
                pm.cind,
                pm.curr,
                pm.rise,
                pm.fall,
                pm.rech,
                pm.fild,
                pm.forc,
                pm.acce,
                pm.sped,
                pm.engy
            ])
            #writ.writerow([i+1, pm[0], pm[1], pm[2], pm[3], pm[6], tlns[i], pm[4], pm[5], dias[i], ress[i], inds[i], cnts[i], flds[i], frcs[i], accs[i], spds[i], engs[i]])

    print("Test [xx]\tWdia [mm]\tBwid [mm]\tBhei [mm]\tLthi [mm]\tTurn [xx]\tTpll [xx]\tClen [mm]\tScon [xx]\tTlen [mm]\tCapa [µF]\tVolt [1V]\tFwid [mm]\tFhei [mm]\tFlen [1m]\tFmas [1g]\tCres [mΩ]\tCind [µH]\tCurr [1A]\tRise [ms]\tFall [ms]\tRech [ms]\tFild [1T]\tForc [1N]\tAcce [m/s2]\tSped [m/s]\tEngy [1J]")
    for i in range(len(parameters)):
        pm = parameters[i]
        print(f"{i+1}\t\t{pm.wdia:.2f}\t\t{pm.bwid:.2f}\t\t{pm.bhei:.2f}\t\t{pm.lthi:.2f}\t\t{pm.turn:.0f}\t\t{pm.tpll:.0f}\t\t{pm.clen:.2f}\t\t{pm.scon:.0f}\t\t{pm.scon*pm.clen:.2f}\t\t{pm.capa:.0f}\t\t{pm.volt:.1f}\t\t{pm.fwid:.2f}\t\t{pm.fhei:.2f}\t\t{pm.flen:.2f}\t\t{pm.fmas:.2f}\t\t{pm.cres:.2f}\t\t{pm.cind:.2f}\t\t{pm.curr:.2f}\t\t{pm.rise:.3f}\t\t{pm.fall:.3f}\t\t{pm.rech:.2f}\t\t{pm.fild:.4f}\t\t{pm.forc:.4f}\t\t{pm.acce:.2f}\t\t{pm.sped:.4f}\t\t{pm.engy:.4f}")
    #print(frcs)







# Data Format, dictionaries
# {wirediameter, barrelwidth, barrelheight (both outer), turncount, coillength, capacitance, voltage, stagecount}



"""
fullsim([Coilsim(Wdia, Bwid, Bhei, Lthi, Turn, Clen, Capa, Volt, Scon)
         for Wdia in [awg(12), awg(14)] # mm (+ AWG)
         for Bwid in [24] # mm
         for Bhei in [3] # mm
         for Lthi in [i for i in range(2,6)] # mm
         for Turn in [i for i in range(25, 200+1, 25)] # count
         for Clen in [50,60,70,80] # mm
         for Capa in [1000,10000] # uF
         for Volt in [63,90] # V
         for Scon in [10] # count
         ],
         "ltspice/coilgunauto2.asc")
"""
#"""
fullsim([Coilsim(Wdia, Bwid, Bhei, Lthi, Turn, Clen, Capa, Volt, Scon)
         for Wdia in [awg(16)] # mm (+ AWG)
         for Bwid in [24] # mm
         for Bhei in [3] # mm
         for Lthi in [3] # mm
         for Turn in [120] # count
         for Clen in [50] # mm
         for Capa in [10000] # uF
         for Volt in [90] # V
         for Scon in [10] # count
         ],
         "ltspice/coilgunauto2.asc")
#"""
"""
fullsim([Coilsim(Wdia, Bwid, Bhei, Lthi, Turn, Clen, Capa, Volt, Scon)
         for Wdia in [awg(12)] # mm (+ AWG)
         for Bwid in [24] # mm
         for Bhei in [3] # mm
         for Lthi in [2] # mm
         for Turn in [75] # count
         for Clen in [40] # mm
         for Capa in [1000] # uF
         for Volt in [63] # V
         for Scon in [20] # count
         ],
         "ltspice/coilgunauto2.asc")
         """