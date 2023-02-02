# Call sc_patch_translations.py from main repo
# Patches in English text into scripts

# Multiprocess or implement looping through all in 
# normal script
# Implement it normal first, then add multiprocessing

import os
from UchuujinPatcher.sc.sc_patch_translations_tmp import patch_translations
from multiprocessing import Pool
import time

def patch_sc():
    start_time = time.time()

    sc_dir = "work/isofiles/sc/"
    scripts = "work/repos/weblate/scripts/"
    patched_dir = "work/isofiles/sc_patched/"
    scripts_tmp = "work/repos/weblate/scripts/temp/"
    
    try:
        os.mkdir(patched_dir)
    except FileExistsError:
        print("Dir already exists")


    
    multiThreaded = True
    
    input('paused')
    
    if multiThreaded:
        filenames = []
        for filename in os.listdir(sc_dir):
            filenames.append(filename)
        
        # debug var
        filenames = ['0000', '0001', '0003']
        print(filenames)
        
            
        with Pool() as pool:
            pool.map(patch_translations, filenames)
                
        input('paused')

        # do after all are processed
        
        #calculate new pointer sc.cpk
        eboot = open("work/isofiles/EBOOT_patched.BIN", "r+b")
        newScOffset = 0
        ptrOff = 0x147044
        eboot.seek(ptrOff, 0)
        
        print("writing eboot pointers")
        for filename in filenames:
            #print(f'writing for {filename}')
            newScSize =os.path.getsize(patched_dir+filename)#get new sc size
            eboot.write(struct.pack("<HH",newScOffset>>11,newScSize>>11))
            newScOffset+=newScSize
        
        
        
    # # old single threaded version
    # else:
    #     for filename in os.listdir(sc_dir):
    #         print(f"Patching {filename}...")
    #         patch_translations(sc_dir + filename,
    #                         scripts_tmp + filename + ".json",
    #                         scripts + "en_US/" + filename + ".po", 
    #                         patched_dir,
    #                         scripts + filename + ".json"
    #                         )
            

    #         newScSize =os.path.getsize(patched_dir+filename)#get new sc size
    #         eboot.write(struct.pack("<HH",newScOffset>>11,newScSize>>11))
    #         newScOffset+=newScSize
        
    elapsed_time = time.time() - start_time
    print('sc patch time:', time.strftime(
            "%H:%M:%S", time.gmtime(elapsed_time)))
        
if __name__ == "__main__":
    patch_sc()
