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

import os
import time

import UchuujinPatcher.create_binary_patch
import UchuujinPatcher.replace_iso
import UchuujinPatcher.pr_pack
import UchuujinPatcher.union_pack
import UchuujinPatcher.union.union_cgs_insert
import UchuujinPatcher.cpk_pack
import UchuujinPatcher.adjust_width_font
import UchuujinPatcher.patch_lt
import UchuujinPatcher.patch_eboot
import UchuujinPatcher.pr_dump
import UchuujinPatcher.cpk_dump
import UchuujinPatcher.decompress_iso
import UchuujinPatcher.clone_repo
import UchuujinPatcher.cleanup

start_time = time.time()

# preparing
UchuujinPatcher.cleanup.del_last_ver()
UchuujinPatcher.clone_repo.clone_repos()

# extracting iso files
UchuujinPatcher.decompress_iso.decompress_iso()
UchuujinPatcher.cpk_dump.cpk_dump()

# import UchuujinPatcher.union_dump
# UchuujinPatcher.union_dump.union_dump()

# import UchuujinPatcher.union.union_cgs_extract
# UchuujinPatcher.union.union_cgs_extract.cgs_extract()

UchuujinPatcher.pr_dump.pr_dump()

# patching cpk files
UchuujinPatcher.patch_eboot.patch_eboot()
UchuujinPatcher.patch_lt.patch_lt()
UchuujinPatcher.adjust_width_font.adjust_width_font()

# multiprocessing scripts must launch on their own to function properly
# launching as a function will cause main.py to run constantly
os.system("py UchuujinPatcher/patch_sc.py")

# import UchuujinPatcher.patch_sc
# UchuujinPatcher.patch_sc.patch_sc()

UchuujinPatcher.cpk_pack.cpk_pack_sc()
# UchuujinPatcher.union.union_cgs_insert.cgs_insert()
# UchuujinPatcher.union_pack.cpk_pack_union()
UchuujinPatcher.pr_pack.pr_pack()

# inserting iso files
UchuujinPatcher.replace_iso.replace_iso()
UchuujinPatcher.create_binary_patch.create_binary_patch()

print("All done!")

elapsed_time = time.time() - start_time
print('Execution time:', time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))
