# Put into same work dir

# Not a great solution, but need to use CriPakTools for this
# Windows only currently... Compile for Linux build.
import os
from shutil import copyfile, rmtree

# # Clean before proceeding
# try:
#     rmtree("isofiles")
# except FileNotFoundError:
#     print("Dirs already deleted.")


def union_dump():
    # Make dir
    os.mkdir("work/isofiles/union")

    # Copy CPT and sc.cpk into same directory so ALL arg doesn't get put in root dir
    copyfile("bin/CriPakTools.exe", "work/isofiles/union/CriPakTools.exe")
    copyfile("work/isofiles/union.cpk", "work/isofiles/union/union.cpk")

    # Must execute in same dir as well
    cwd = os.getcwd()
    os.chdir("work/isofiles/union")
    os.system("CriPakTools.exe union.cpk ALL")

    # Delete tools
    os.remove("CriPakTools.exe")
    os.remove("union.cpk")

    # Go back to root dir
    # print(cwd)
    os.chdir(cwd)


if __name__ == "__main__":
    union_dump()
