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

import UchuujinPatcher.cleanup
UchuujinPatcher.cleanup.del_last_ver()

import UchuujinPatcher.clone_repo
UchuujinPatcher.clone_repo.clone_repos()

import UchuujinPatcher.decompress_iso
UchuujinPatcher.decompress_iso.decompress_iso()

import UchuujinPatcher.cpk_dump
UchuujinPatcher.cpk_dump.cpk_dump()
    
import UchuujinPatcher.union_dump
UchuujinPatcher.union_dump.union_dump()

import UchuujinPatcher.union.union_cgs_extract
UchuujinPatcher.union.union_cgs_extract.cgs_extract()

import UchuujinPatcher.patch_eboot
UchuujinPatcher.patch_eboot.patch_eboot()

import UchuujinPatcher.patch_lt
UchuujinPatcher.patch_lt.patch_lt()

import UchuujinPatcher.adjust_width_font
UchuujinPatcher.adjust_width_font.adjust_width_font()

import UchuujinPatcher.patch_sc
UchuujinPatcher.patch_sc.patch_sc()

import UchuujinPatcher.cpk_pack
UchuujinPatcher.cpk_pack.cpk_pack_sc()

import UchuujinPatcher.union.union_cgs_insert
UchuujinPatcher.union.union_cgs_insert.cgs_insert()

import UchuujinPatcher.union_pack
UchuujinPatcher.union_pack.cpk_pack_union()

import UchuujinPatcher.replace_iso
UchuujinPatcher.replace_iso.replace_iso()

import UchuujinPatcher.create_binary_patch
UchuujinPatcher.create_binary_patch.create_binary_patch()

print("All done!")
