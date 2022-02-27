# Using bsdiff is very slow (never finished properly) and ram intensive (9GB!), not a good option for this use

from datetime import date
import hashlib

originalIso = "2668 - Nichijou - Uchuujin (Japan) (v1.01).iso"
patchedIso = "NichiPatched.iso"

today = date.today()

# Label with latest translation commit or date?
# Date for now
patchFile = f"UchuujinEng_{date.isoformat(today)}.patch"


# Create binary patch
# xdelta?


# Generate md5 hashes for .isos, although xdelta protects against patching incorrect files

# better method to generate md5 hash from large files
# about as fast as normal method, but only uses 5MB of ram (instead of 900MB)!
# from: https://www.kite.com/python/answers/how-to-generate-an-md5-hash-for-large-files-in-python
def makeMD5(filename):
    md5_object = hashlib.md5()
    block_size = 128 * md5_object.block_size
    a_file = open(filename, 'rb')
    
    chunk = a_file.read(block_size)
    while chunk:
        md5_object.update(chunk)
        chunk = a_file.read(block_size)

    md5Hash = md5_object.hexdigest()
    return md5Hash


print("Generating MD5 Hashes...")
originalMD5 = makeMD5(originalIso)
print("Original ISO MD5: " + originalMD5)
patchedMD5 = makeMD5(patchedIso)
print("Patched ISO MD5: " + patchedMD5)
#patchFileMD5 = makeMD5(patchFile)
#print("Patch File MD5: " + patchFileMD5)
patchFileMD5 = "placeholder"

# Create text file
# Make into yml or similar file for player-end patch tool to use?
with open('md5_hashes.txt', 'w') as f:
    f.write("MD5 of original ISO used: \n" + originalMD5 + "\n\n")
    f.write("MD5 of patched ISO generated: \n" + patchedMD5 + "\n\n")
    f.write("MD5 of patch file: \n" + patchFileMD5 + "\n")


# Create zip with all files needed
# readme, patch file, md5 hashes, patcher exe, etc.
# mention in readme for an alternative method: https://www.marcrobledo.com/RomPatcher.js/
