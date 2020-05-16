import sys
import subprocess
import os
import shutil
from termcolor import colored, cprint

# Check if a path points to a folder or file
def file_check(file_path):
  if os.path.isfile(file_path):
    return "is_file"
  elif os.path.isdir(file_path):
    return "is_dir"
  else:
    raise ValueError("Invalid file path! Please check your input.")

# Split two path (one is parent folder and the other one is child file/folder)
def split_folder(fa, fb):

  if fa in fb:
    pa = fa
    ch = fb
  elif fb in fa:
    pa = fb
    ch = fa
  else:
    return pa, ""

  ch_part = ch.replace(pa, "")
  while ch_part[0] == '/':
    ch_part = ch_part[1:]
  while pa[-1] == "/":
    pa = pa[:-1]
  return pa, ch_part

def get_torrent_name(file_root, aria2_return):
  _, ch_part = split_folder(file_root, aria2_return)
  tor_name = ch_part.split("/")[0]
  print(tor_name)
  return tor_name

# Check current seeding jobs from the logfile
def add_seedings(uploaded_log, file_root, seeding=None):
  _, diff = split_folder(file_root, seeding)
  if seeding and diff:
    if num_folders(diff) == 1:
      with open(uploaded_log, "a") as f:
        f.write(seeding + "\n")

  with open(uploaded_log, "r") as f:
    remainings = f.readlines()

  # Trim the log
  with open(uploaded_log, "w") as f:
    for remain in remainings:
      if remain.strip().strip("/n"):
        f.write(remain)
    f.truncate()

  normal_msg("remaining seeding BT tasks include: ")

  for fname in remainings:
    yellow_msg(fname)


def upload(rclone, source, dest, delete=False):
  filetype = file_check(source)
  if filetype == "is_file":
    dest = dest.replace(os.path.basename(source), "")
  if delete:
    fcmd = "move"
  else:
    fcmd = "copy"

  subprocess.run([rclone, "--ignore-existing", fcmd, source, dest], check=True)

  normal_msg("Finished uploading {} to {}.".format(source, dest))

  if delete:
    warn_msg("{} will be deleted directly instead of "
             "entering seeding ".format(source))


def get_abs_subpath(parent):
  parent = os.path.abspath(parent)
  children = os.listdir(parent)
  for i, child in enumerate(children):
    children[i] = os.path.join(parent, child)
  return children

# Get number of folders (The path must be a directory)
def num_folders(dir_path):
  while dir_path[0] == "/":
    dir_path = dir_path[1:]
  while dir_path[-1] == "/":
    dir_path = dir_path[:-1]
  if dir_path:
    return len(dir_path.split("/"))
  else:
    return 0


# Only delete the child if the child is drectly under the parent folder
def only_direct_delete(parent, child):
  parent = os.path.abspath(parent)
  child = os.path.abspath(child)
  _, diff = split_folder(parent, child)
  if num_folders(diff) == 1:
    warn_msg("Deleting {}.".format(child))
    if file_check(child) == "is_file":
      os.remove(child)
    else:
      shutil.rmtree(child)
    warn_msg("{} Deleted!".format(child))
  else:
    yellow_msg("{} are not directly under {}, skipped.".format(child, parent))

def media_sort(sorter, source, accu, tv_dir, movie_dir):
  subprocess.run([sorter,
                  "-a",
                  accu,
                  "-r",
                  "--tv-dir",
                  tv_dir,
                  "--movie-dir",
                  movie_dir,
                  source], check=True)
  normal_msg("Finished sorting possible media files.")


def normal_msg(msg):
  cprint(msg, 'green', 'on_grey')

def warn_msg(msg):
  cprint('Warning: ' + msg, 'magenta', attrs = ['bold'], file=sys.stderr)

def err_msg(msg):
  cprint('Error: ' + msg, 'red', attrs = ['bold'], file=sys.stderr)

def yellow_msg(msg):
  cprint(msg, 'yellow')

def print_disk_usage():
  total, used, free = shutil.disk_usage("/")
  yellow_msg("Current disk usage are: \n")
  yellow_msg("Total: %d GiB" % (total // (2**30)))
  yellow_msg("Used: %d GiB" % (used // (2**30)))
  yellow_msg("Free: %d GiB" % (free // (2**30)))

