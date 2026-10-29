import os
try:
    from UchuujinPatcher import console
except ImportError:
    import console
try:
    from UchuujinPatcher.sc import text_layout
except ImportError:
    from sc import text_layout


def decrypt_eboot():
    # only depends on the original iso, so the result can be cached
    console.info("Decrypting EBOOT.BIN")
    console.run("bin\\deceboot.exe work/isofiles/EBOOT.BIN work/isofiles/EBOOT_DEC.BIN")


def patch_eboot():
    #insert vwf function
    console.info("Inserting variable-width font function")
    console.info(f"Setting game line limit to {text_layout.MAX_COLUMNS} glyphs")
    console.run(f"bin\\armips.exe -equ LINE_COLS {text_layout.MAX_COLUMNS} UchuujinPatcher/eboot/EBOOT.asm")
    # need VS C++ 2015 redist installed, 
    # will NOT generate patched version without it installed
    # will NOT give error, will cause scripts to break down the line
    # https://www.microsoft.com/en-US/download/details.aspx?id=48145


if __name__ == "__main__":
    decrypt_eboot()
    patch_eboot()
