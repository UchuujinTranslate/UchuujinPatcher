import shutil
import struct
import os
import gzip
import io,glob
infos = [[0,0,65536,'pixel',False,None,0],
[1,65536,40960,'pixel',False,None,0],
[2,106496,4096,'pixel',True,1,16],
[3,110592,14336,'pixel',True,5,32],
[4,124928,24576,'pixel',True,3,32],
[5,149504,16384,'pixel',True,2,16],
[6,165888,32768,'pixel',False,None,0],
[7,198656,32768,'pixel',False,None,0],
[8,231424,34816,'pixel',False,None,0],
[9,266240,2048,'pixel',True,1,16],
[10,268288,2048,'pixel',True,1,16],
[11,270336,20480,'pixel',True,4,32],
[12,290816,24576,'pixel',True,2,16],
[13,315392,6144,'pixel',True,4,32],
[14,321536,34816,'pixel',True,4,32],
[15,356352,10240,'pixel',True,2,16],
[16,366592,12288,'pixel',True,2,16],
[17,378880,12288,'pixel',True,2,16],
[18,391168,6144,'pixel',True,1,16],
[19,397312,92160,'pixel',True,4,32],
[20,489472,34816,'pixel',True,6,32],
[21,524288,14336,'pixel',True,4,32],
[22,538624,32768,'pixel',True,2,16],
[23,571392,32768,'pixel',True,4,32],
[24,604160,22528,'pixel',True,4,32],
[25,626688,26624,'bin',False,None,0],
[26,653312,352256,'pixel',False,None,0],
[27,1005568,49152,'pixel',False,None,0],
[28,1054720,1024,'palette',False,None,0],
[29,1055744,256,'palette',False,None,0],
[30,1056000,1024,'palette',False,None,0],
[31,1057024,1024,'palette',False,None,0],
[32,1058048,256,'palette',False,None,0],
[33,1058304,256,'palette',False,None,0],
[34,1058560,256,'palette',False,None,0],
[35,1058816,256,'palette',False,None,0],
[36,1059072,1024,'palette',False,None,0],
[37,1060096,1024,'palette',False,None,0],
[38,1061120,1024,'palette',False,None,0],
[39,1062144,256,'palette',False,None,0],
[40,1062400,1024,'palette',False,None,0],
[41,1063424,1024,'palette',False,None,0],
[42,1064448,1024,'palette',False,None,0],
[43,1065472,1024,'palette',False,None,0],
[44,1066496,1024,'palette',False,None,0],
[45,1067520,1024,'palette',False,None,0],
[46,1068544,1024,'palette',False,None,0],
[47,1069568,256,'palette',False,None,0],
[48,1069824,1024,'palette',False,None,0],
[49,1070848,1024,'palette',False,None,0],
[50,1071872,1024,'palette',False,None,0],
[51,1072896,1024,'palette',False,None,0],
[52,1073920,1024,'palette',False,None,0],
[53,1074944,1024,'palette',False,None,0],
[54,1075968,1024,'palette',False,None,0],
[55,1076992,1024,'palette',False,None,0],
[56,1078016,1024,'palette',False,None,0],
[57,1079040,1024,'palette',False,None,0],
[58,1080064,256,'palette',False,None,0],
[59,1080320,3072,'palette',False,None,0],]

cgsInfo = [[0,29,512,128,4,],
[1,30,256,160,8,],
[3,36,256,320,8,],
[4,28,512,192,8,],
[5,37,512,128,8,],
[12,41,256,192,8,],
[14,43,512,320,8,],
[18,47,128,128,4,],
[20,53,512,384,8,],
[23,56,512,192,8,],
[27,59,512, 96,8,],
]
def calc_checksum(f):
    s = f.tell()
    f.seek(0)
    p1 = 0x11111111
    p2 = 0x11111111
    p3 = 0x11111111
    p4 = 0x11111111
    m = 0xffffffff
    s -= 16
    while s > 0:
        a1 = int.from_bytes(f.read(4), byteorder='little')
        a2 = int.from_bytes(f.read(4), byteorder='little')
        a3 = int.from_bytes(f.read(4), byteorder='little')
        a4 = int.from_bytes(f.read(4), byteorder='little')
        p1 += a1
        p1 = p1 & m
        if p1 < a1:
            p2 += 1 + a2
        else:
            p2 += 0 + a2
        p2 = p2 & m
        p3 += a3
        p3 = p3 & m
        if p3 < a3:
            p4 += 1 + a4
        else:
            p4 += 0 + a4
        p4 = p4 & m
        s -= 16
    # print("%x %x %x %x" % (p1, p2, p3, p4))
    return struct.pack("<IIII", p1, p2, p3, p4)

