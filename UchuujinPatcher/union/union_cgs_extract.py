import shutil
import os
import struct
import json
import gzip
from concurrent.futures import ThreadPoolExecutor
try:
    from UchuujinPatcher import console
except ImportError:
    import console
def copy_cgs_translated():
    # translations come from the repo, so this is redone on every run
    shutil.rmtree("work/isofiles/cgs_translated", ignore_errors=True)
    shutil.copytree("work/repos/cgs/cgs_translated", "work/isofiles/cgs_translated")
    console.info("Copied translated CG images")


def cgs_extract():
    os.makedirs(os.path.dirname("work/isofiles/cgs/"), exist_ok=True)
    cwd = os.getcwd()
    meta = json.loads(open("UchuujinPatcher/union/cgs.json", "rb").read())
    console.info(f"Extracting {len(meta)} CG files from union.cpk")
    # GIM files are written one by one (cheap), then converted to PNG in
    # parallel since each GimConv call is a separate process
    os.makedirs("work/isofiles/gim_tmp", exist_ok=True)
    jobs = []
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
            gim_path = "work/isofiles/gim_tmp/{0}_{1:02d}.gim".format(union_index, pixel_index)
            gim = open(gim_path, 'wb')
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
            jobs.append((gim_path, "{0}/work/isofiles/cgs/{1}_{2:02d}.png".format(
                cwd, union_index, pixel_index)))
            pixel_index += 1
        if info["content"]["map"]:
            map = open("work/isofiles/cgs/{0}.map".format(union_index), "wb")
            f.seek(info["content"]["map"]["offset"])
            map.write(f.read(info["content"]["map"]["size"]))

    def convert(job):
        gim_path, png_path = job
        console.run(
            "bin\\GimConv\\GimConv.exe {0} -o {1}".format(gim_path, png_path),
            "GimConv " + os.path.basename(gim_path))
        os.remove(gim_path)

    workers = min(32, (os.cpu_count() or 4) * 2)
    console.info(f"Converting {len(jobs)} images to PNG using {workers} workers")
    with ThreadPoolExecutor(max_workers=workers) as pool:
        for done, _ in enumerate(pool.map(convert, jobs), 1):
            console.progress(done, len(jobs), "images")
    os.rmdir("work/isofiles/gim_tmp")
if __name__ == "__main__":
    cgs_extract()
    copy_cgs_translated()
