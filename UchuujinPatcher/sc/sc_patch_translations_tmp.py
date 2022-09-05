import binascii
import os
import sys, struct, json
import io
from os.path import basename
import polib

def patch_translations(sc_file, meta, po, patched_dir, meta2):
    sc = open(sc_file, 'rb')
    sc_name = basename(sc_file)
    meta = json.load(open(meta, 'r', encoding='utf-8'))
    po = polib.pofile(po)
    # patched_dir = (patched_dir)
    meta2 = json.load(open(meta2, 'r', encoding='utf-8'))
    table = {
    "⠀":0x0000,
    " ":0x0000,
    ",":0x0003,
    ".":0x0004,
    ":":0x0006,
    ";":0x0007,
    "?":0x0008,
    "!":0x0009,
    "\"":0x000A,
    "\'":0x000C,
    "～" :0x0020,
    "~" :0x0020,
    "(":0x0029,
    ")":0x002A,
    "[":0x002D,
    "]":0x002E,
    "{":0x002F,
    "}":0x0030,
    "+":0x003B,
    "–":0x003c,
    "—":0x003C,
    "-":0x003C,
    "=":0x0040,
    "¥":0x004e,
    "%":0x0052,
    "#":0x0053,
    "&":0x0054,
    "*":0x0055,
    "@":0x0056,
    "0":0x0092,
    "1":0x0093,
    "2":0x0094,
    "3":0x0095,
    "4":0x0096,
    "5":0x0097,
    "6":0x0098,
    "7":0x0099,
    "8":0x009A,
    "9":0x009B,
    "A":0x009C,
    "B":0x009D,
    "C":0x009E,
    "D":0x009F,
    "E":0x00A0,
    "F":0x00A1,
    "G":0x00A2,
    "H":0x00A3,
    "I":0x00A4,
    "J":0x00A5,
    "K":0x00A6,
    "L":0x00A7,
    "M":0x00A8,
    "N":0x00A9,
    "O":0x00AA,
    "P":0x00AB,
    "Q":0x00AC,
    "R":0x00AD,
    "S":0x00AE,
    "T":0x00AF,
    "U":0x00B0,
    "V":0x00B1,
    "W":0x00B2,
    "X":0x00B3,
    "Y":0x00B4,
    "Z":0x00B5,
    "a":0x00B6,
    "b":0x00B7,
    "c":0x00B8,
    "d":0x00B9,
    "e":0x00BA,
    "f":0x00BB,
    "g":0x00BC,
    "h":0x00BD,
    "i":0x00BE,
    "j":0x00BF,
    "k":0x00C0,
    "l":0x00C1,
    "m":0x00C2,
    "n":0x00C3,
    "o":0x00C4,
    "p":0x00C5,
    "q":0x00C6,
    "r":0x00C7,
    "s":0x00C8,
    "t":0x00C9,
    "u":0x00CA,
    "v":0x00CB,
    "w":0x00CC,
    "x":0x00CD,
    "y":0x00CE,
    "z":0x00CF,
    "é":0x01cf,#only in café ?
    "è":0x01cf,
    }
    f = open("UchuujinPatcher/sc/uchuujin.tbl", "r", encoding="utf-8")
    gtbl = {}
    for line in f:
        if line[0] != "#":
            val, key = line[:-1].split("=", 1)
            val = int(val, 16)
            key = str(key.replace("\\n", "\n"))
            gtbl[key] = val
    table.update(gtbl)

    def encode(asc):
        ret = b""
        length = len(asc)
        asc += "[{FFFF}]"
        i = 0
        while i < length:
            c = asc[i]
            if asc[i] == "[" and asc[i + 1] == "{" and asc[i + 6] == "}" and asc[i + 7] == "]":
                ret += struct.pack("<H", int(asc[i + 2:i + 6], 16))
                i += 8
            elif asc[i] == "\n":    # newline
                ret += struct.pack("<H", 0xfffe)
                i+=1
            elif asc[i] == "\\" and  asc[i+1] == "n":
                ret += struct.pack("<H", 0xfffe)
                i+=2
            elif  asc[i] == "." and asc[i+1] == "." and asc[i+2] == ".":
                ret += struct.pack("<H", 0x23) # 3 periods to elipsis
                i+=3
            elif asc[i] == "!" and asc[i+1] == "!":
                ret += struct.pack("<H", 0x017f)
                i+=2
            elif asc[i] == "!" and asc[i+1] == "?":
                ret += struct.pack("<H", 0x0180)
                i+=2
            elif asc[i] == "…":
                ret += struct.pack("<H", 0x23)
                i+=1
            elif c in table:
                ret += struct.pack("<H", table[c])
                i += 1
            else:
                print("uncaught chr "+c)
                print("skip chr")
                input("press any key")
                i+=1

        return ret,len(ret)


    def updateOffsets(offsets,current,inc):
        newOffsets = []
        for offset in offsets:
            if offset > current:
                offset+=inc
            newOffsets.append(offset)
        return newOffsets


    patched = io.BytesIO()
    newBuff = io.BytesIO()
    patched.write(binascii.unhexlify(meta["UNK"].encode("ASCII")))
    patched.seek(0x80)
    patched.write(struct.pack("<IIII", meta["id"], meta["total"], meta["ptrs"], meta["extra"]))
    newBuff.write(bytes(meta["ptr2"]["size"]))
    newBuff.write(binascii.unhexlify(meta["ptr2"]["ctrl_code"].encode("ASCII")))
    newOffset = newBuff.tell()

    #update speaker & text from *.po
    for i in range(0, len(meta2)):
        dialog = meta2[i]

        dialog["speaker"] = dialog["speaker"].replace('\\n', '\n')
        dialog["text"] = dialog["text"].replace('\\n', '\n')
        index = dialog["id"]

        speakerTranslation = ""
        textTranslation = ""

        for entry in po:
            warning = int(str(entry).split("\n")[1][-1:])

            if len(entry.msgstr) > 0:
                # print("matching...");
                # print("msgid: %s;\ndialo: %s;\nspeak: %s;\n" %
                #       (entry.msgid, dialog["speaker"], dialog["text"]));

                if entry.msgid == dialog["speaker"]:
                    speakerTranslation = entry.msgstr
                    print("speakerMatch: %s -> %s\n" %
                        (entry.msgid.rstrip(), speakerTranslation.rstrip()))

                if entry.msgid == dialog["text"]:
                    textTranslation = entry.msgstr
                    print("textMatch: %s -> %s\n" %
                        (entry.msgid.rstrip(), textTranslation.rstrip()))


        try:
            # Insert speaker
            if len(speakerTranslation) > 0:
                meta["contents"][index]["speaker"] = speakerTranslation

            # Insert text
            if len(textTranslation) > 0:
                meta["contents"][index]["text"] = textTranslation+'\n'
        except:
            print("wrong id",sc_name)
            print(dialog)




    #main section
    for i in range(meta["total"]):
        patched.write(struct.pack("<I", newOffset))
        newBuff.write(struct.pack("<HH", meta["contents"][i]["magic"], meta["contents"][i]["id"]))
        newSpeaker = meta["contents"][i]["speaker"]
        newText = meta["contents"][i]["text"]



        bSpeaker,newLenSpeaker = encode(newSpeaker)
        inc = newLenSpeaker - meta["contents"][i]["speaker_len"]
        meta["ptr2"]["offsets"] = updateOffsets(meta["ptr2"]["offsets"],newBuff.tell(),inc)
        newBuff.write(bSpeaker)

        newBuff.write(b"\xff\xff")


        bText, newLenText = encode(newText)
        inc = newLenText - meta["contents"][i]["text_len"]
        meta["ptr2"]["offsets"] = updateOffsets(meta["ptr2"]["offsets"], newBuff.tell(), inc)
        newBuff.write(bText)


        newBuff.write(binascii.unhexlify(meta["contents"][i]["ctrl_code"].encode("ASCII")))
        newOffset = newBuff.tell()
    patched.seek(meta["ptrs"] + 0x80)



    # extra section
    if meta["extra"] > 0:
        for extra in meta["extra_section"]:
            ptr = [0, 0, 0, 0, 0, 0, 0, 0]
            ptr[0] = extra["id"]
            for i in range(extra["total"]):
                newOffset = newBuff.tell()
                ptr[i + 1] = newOffset
                newText = extra["contents"][i]["text"]
                bText, newLenText = encode(newText)
                inc = newLenText - extra["contents"][i]["text_len"]
                meta["ptr2"]["offsets"] = updateOffsets(meta["ptr2"]["offsets"], newBuff.tell(), inc)
                newBuff.write(bText)
                newBuff.write(binascii.unhexlify(extra["contents"][i]["ctrl_code"].encode("ASCII")))
            patched.write(struct.pack("<IIIIIIII", *ptr))

    newBuff.seek(0)
    newBuff.write(struct.pack("<{}I".format(meta["ptr2"]["total"]+1),meta["ptr2"]["size"],*meta["ptr2"]["offsets"]))
    patched.seek(0x800, 0)
    patched.write(newBuff.getbuffer())
    align = 0x1000 - (patched.tell() % 0x1000)#size align
    patched.write(b"\x00"*align)



    s = patched.tell()
    patched.seek(0)
    p1 = 0x11111111
    p2 = 0x11111111
    p3 = 0x11111111
    p4 = 0x11111111
    m = 0xffffffff
    s -= 16
    while s > 0:
        a1 = int.from_bytes(patched.read(4), byteorder='little')
        a2 = int.from_bytes(patched.read(4), byteorder='little')
        a3 = int.from_bytes(patched.read(4), byteorder='little')
        a4 = int.from_bytes(patched.read(4), byteorder='little')
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
    print("%x %x %x %x" % (p1, p2, p3, p4))
    checksum = struct.pack("<IIII", p1, p2, p3, p4)
    patched.seek(-16, 2)
    patched.write(checksum)
    open(patched_dir+sc_name,"wb").write(patched.getbuffer())

