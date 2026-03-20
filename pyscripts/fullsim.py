import PyLTSpice
import femm

import math
from math import sqrt, log10

import csv

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

def get_current(raw_file, log_file):
    return PyLTSpice.LTSpiceLogReader(log_file)["current"][0]

def fullsim(test_parameters,spice_file=""): # 0 - Wire Diamater [Wdia mm], 1 - Barrel Diameter [Bdia mm], 2 - Turn Count [Turn xx], 3 - Stage Length [Clen mm], 4 - Capacitance [Capa uF], 5 - Voltage [Volt 1V], 6 - Stage Count [Scon xx]

    while True:
        prompt = input(f"About to run [{len(test_parameters)}] tests. \nV - View Tests // C - Cancel // S - Start\n> ")
        if prompt == "C":
            return 0
        elif prompt == "V":
            print("Test [xx]\tWdia [mm]\tBdia [mm]\tTurn [xx]\tClen [mm]\tScon [xx]\tTlen [mm]\tCapa [µF]\tVolt [1V]")
            for i in range(len(test_parameters)):
                pm = test_parameters[i]
                print(f"{i+1}\t\t{pm[0]:.2f}\t\t{pm[1]:.2f}\t\t{pm[2]:.0f}\t\t{pm[3]:.2f}\t\t{pm[6]:.0f}\t\t{pm[3]*pm[6]:.2f}\t\t{pm[4]:.2f}\t\t{pm[5]:.1f}")
        elif prompt == "S":
            break

    copperres = 1.71*10**-8

    # P1 Coil Calculations

    lens = []
    trns = []
    dias = []
    ress = []
    inds = []
    prog = 0
    print("Parameter generation started.")
    for pm in test_parameters:
        tpl = pm[3] // pm[0] # turns per layer

        lay = math.ceil(pm[2]/tpl) # layers

        ttl = wirelength(pm[0], pm[1], pm[2], tpl) # total wire length

        ptn = math.pi*(pm[1]+(pm[0] * (pm[2] // tpl + 1))) # final layer turn length

        dia = math.ceil(pm[2]/tpl)*pm[0]+pm[1] # final diameter

        res = (ttl*copperres)/((pm[0]/2000)**2*math.pi) # final resistance

        ind = ((4*math.pi * 10**-7)*(pm[2]**2)*(math.pi*((dia/2000)**2))/(pm[3]/1000)) * 1000000 # final inductance

        #print(f"Total wire length {ttl:.4f}mm over {lay:.0f} layers, {tpl:.0f} turns per layer, {ptn:.2f}mm length per turn (final layer); final coil width {dia:.2f}mm; total resistance {res:.4f}mΩ, total inductance {ind:.4f}µH")
        lens.append(pm[3])
        trns.append(pm[2])
        dias.append(dia)
        ress.append(res)
        inds.append(ind)
        prog += 1
        print(f"Generated sim {prog}/{len(test_parameters)}:\t[{pm[0]:.2f}mm, {pm[1]:.2f}mm, {pm[2]:.2f}tu, {pm[3]:.2f}mm]")
    print("Table generation completed.")
    #print("TNum (xx)\tWDia (mm)\tBdia (mm)\tTurn (xx)\tClen (mm)\tCdia (mm)\tCrad (mm)\tCres (mΩ)\tCind (µH)")
    #for i in range(len(test_parameters)):
    #    print(f"{i+1}\t\t{test_parameters[i][0]:.2f}\t\t{test_parameters[i][1]:.2f}\t\t{test_parameters[i][2]:.0f}\t\t{test_parameters[i][3]:.2f}\t\t{dias[i]:.2f}\t\t{dias[i]/2:.2f}\t\t{ress[i]:.5f}\t{inds[i]:.5f}")

    pmset = [] # parameter set
    #for i in range(len(test_parameters)):
        #pmset.append({test_parameters[i][0], test_parameters[i][1], test_parameters[i][2], test_parameters[i][3], dias[i], ress[i], inds[i]})
    #print(pmset)
    print("Parameter generation completed.")


    # P2 LTSpice Simulation

    #print("LTSpice parameter tables generated.")

    print("Starting LTSpice...")

    sim = PyLTSpice.SimRunner(output_folder="./output/ltspice",simulator="D:\\ProgramFiles\\LTspice\\LTspice.exe",parallel_sims=10)

    net = PyLTSpice.SpiceEditor(spice_file)

    #net.set_parameters(slen=tb_slen, turns=tb_trns, cdia=tb_cdia, cres=tb_cres, coil=tb_inds)
    #net.add_instructions(f".step PARAM n 1 {len(test_parameters)} 1")

    cnts = {} # currents
    prog = 0
    for i in range(len(test_parameters)): # Run each simulation per generated parameter set
        net.set_parameters(coil=inds[i]*10**-6, cres=ress[i]*10**-3, cap=test_parameters[i][4]*10**-6, involt=test_parameters[i][5], testnum=i)
        #net_name = f"coilgunauto_size{test_parameters[i][0]:.2f}_dia{test_parameters[i][1]:.2f}_turn{test_parameters[i][2]:.2f}_length{test_parameters[i][3]:.2f}.net"
        net_name = f"coilgunauto_{i+1}.net"
        sim.run(net, run_filename=net_name)

        prog += 1
        print(f"Finished sim {prog}/{len(test_parameters)}: \t[{inds[i]:.4f}µH, {ress[i]:.4f}mΩ]")

    sim.wait_completion()
    for raw, log in sim:
            if log:
                data = PyLTSpice.LTSpiceLogReader(log)
                #print(data["current"])
                cnts[data["test"][0]] = data["current"][0]
    #print(cnts)

    
    
    #print(cnts)
    print("LTSpice simulation finished.")


    # P3 FEMM Simulation
    print("Starting FEMM...")
    frcs = [] # forces
    flds = [] # fields
    femm.openfemm()
    prog=0
    for i in range(len(test_parameters)):
        #print(test_parameters[i][0])
        #print(dias)
        dim1 = [test_parameters[i][1]/20, -test_parameters[i][3]/20]
        dim2 = [dias[i]/20, test_parameters[i][3]/20]
        #print(dim1)
        #print(dim2)
        femm.opendocument("../femm/coilgunauto.fem")
        femm.main_minimize()
        femm.mi_saveas(f"./output/femm/coilgunauto_scriptsim.fem")

        femm.mi_seteditmode("segments")
        femm.mi_drawrectangle(dim1[0], dim1[1], dim2[0], dim2[1])

        femm.mi_addmaterial("Coilwire", 1, 1, 0, 0, 58, 0, 0, 1, 3, 0, 0, 1, test_parameters[i][0])

        femm.mi_modifycircprop("Coil",1,cnts[i])

        femm.mi_seteditmode('blocks')

        femm.mi_addblocklabel((test_parameters[i][1]/20+dias[i]/20)/2,0)
        femm.mi_selectlabel((test_parameters[i][1]/10+dias[i]/10)/2,0)
        femm.mi_setblockprop("Coilwire",1,0,"Coil",0,0,test_parameters[i][2])
        femm.mi_clearselected()

        femm.mi_addblocklabel((dias[i]/2+test_parameters[i][0]/2)/10+0.1,0)
        femm.mi_selectlabel((dias[i]/2+test_parameters[i][0]/2)/10+0.1,0)
        femm.mi_setblockprop("Air",1,0,"None",0,0,1)
        femm.mi_clearselected()

        femm.mi_seteditmode("group")

        femm.mi_selectgroup(1)
        femm.mi_movetranslate(0, -(test_parameters[i][3]/20))

        femm.mi_analyze(1)
        femm.mi_loadsolution()

        femm.mo_groupselectblock(1)
        fz=femm.mo_blockintegral(19)
        fl=femm.mo_getb(test_parameters[i][1]/20-0.1,0)
        frcs.append(fz)
        flds.append(sqrt(fl[0]**2 + fl[1]**2))
        prog+=1
        print(f"Finished sim {prog}/{len(test_parameters)}:\t[{test_parameters[i][0]:.2f}mm, {test_parameters[i][2]:.0f}tu, {cnts[i]:.2f}A]")
        

        femm.mi_close()
        #print(fz)

    femm.closefemm()
    #print(flds)
    print("FEMM simulation finished.")
    

    # P4 Post-processing Data
    print("Calculating post-process data...")
    accs = []
    spds = []
    tlns = []
    engs = []
    for i in range(len(test_parameters)):
        pm = test_parameters[i]
        tlen = pm[3]*pm[6]
        acc = frcs[i]/0.006
        spd = sqrt(2*acc*((tlen/1000)))
        accs.append(acc)
        spds.append(spd)
        tlns.append(tlen)
        engs.append(0.5*0.006*(spd**2))
        
        print(f"Done data point {i+1}/{len(test_parameters)}.")
    print("Post-process data calculated.")

    print()



    


    # P5 Results
    print(f"Completed [{len(test_parameters)}] tests.")
    print("Results ready. Writing to spreadsheet...")
    with open("./output/output.csv", 'w', newline='') as file:
        writ = csv.writer(file, delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
        for i in range(len(test_parameters)):
            pm = test_parameters[i]
            writ.writerow([i+1, pm[0], pm[1], pm[2], pm[3], pm[6], tlns[i], pm[4], pm[5], dias[i], ress[i], inds[i], cnts[i], flds[i], frcs[i], accs[i], spds[i], engs[i]])

    print("Test [xx]\tWdia [mm]\tBdia [mm]\tTurn [xx]\tClen [mm]\tScon [xx]\tTlen [mm]\tCapa [µF]\tVolt [1V]\tCdia [mm]\tCres [mΩ]\tCind [µH]\tCurr [1A]\tMfld [1T]\tMfrc [1N]\tAcce [m/s2]\tEspd [m/s]\tEngy [1J]")
    for i in range(len(test_parameters)):
        pm = test_parameters[i]
        print(f"{i+1}\t\t{pm[0]:.2f}\t\t{pm[1]:.2f}\t\t{pm[2]:.0f}\t\t{pm[3]:.2f}\t\t{pm[6]:.0f}\t\t{tlns[i]}\t\t{pm[4]:.2f}\t\t{pm[5]:.1f}\t\t{dias[i]:.2f}\t\t{ress[i]:.2f}\t\t{inds[i]:.2f}\t\t{cnts[i]:.2f}\t\t{flds[i]:.4f}\t\t{frcs[i]:.4f}\t\t{accs[i]:.2f}\t\t{spds[i]:.4f}\t\t{engs[i]:.4f}")
    #print(frcs)

    return 0

# Fullsim Parameters:
# Wire Size, Barrel Diameter, Turn Count, Stage Length, Capacitance (uF), Voltage (V), Stage Count
#fullsim([[awg(y), 33.40, x, 40, z, 90] for x in range(25,250+1,25) for y in [12] for z in [1000]], "../ltspice/coilgunauto.asc")

fullsim([[awg(Wdia), Bdia, Turn, Clen, Capa, Volt, Scon] 
         for Wdia in [awg(12), awg(14), awg(16)] # mm (+ AWG)
         for Bdia in [26] # mm
         for Turn in [200] # count
         for Clen in [50] # mm
         for Capa in [1000, 2000, 3000] # uF
         for Volt in [100] # V
         for Scon in [20] # count
         ], 
         "../ltspice/coilgunauto.asc")