def compress_file(chunk,ref,dsize,binary):
    ret = io.BytesIO()
    ret.write(struct.pack("I",chunk))
    binary_compressed = io.BytesIO()
    for _ in range(chunk):
        ret.write(struct.pack("I",binary_compressed.tell()+ref))
        binary_compressed.write(struct.pack("IIII", dsize, 0, 0, 0))
        binary_compressed.write(gzip.compress(binary.read(dsize),compresslevel=9))
        align = (16 - (binary_compressed.tell() % 16))
        if align:
            binary_compressed.write(b"\x00" * align)
    ret.write(struct.pack("I", binary_compressed.tell() + ref))
    align = (16 - (binary_compressed.tell() % 16))
    if align:
        binary_compressed.write(b"\x00" * align)
    ret.seek(ref)
    ret.write(binary_compressed.getbuffer())
    align = (0x800 - (ret.tell() % 0x800))
    if align:
        ret.write(b"\x00" * align )
    checksum = calc_checksum(ret)
    ret.seek(-16, 2)
    ret.write(checksum)
    ret.seek(0)
    return ret.read()
def cgs_pack():
    cwd = os.getcwd()
    for info in cgsInfo:
        id_pixel,id_palette,pix_width,pix_height,form = info
       
        if os.path.exists("work/isofiles/pr_cgs_translated/{0:02d}.png".format(id_pixel)):
            
            os.system("bin\\GimConv\\GimConv.exe work/isofiles/pr_cgs_translated/{1:02d}.png -o {0}/work/isofiles/temp{3}.gim -pspindex{2}".format(cwd, id_pixel,form,id_pixel))
            gim = open("work/isofiles/temp{0}.gim".format(id_pixel), 'rb')
            gim.seek(0x44)
            gim_format = struct.unpack("H", gim.read(2))[0]
            gim.seek(0x34)
            pixel_size = struct.unpack("I", gim.read(4))[0] - 0x50
            if (gim_format != 4) and (gim_format != 5):
                print("Invalid gim format, make sure the png format are indexed color.")
                sys.exit()
            gim.seek(0x80)
            pixel = gim.read(pixel_size)
            gim.seek(4, 1)
            palet_size = struct.unpack("I", gim.read(4))[0] - 0x50
            if gim_format == 4:
                palet_size = 0x100
            gim.seek(0x48, 1)
            pallete = gim.read(palet_size)
            gim.close()
            open("work/isofiles/pr_patched/{0:04d}.pixel".format(id_pixel),"wb").write(pixel)
            open("work/isofiles/pr_patched/{0:04d}.palette".format(id_palette),"wb").write(pallete)
        
def pr_pack():
    os.makedirs(os.path.dirname("work/isofiles/pr_patched/"), exist_ok=True)
    cgs_pack()
    shutil.copy("work/isofiles/pr.bin","work/isofiles/pr_patched.bin")
    pr = open("work/isofiles/pr_patched.bin","r+b")
    for info in infos:
        id,offset,size,type,compress,chunk,ref = info
        pr.seek(offset,0)
        if os.path.exists("work/isofiles/pr_patched/{0:04d}.{1}".format(id,type)):
            if compress == True:
                dec = open("work/isofiles/pr_patched/{0:04d}.{1}".format(id,type),"rb").read()
                buff = compress_file(chunk,ref, len(dec)//chunk,io.BytesIO(dec))
            else:
                buff = open("work/isofiles/pr_patched/{0:04d}.{1}".format(id,type),"rb").read()
            if len(buff)>size:
                open("work/isofiles/pr_fail_{0:04d}.{1}".format(id,type),"wb").write(buff)
                print("Modified file is larger than original,skip insert!!",id,hex(size),hex(len(buff)))
            else:
                pr.write(buff)
    checksum = calc_checksum(pr)
    pr.seek(-16, 2)
    pr.write(checksum)
    pr.flush()
    pr.close()
if __name__ == "__main__":
    pr_pack()
