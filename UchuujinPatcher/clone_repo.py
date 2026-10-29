import shutil
from tqdm import tqdm
from git import Repo, RemoteProgress
from git.exc import GitError
import os
try:
    from UchuujinPatcher import console
except ImportError:
    import console

# ------------------------- Class and function defs ------------------------- #

# Cloning progress bar
class CloneProgress(RemoteProgress):
    def __init__(self):
        super().__init__()
        self.pbar = tqdm(bar_format="    {l_bar}{bar:30}{r_bar}")  # Replace with Rich later on

    def update(self, op_code, cur_count, max_count=None, message=''):
        self.pbar.total = max_count
        self.pbar.n = cur_count
        self.pbar.refresh()

    def close(self):
        self.pbar.close()

repo_dir = "work/repos/"

def CloneRepo(git_url, branch, folder):
    branch_dir = repo_dir + "/" + folder

    console.info(f"Cloning {branch} branch of {git_url.rsplit('/', 1)[-1]}")
    progress = CloneProgress()
    Repo.clone_from(git_url, branch_dir,
                    branch=branch,
                    progress=progress,
                    multi_options=['--depth 1']  # only grab most recent
                    )
    progress.close()


def UpdateRepo(git_url, branch, folder):
    """Clone the repo, or update an existing clone to the latest commit."""
    branch_dir = repo_dir + "/" + folder
    name = f"{git_url.rsplit('/', 1)[-1]} ({branch})"

    if not os.path.isdir(os.path.join(branch_dir, ".git")):
        CloneRepo(git_url, branch, folder)
        return

    try:
        repo = Repo(branch_dir)
        old = repo.head.commit.hexsha
    except GitError:
        console.warn(f"Existing clone of {name} is unusable, cloning again")
        shutil.rmtree(branch_dir, onerror=_on_rm_error)
        CloneRepo(git_url, branch, folder)
        return

    try:
        repo.git.fetch("--depth", "1", "origin", branch)
        repo.git.reset("--hard", "FETCH_HEAD")
    except GitError as e:
        console.warn(f"Could not update {name}, using existing copy "
                     f"({old[:7]}): {str(e).splitlines()[-1].strip()}")
        return

    new = repo.head.commit.hexsha
    if new == old:
        console.info(f"{name} already up to date ({new[:7]})")
    else:
        console.ok(f"Updated {name}: {old[:7]} -> {new[:7]}")


def _on_rm_error(func, path, exc_info):
    # .git files are read-only on Windows
    import stat
    os.chmod(path, stat.S_IWRITE)
    os.unlink(path)


def clone_repos():
    UpdateRepo("https://github.com/UchuujinTranslate/uchuujin.git", "weblate", "weblate")
    UpdateRepo("https://github.com/UchuujinTranslate/cgs.git", "main", "cgs")


if __name__ == "__main__":
    clone_repos()
