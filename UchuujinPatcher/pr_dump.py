import shutil
import struct
import os
import json
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

def cgs_dump():
    for info in cgsInfo:
        cwd = os.getcwd()
        id_pixel,id_palette,pix_width,pix_height,form = info
        print(info)
        pixel = open("work/isofiles/pr/{0:04d}.pixel".format(id_pixel),"rb").read()
        pallete = open("work/isofiles/pr/{0:04d}.palette".format(id_palette),"rb").read()
        pix_height =  len(pixel) // pix_width
        os.makedirs("work/isofiles/pr_cgs/", exist_ok=True)
        gim = open("work/isofiles/temp.gim", 'wb')
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
        hdr[18] = pix_width
        
        hdr[19] = pix_height
        hdr[25] = len(pixel) + 0x40
        if form == 4:
            hdr[17] = 0x00010004
            hdr[18] = pix_width
            pix_height = len(pixel) // pix_width * 2
            hdr[19] = pix_height
            hdr[20] = 0x00100004
        gim.write(struct.pack("<18I2H13I", *hdr))
        gim.write(pixel)
        gim.write(
            b'\x05\x00\x00\x00P\x04\x00\x00P\x04\x00\x00\x10\x00\x00\x000\x00\x00\x00\x03\x00\x00\x00\x00\x01\x01\x00 \x00\x10\x00\x01\x00\x02\x00\x00\x00\x00\x000\x00\x00\x00@\x00\x00\x00@\x04\x00\x00\x00\x00\x00\x00\x02\x00\x01\x00\x03\x00\x01\x00@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
        gim.write(pallete)
        gim.flush()
        gim.close()
        os.system("bin\\GimConv\\GimConv.exe work/isofiles/temp.gim -o {0}/work/isofiles/pr_cgs/{1:02d}.png".format(cwd,id_pixel))
        os.remove("work/isofiles/temp.gim")
def decompress(buff):
    com = io.BytesIO(buff)
    chunk = struct.unpack("I",com.read(4))[0]
    offsets = struct.unpack("{}I".format(chunk+1),com.read((chunk+1)*4))
    ref = offsets[0]
    dec = b""
    for i in range(chunk):
        com.seek(offsets[i]+0x10)
        dec+= gzip.decompress(com.read(offsets[i+1]-offsets[i]-0x10))
    return dec,ref

def pr_dump():
    os.makedirs(os.path.dirname("work/isofiles/pr/"), exist_ok=True)
    shutil.copytree("work/repos/weblate/pr_cgs_translated", "work/isofiles/pr_cgs_translated")
    pr = open("work/isofiles/pr.bin","rb")
    for info in infos:
        id,offset,size,type,compress,chunk,ref = info
        pr.seek(offset,0)
        buff = pr.read(size)
        ref = 0
        if compress == True:
            dec,ref = decompress(buff)
            open("work/isofiles/pr/{0:04d}.{1}".format(id,type),"wb").write(dec)
        else:
           
            open("work/isofiles/pr/{0:04d}.{1}".format(id,type),"wb").write(buff)
        info.append(ref)
        print(info)
        
    cgs_dump()
    
if __name__ == "__main__":
    pr_dump()
