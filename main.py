# Use this file to structure the project and
# be the main way to order the scripts
# mpX = multiprocessing

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

import UchuujinPatcher.clone_repo
UchuujinPatcher.clone_repo.del_old_vers()
UchuujinPatcher.clone_repo.clone_repos()

import UchuujinPatcher.decompress_iso
UchuujinPatcher.decompress_iso.decompress_iso()

import UchuujinPatcher.cpk_dump
UchuujinPatcher.cpk_dump.cpk_dump()

import UchuujinPatcher.patch_eboot
UchuujinPatcher.patch_eboot()

import UchuujinPatcher.patch_lt
UchuujinPatcher.patch_lt()

import UchuujinPatcher.patch_sc
UchuujinPatcher.patch_sc()

import UchuujinPatcher.cpk_pack
UchuujinPatcher.cpk_pack()

import UchuujinPatcher.replace_iso
UchuujinPatcher.replace_iso()

import UchuujinPatcher.create_binary_patch
UchuujinPatcher.create_binary_patch()



# Jank way to run all the scripts currently
# import os

# os.system("py UchuujinPatcher/clone_repo.py")
# os.system("py UchuujinPatcher/decompress_iso.py")
# os.system("py UchuujinPatcher/cpk_dump.py")
# os.system("py UchuujinPatcher/patch_eboot.py")
# os.system("py UchuujinPatcher/patch_lt.py")
# os.system("py UchuujinPatcher/adjust_width_font.py")
# os.system("py UchuujinPatcher/patch_sc.py")
# os.system("py UchuujinPatcher/cpk_pack.py")
# os.system("py UchuujinPatcher/replace_iso.py")
# os.system("py UchuujinPatched/create_binary_patch.py")
