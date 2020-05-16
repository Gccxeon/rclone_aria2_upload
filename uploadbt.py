#!/usr/bin/python3

import common_tools
import configparser
import os
import sys
import time


pwd = os.getcwd()

# Configure area:
conf = configparser.ConfigParser()
with open(pwd + '/config') as f:
  conf.read_file(f)
  uploader = conf.get('Path', 'rclone_path')
  uploaded_log = conf.get('Path', 'uploaded_log_file')
  file_root = conf.get('Path', 'aria2_download_path')

  remote_dest = conf.get("Remote", "remote_dest")
  remote_name = conf.get("Remote", "remote_name")
  file_des = remote_name + ":" + remote_dest


  rclone_mount = conf.get("Media_Sort", "remote_mount_loc")
  tv_dir_r = conf.get("Media_Sort", "tv_dir")
  tv_dir = os.path.join(rclone_mount, tv_dir_r)
  movie_dir_r  = conf.get("Media_Sort", "movie_dir")
  movie_dir = os.path.join(rclone_mount, movie_dir_r)
  accuracy = conf.get("Media_Sort", "accuracy")

  remote_source = os.path.join(rclone_mount, remote_dest)


# Get args from aria2
args = list(sys.argv)
_, pid, filenum, file_path = args

if filenum == 0:
  # Then there is nothing to do
  exit(0)

file_path = str(file_path)

# Check if path is valid
if not os.path.exists(file_path):
  common_tools.err_msg("The path of downloaded file ({}) "
                       "doesn't exist".format(file_path))
  exit(0)

torrent_name = common_tools.get_torrent_name(file_root, file_path)
file_des = file_des + '/' + torrent_name

while file_des[-1] == "/":
  file_des = file_des[:-1]

common_tools.normal_msg("Preparing to upload " + file_path)


with open(uploaded_log, "r") as f:
  uploaded = f.readlines()

with open(uploaded_log, "w") as f:
  stop_flag = False
  for line in uploaded:
    if line.strip('\n') == file_path.strip('\n'):
      stop_flag = True
      common_tools.yellow_msg("{} has been uploaded already.\n".format(file_path))
      common_tools.warn_msg("By default, now it will be deleted from your "
                            "hard disk!\n")
      common_tools.only_direct_delete(file_root, file_path)
      common_tools.print_disk_usage()

    elif line.strip().strip('\n'):
      f.write(line)
    f.truncate()


# Begin upload process
if not stop_flag:
  # Usually BT files are contained inside a folder instead of a file directly.
  # So if this happens, event can then be treated as a normal http download
  if common_tools.file_check(file_path) == "is_file":
    common_tools.upload(uploader, file_path, file_des, delete=True)

  # An standard rclone example
  else:
    common_tools.upload(uploader, file_path, file_des)
    common_tools.add_seedings(uploaded_log, file_root, file_path)

  common_tools.print_disk_usage()

  # Perform a media sort (Optional)
  if os.path.exists(remote_source):
    common_tools.normal_msg("Starting media sorting task.")
    time.sleep(30)
    sort_source = os.path.join(remote_source, torrent_name)
    sorter = pwd + "/media-sort"
    common_tools.media_sort(sorter, sort_source, accuracy, tv_dir, movie_dir)
