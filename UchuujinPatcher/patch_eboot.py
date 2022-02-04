import os

#decrypt eboot
os.system("bin\\deceboot.exe isofiles/EBOOT.BIN isofiles/EBOOT_DEC.BIN")



#insert vwf function
os.system("bin\\armips.exe repos/main/EBOOT.asm")
