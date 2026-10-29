# https://pypi.org/project/bsdiff4/

# Use bsdiff and eboot patch in main repo

# Needs wheel and VC++ 2015 v140 toolset (choco install vcbuildtools)
# on Windows, look into Linux / Docker

import bsdiff4
try:
    from UchuujinPatcher import console
except ImportError:
    import console

def patch_lt():
    console.info("Applying lt.bin patch")
    bsdiff4.file_patch("work/isofiles/lt.bin",
                       "work/isofiles/lt_patched.bin",
                    "UchuujinPatcher/lt/lt.bin.patch"
                    )


if __name__ == "__main__":
    patch_lt()
