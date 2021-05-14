Currently, we rely on the post link (and pre unlink) scripts for packaging up.
The idea is to create a bash script in the anaconda bin directory. The anaconda
main directory is specified by the environment variable 'PREFIX' in the
'post-link.sh' script. Suppose conda is activated and therefore the system can
find the created bash script, it can then be launched from the command line
anywhere. Alternatively, we can provide the bash script to users so they can put
it anywhere the system can find (e.g. with sudo privilege, the script can be put
under '/usr/bin/' directory). Within the bash script, we prepare a temporary
'main.py' file under '/tmp' directory, which will kick off the main GUI through
importing the module 'sofq_calib' that is installed with conda. After the GUI is
closed, the temporary 'main.py' file will be deleted.

The 'pre-unlink.sh' is responsible for deleting the 'sofq_calib' bash script
when removing the conda package 'sofq_calib'.

!!!!!!!!!
ATTENTION
!!!!!!!!!
If in the future, policies concerning the using of post-link and pre-unlink
script is changed, problems may happen during both conda building on our end or
installation and program execution on users' end. In that case, we need to
specifically figure out what needs to be done.

==============================
Yuanpeng Zhang @ Sun 29-Sep-19
==============================
