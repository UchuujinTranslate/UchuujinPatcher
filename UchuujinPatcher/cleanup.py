import os
import shutil
import stat

# --------------------------- Delete old versions --------------------------- #
# probably not necessary


# needed for deleting read-only files in .git
def on_rm_error(func, path, exc_info):
    # path contains the path of the file that couldn't be removed
    # let's just assume that it's read-only and unlink it.
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)


def del_last_ver():
    # more graceful way of doing this than try for each line?
    try:
        shutil.rmtree("repos", onerror=on_rm_error)
    except FileNotFoundError:
        print("Dir already deleted.")
        
    try:
        shutil.rmtree("weblate_scripts")
    except FileNotFoundError:
        print("Dir already deleted.")
        
    try:
        shutil.rmtree("main_src")
    except FileNotFoundError:
        print("Dir already deleted.")
        
    try:
        shutil.rmtree("isofiles")
    except FileNotFoundError:
        print("Dir already deleted.")
        
    try:
        os.remove("NichiPatched.iso")
    except FileNotFoundError:
        print("Dirs already deleted.")


if __name__ == "__main__":
    del_last_ver()
