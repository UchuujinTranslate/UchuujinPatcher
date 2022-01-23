# https://pypi.org/project/bsdiff4/

# Use bsdiff and eboot patch in main repo

# Needs wheel and VC++ 2015 v140 toolset (choco install vcbuildtools)
# on Windows, look into Linux / Docker

import bsdiff4

bsdiff4.file_patch("isofiles/lt.bin",
                   "isofiles/lt_patched.bin",
                   "repos/main/lt.bin.patch"
                   )
