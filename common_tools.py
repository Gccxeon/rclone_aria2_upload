import sys
import subprocess
import os
import shutil

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
    pass

  ch_part = ch.replace(pa, "")
  while ch_part[0] == '/':
    ch_part = ch_part[1:]
  while pa[-1] == "/":
    pa = pa[:-1]
  return pa, ch_part

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

  subprocess.run(["echo",
                   "remaining seeding BT task includes: "])

  for fname in remainings:
    if fname:
      subprocess.run(["echo", fname])


def upload(rclone, source, dest, delete=False):
  filetype = file_check(source)
  if filetype == "is_file":
    dest = dest.replace(os.path.basename(source), "")
  if delete:
    fcmd = "move"
  else:
    fcmd = "copy"
  subprocess.run([rclone,
                  "--ignore-existing",
                  fcmd,
                  source,
                  dest])

def get_abs_subpath(parent):
  parent = os.path.abspath(parent)
  children = os.listdir(parent)
  for i, child in enumerate(children):
    children[i] = os.path.join(parent, child)
  return children

# Only delete the child if the child is drectly under the parent folder
def only_direct_delete(parent, child):
  parent = os.path.abspath(parent)
  child = os.path.abspath(child)
  _, diff = split_folder(parent, child)
  if num_folders(diff) == 1:
    print(f"Warning: deleted {child}.")
    if file_check(child) == "is_file":
      os.remove(child)
    else:
      shutil.rmtree(child)

def num_folders(dir_path):
  while dir_path[0] == "/":
    dir_path = dir_path[1:]
  while dir_path[-1] == "/":
    dir_path = dir_path[:-1]
  if dir_path:
    return len(dir_path.split("/"))
  else:
    return 0
