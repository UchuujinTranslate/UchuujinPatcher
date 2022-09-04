import os


def patch_eboot():
    print("patch_eboot.py")
    
    #decrypt eboot
    print("Decrypting eboot...")
    os.system(
        "bin\\deceboot.exe work/isofiles/EBOOT.BIN work/isofiles/EBOOT_DEC.BIN")

    #insert vwf function
    print("Inserting vwf function...")
    os.system("bin\\armips.exe UchuujinPatcher/eboot/EBOOT.asm")


if __name__ == "__main__":
    patch_eboot()
