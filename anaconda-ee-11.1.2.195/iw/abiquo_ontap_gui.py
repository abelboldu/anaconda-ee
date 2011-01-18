#
# abiquo_gui.py: Choose tasks for installation
#
# Copyright 2010 Abiquo
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
#

import gtk
import gtk.glade
import gobject
import gui
from iw_gui import *
from rhpl.translate import _, N_
from constants import productName

from netconfig_dialog import NetworkConfigurator
import network

from yuminstall import AnacondaYumRepo
import yum.Errors

import logging
log = logging.getLogger("anaconda")

class AbiquoOntapWindow(InstallWindow):
    def getNext(self):
        self.data.abiquo_rs.ontap_server_ip = \
                self.xml.get_widget('ontap_server_ip').get_text()
        self.data.abiquo_rs.ontap_user = \
                self.xml.get_widget('ontap_user').get_text()
        self.data.abiquo_rs.ontap_password = \
                self.xml.get_widget('ontap_password').get_text()

    def getScreen (self, anaconda):
        self.intf = anaconda.intf
        self.dispatch = anaconda.dispatch
        self.backend = anaconda.backend
        self.anaconda = anaconda
        self.data = anaconda.id

        (self.xml, vbox) = gui.getGladeWidget("abiquo_ontap.glade", "settingsBox")
        self.xml.get_widget('ontap_user').set_text(self.data.abiquo_rs.ontap_user)
        self.xml.get_widget('ontap_password').set_text(self.data.abiquo_rs.ontap_password)
        self.xml.get_widget('ontap_server_ip').set_text(self.data.abiquo_rs.ontap_server_ip)
        return vbox
