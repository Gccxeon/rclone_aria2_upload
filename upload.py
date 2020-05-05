import sys
import shutil
import subprocess
import os

# Configure area:
#uploadcmd = "bash /home/up2one"
uploader = "/usr/bin/rclone"
uploaded_log = "./uploaded"
file_des = "pdrive:/tmp/"
file_root = "/home/dap/Projects/Scripts/rclone_uploader/test"

# other utils
def file_check(file_path):
  if os.path.isfile(file_path):
    return "is_file"
  elif os.path.isdir(file_path):
    return "is_dir"
  else:
    raise ValueError("Invalid file path! Please check your input.")

def seedings(uploaded_log, stop_flag):
  with open(uploaded_log, "r") as f:
    remainings = f.readlines()

  subprocess.call(["echo",
                   "remaining seeding BT task includes: "])

  for fname in remainings:
    if fname:
      subprocess.call(["echo", fname])


args = list(sys.argv)
_, pid, filenum, file_path = args
if not os.path.exists(file_path):
  file_path = os.path.join(file_root, file_path)
if not os.path.exists(file_path):
  subprocess.call(["echo",
                   "The given path of file ({}) "
                   "doesn't exist".format(file_path)])
subprocess.call(["echo", "Preparing to upload " + file_path])


filable = file_check(file_path)
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

      if filable == "is_file":
        os.remove(file_path)
      else:
        shutil.rmtree(file_path)
    else:
      f.write(line)

# begin upload subprocess

if not stop_flag:
  # An standard rclone example
  if filable == "is_file":
    subprocess.run([uploader,
                    "--ignore-existing",
                    "copy",
                    file_path,
                    file_des])
    os.remove(file_path)
  else:
    subprocess.run([uploader,
                    "--ignore-existing",
                    "copy",
                    file_path,
                    file_des + os.path.basename(file_path)])
    shutil.rmtree(file_path)

seedings(uploaded_log, stop_flag)
