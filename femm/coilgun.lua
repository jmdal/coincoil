showconsole()
mydir="./"
open(mydir .. "coilgun.fem")
mi_saveas(mydir .. "temp.fem")
mi_seteditmode("group")
total=0
max=0
for n=0,50 do
	mi_analyze()
	mi_loadsolution()
	mo_groupselectblock(1)
	fz=mo_blockintegral(19)
	print((50-n)/10,"cm from center",fz)
	total=total+fz
	if (n<50) then
		mi_selectgroup(1)
    	mi_movetranslate(0,0.1)
	end
	if (fz>max) then
		max=fz
	end
end
print("total",total)
print("max",max)
mo_close()
mi_close()
