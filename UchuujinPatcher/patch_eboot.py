import os


def patch_eboot():
    #decrypt eboot
    os.system("bin\\deceboot.exe isofiles/EBOOT.BIN isofiles/EBOOT_DEC.BIN")

    #insert vwf function
    os.system("bin\\armips.exe UchuujinPatcher/eboot/EBOOT.asm")


if __name__ == "__main__":
    patch_eboot()
