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

# Make dir
os.mkdir("isofiles/pack")


# Copy CPT and sc.cpk into same directory so ALL arg doesn't get put in root dir
copyfile("bin/CriPakTools.exe", "isofiles/pack/CriPakTools.exe")
copyfile("isofiles/sc.cpk", "isofiles/pack/sc.cpk")

# Must execute in same dir as well
cwd = os.getcwd()
os.chdir("isofiles/pack")
os.system("CriPakTools.exe sc.cpk ALL")

# Delete tools
os.remove("CriPakTools.exe")
os.remove("sc.cpk")

# Go back to root dir
# print(cwd)
os.chdir(cwd)
