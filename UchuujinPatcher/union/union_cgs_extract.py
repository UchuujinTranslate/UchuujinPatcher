import shutil
import os
import struct
import json
import gzip
def cgs_extract():
    os.makedirs(os.path.dirname("work/isofiles/cgs/"), exist_ok=True)
    shutil.copytree("work/repos/weblate/cgs_translated", "work/isofiles/cgs_translated")
    cwd = os.getcwd()
    meta = json.loads(open("UchuujinPatcher/union/cgs.json", "rb").read())
    print(cwd)
    for union_index in meta:
        f = open("work/isofiles/union/{}".format(union_index), "rb")
        info = meta[str(union_index)]
        open("work/isofiles/cgs/{}.json".format(union_index), 'wb').write(json.dumps(info, indent=4).encode("utf-8"))
        pixel_index = 1
        for pal, pix in zip(info["content"]["pallete"], info["content"]["pixel"]):
            f.seek(pal["offset"])
            pallete = f.read(pal["size"])
            pixel = b""
            for off, size in zip(pix["chunk_offset"], pix["gzip_csizes"]):
                f.seek(off + pix["offset"] + 16)
                pixel += gzip.decompress(f.read(size))
            gim = open("work/isofiles/temp.gim".format(union_index, pixel_index), 'wb')
            hdr = [0x2E47494D, 0x312E3030,
                   0x00505350,
                   0x00000000,
                   0x02,
                   0x000104C0,  # tsize +0x4c0
                   0x00000010,  #
                   0x00000010,  #
                   0x03,  #
                   0x000104B0,  #
                   0x00000010,  #
                   0x00000010,  #
                   0x04,  #
                   0x00010050,  # tsize +0x50
                   0x00010050,  # tsize +0x50
                   0x00000010,  #
                   0x30,  #
                   0x00010005,  #
                   0x00000100,  # w
                   0x00000100,  # h
                   0x00100008,  #
                   0x00020008,  #
                   0x00000000,  #
                   0x00000030,  #
                   0x00000040,  #
                   0x00010040,  # tsize +0x40
                   0x00000000,  #
                   0x00010001,  #
                   0x00010003,  #
                   0x00000040,  #
                   0x00000000,  #
                   0x00000000,  #
                   0x00000000,  #
                   ]
            hdr[5] = len(pixel) + 0x4c0
            hdr[9] = len(pixel) + 0x4b0
            hdr[13] = len(pixel) + 0x50
            hdr[14] = len(pixel) + 0x50
            hdr[18] = pix["width"]
            pix["height"] = len(pixel) // pix["width"]
            hdr[19] = pix["height"]
            hdr[25] = len(pixel) + 0x40
            if pix["format"] == "-pspindex4":
                hdr[17] = 0x00010004
                hdr[18] = pix["width"]
                pix["height"] = len(pixel) // pix["width"] * 2
                hdr[19] = pix["height"]
                hdr[20] = 0x00100004
            gim.write(struct.pack("<18I2H13I", *hdr))
            gim.write(pixel)
            gim.write(
                b'\x05\x00\x00\x00P\x04\x00\x00P\x04\x00\x00\x10\x00\x00\x000\x00\x00\x00\x03\x00\x00\x00\x00\x01\x01\x00 \x00\x10\x00\x01\x00\x02\x00\x00\x00\x00\x000\x00\x00\x00@\x00\x00\x00@\x04\x00\x00\x00\x00\x00\x00\x02\x00\x01\x00\x03\x00\x01\x00@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
            gim.write(pallete)
            gim.flush()
            gim.close()
            os.system(
                "bin\\GimConv\\GimConv.exe work/isofiles/temp.gim -o {2}/work/isofiles/cgs/{0}_{1:02d}.png".format(
                    union_index, pixel_index, cwd))
            os.remove("work/isofiles/temp.gim")
            pixel_index += 1
        if info["content"]["map"]:
            map = open("work/isofiles/cgs/{0}.map".format(union_index), "wb")
            f.seek(info["content"]["map"]["offset"])
            map.write(f.read(info["content"]["map"]["size"]))
if __name__ == "__main__":
    cgs_extract()
