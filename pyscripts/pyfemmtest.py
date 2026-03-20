import femm

femm.openfemm()
femm.opendocument("../femm/coilgunauto.fem")
femm.mi_saveas("./output/femm/temp.fem")

z=[]
f=[]
for n in range(0,50):
	"""
	femm.mi_analyze()
	femm.mi_loadsolution()
	femm.mo_groupselectblock(1)
	fz=femm.mo_blockintegral(19)
	z.append(n*0.1)
	f.append(fz)
	femm.mi_selectgroup(1)
	femm.mi_movetranslate(0, 0.1)
	"""
	break

femm.mi_seteditmode("segments")
femm.mi_drawrectangle(1.67,-3.00,2.33,3.00)

femm.mi_addmaterial("Coilwire", 1, 1, 0, 0, 58, 0, 0, 1, 3, 0, 0, 1, 2.05)

femm.mi_modifycircprop("Coil",1,60)

femm.mi_seteditmode('blocks')

femm.mi_addblocklabel(2,0)
print(femm.mi_selectlabel(2,0))
femm.mi_setblockprop("Coilwire",1,0,"Coil",0,0,100)
femm.mi_clearselected()

femm.mi_addblocklabel(2.43,0)
print(femm.mi_selectlabel(2.43,0))
femm.mi_setblockprop("Air",1,0,"None",0,0,1)
femm.mi_clearselected()

femm.mi_seteditmode("group")

femm.mi_selectgroup(1)
femm.mi_movetranslate(0, 5-3)

femm.mi_analyze()
femm.mi_loadsolution()

femm.mo_groupselectblock(1)
fz=femm.mo_blockintegral(19)
z.append(n*0.1)
f.append(fz)

femm.closefemm()
print(z)
print(f)
