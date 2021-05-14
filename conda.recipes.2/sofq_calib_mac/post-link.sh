#!/bin/bash

anaconda_python=$(conda info | grep "active env location" | cut -d":" -f2 | tr -d ' ')

echo "#!/bin/bash" > ${PREFIX}/bin/sofq_calib
echo 'echo "import wx" > /tmp/main.py' >> ${PREFIX}/bin/sofq_calib
echo 'echo "from sofq_calib import sofq_calib" >> /tmp/main.py' >> ${PREFIX}/bin/sofq_calib
echo 'echo "if __name__ == \"__main__\":" >> /tmp/main.py' >> ${PREFIX}/bin/sofq_calib
echo 'echo "    app = wx.App()" >> /tmp/main.py' >> ${PREFIX}/bin/sofq_calib
echo 'echo "    fr = sofq_calib.MainFrame(wx.Frame)" >> /tmp/main.py' >> ${PREFIX}/bin/sofq_calib
echo 'echo "    fr.Show()" >> /tmp/main.py' >> ${PREFIX}/bin/sofq_calib
echo 'echo "    app.MainLoop()" >> /tmp/main.py' >> ${PREFIX}/bin/sofq_calib
echo "${anaconda_python}/bin/pythonw /tmp/main.py" >> ${PREFIX}/bin/sofq_calib
echo "rm -rf /tmp/main.py" >> ${PREFIX}/bin/sofq_calib

chmod a+x ${PREFIX}/bin/sofq_calib
