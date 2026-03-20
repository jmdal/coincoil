showconsole()
mydir="./"
open(mydir .. "coilgunlong.fem")
mi_saveas(mydir .. "temp.fem")
mi_seteditmode("group")
for n=0,30 do
	mi_analyze()
	mi_loadsolution()
	mo_groupselectblock(1)
	fz=mo_blockintegral(19)
	print((30-n)/10,"cm from center",fz)
	if (n<30) then
		mi_selectgroup(1)
    	mi_movetranslate(0,0.1)
	end
end
mo_close()
mi_close()
