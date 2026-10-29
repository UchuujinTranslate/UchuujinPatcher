# Put into same work dir

# Not a great solution, but need to use CriPakTools for this
# Windows only currently... Compile for Linux build.
import os
from shutil import copyfile, rmtree
try:
    from UchuujinPatcher import console
except ImportError:
    import console

# # Clean before proceeding
# try:
#     rmtree("isofiles")
# except FileNotFoundError:
#     print("Dirs already deleted.")

def cpk_dump():
    # Make dir
    
    try:
        os.mkdir("work/isofiles/sc")
    except FileExistsError:
        console.warn("work/isofiles/sc already exists")


    # Copy CPT and sc.cpk into same directory so ALL arg doesn't get put in root dir
    copyfile("bin/CriPakTools.exe", "work/isofiles/sc/CriPakTools.exe")
    copyfile("work/isofiles/sc.cpk", "work/isofiles/sc/sc.cpk")

    # Must execute in same dir as well
    cwd = os.getcwd()
    os.chdir("work/isofiles/sc")
    console.info("Dumping sc.cpk contents")
    console.run(".\\CriPakTools.exe sc.cpk ALL", "CriPakTools")

    # Delete tools
    os.remove("CriPakTools.exe")
    os.remove("sc.cpk")

    # Go back to root dir
    # print(cwd)
    os.chdir(cwd)


if __name__ == "__main__":
    cpk_dump()
