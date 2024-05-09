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
    # need VS C++ 2015 redist installed, 
    # will NOT generate patched version without it installed
    # will NOT give error, will cause scripts to break down the line
    # https://www.microsoft.com/en-US/download/details.aspx?id=48145


if __name__ == "__main__":
    patch_eboot()
