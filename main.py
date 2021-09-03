# Use this file to structure the project and
# be the main way to order the scripts

# Order:
# config - Check if exists, if not, go into creation process
# setup

# Setup process, could run together
# mp1 - clone_repo
# mp1 - decompress_iso

# The rest must be in order roughly
# cpk_dump
# mp2 - patch_eboot
# mp2 - patch_sc
# cpk_pack
# replace_iso
# create_binary_patch
# distrib


# Jank way to run all the scripts currently
import os
os.system("py UchuujinPatcher/clone_repo.py")
os.system("py UchuujinPatcher/decompress_iso.py")
os.system("py UchuujinPatcher/cpk_dump.py")
os.system("py UchuujinPatcher/patch_eboot.py")
os.system("py UchuujinPatcher/patch_sc.py")
os.system("py UchuujinPatcher/cpk_pack.py")
os.system("py UchuujinPatcher/replace_iso.py")
