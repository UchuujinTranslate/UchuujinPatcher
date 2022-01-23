# from shutil import copytree, rmtree
import shutil
from tqdm import tqdm
from git import Repo, RemoteProgress
import os, stat

# --------------------------- Delete old versions --------------------------- #
# probably not necessary


# needed for deleting read-only files in .git
def on_rm_error(func, path, exc_info):
    # path contains the path of the file that couldn't be removed
    # let's just assume that it's read-only and unlink it.
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)

try:
    shutil.rmtree("repos", onerror=on_rm_error)
    shutil.rmtree("weblate_scripts")
    shutil.rmtree("master_src")
except FileNotFoundError:
    print("Dirs already deleted.")


# ------------------------- Class and function defs ------------------------- #

# Cloning progress bar
class CloneProgress(RemoteProgress):
    def __init__(self):
        super().__init__()
        self.pbar = tqdm()  # Replace with Rich later on

    def update(self, op_code, cur_count, max_count=None, message=''):
        self.pbar.total = max_count
        self.pbar.n = cur_count
        self.pbar.refresh()
        
    def close(self):
        self.pbar.close()

repo_dir = "repos/"

def CloneRepo(git_url, branch):
    branch_dir = repo_dir + branch
    
    print(f"Cloning {branch} repo...")
    Repo.clone_from(git_url, branch_dir, 
                    branch=branch,
                    progress=CloneProgress(),
                    multi_options=['--depth 1']  # only grab most recent
                    )
    CloneProgress().close()


# ----------------- Make separate versions for both repos ---------------- #
# Clone both repos
#CloneRepo("https://github.com/UchuujinTranslate/extraction-tools.git", "main")
CloneRepo("https://github.com/gil-unx/extraction-tools.git")
#CloneRepo("https://github.com/UchuujinTranslate/uchuujin.git", "weblate")
CloneRepo("https://github.com/gil-unx/uchuujin.git", "weblate")

# Take src from extraction-tools
print("Copying src dir from master branch...")
shutil.copytree("repos/main/src", "main_src")

# Take scripts out of weblate
print("Copying scripts dir from weblate branch...")
shutil.copytree("repos/weblate/scripts", "weblate_scripts")


print("Done!")
