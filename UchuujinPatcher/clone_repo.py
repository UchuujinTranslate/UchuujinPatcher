# from shutil import copytree, rmtree
import shutil
from tqdm import tqdm
from git import Repo, RemoteProgress
import os, stat

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

repo_dir = "work/repos/"

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
def clone_repos():
    # Clone repo
    CloneRepo("https://github.com/UchuujinTranslate/uchuujin.git", "weblate")
    CloneRepo("https://github.com/UchuujinTranslate/uchuujin.git", "master")


    # Take scripts out of weblate
    print("Copying scripts dir from weblate branch...")
    shutil.copytree("work/repos/weblate/scripts", "work/weblate_scripts")


    print("Done!")


if __name__ == "__main__":
    clone_repos()
