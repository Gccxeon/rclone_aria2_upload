import sys
import subprocess
import os
import shutil
import common_tools

# Configure area:
uploader = "/usr/bin/rclone"
uploaded_log = "/root/rclone_aria2_upload/uploaded"
#uploaded_log = "./uploaded"
#file_root = "/home/dap/Projects/Scripts/rclone_uploader"
file_root = "/home/download"
file_des = "pdrive:/tmp/"


args = list(sys.argv)
_, pid, filenum, file_path = args
file_path = str(file_path)
# Preprocessing the loading path
file_path = os.path.abspath(file_path)
file_path = os.path.join(file_root, file_path)
file_root, ch_file_path = common_tools.split_folder(file_root, file_path)

# Check if processed path is still valid
if not os.path.exists(file_path):
  file_path = os.path.join(file_root, file_path)
if not os.path.exists(file_path):
  subprocess.call(["echo",
                   "The given path of file ({}) "
                   "doesn't exist".format(file_path)])
  exit(0)
torrent_name = common_tools.get_torrent_name(file_root, file_path)
file_path = os.path.join(file_root, torrent_name)
file_des += torrent_name
while file_des[-1] == "/":
  file_des = file_des[:-1]

subprocess.run(["echo", "Preparing to upload " + file_path])


with open(uploaded_log, "r") as f:
  uploaded = f.readlines()
with open(uploaded_log, "w") as f:
  stop_flag = False
  for line in uploaded:
    if line.strip('\n') == file_path.strip('\n'):
      stop_flag = True
      subprocess.call(["echo", 'The file has been uploaded already'])
      subprocess.call(["echo",
                       "By default, now {} will be deleted".format(file_path)])

      # There is a potential bug when doing this:
      # If a parent file_path gets here later on while the sub-files haven't
      # finish the upload, the whole parent folder will be dedeleted and the
      # unfinished sub files won't possiblely get uploaded.
      common_tools.only_direct_delete(file_root, file_path)
    elif line.strip().strip('\n'):
      f.write(line)
# Begin upload process
if not stop_flag:
  # Usually bt task are contained inside a folder instead of directly under
  # root folder. If this happens, event can then be seen as a normal http
  # download
  if common_tools.file_check(file_path) == "is_file":
    common_tools.upload(uploader, file_path, file_des, delete=True)

  # An standard rclone example
  else:
    common_tools.upload(uploader, file_path, file_des)
    common_tools.add_seedings(uploaded_log, file_root, file_path)
