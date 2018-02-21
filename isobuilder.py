"""The module has functions to build ISO's"""
from subprocess import call
from paths import ISO_BASE, ISO_ESXI, ISO_KVM

class iso_builder(object):
    """Class with functions to build ISO for esxi and kvm"""

    def iso_builder_esxi(self):
        """function to build iso"""
        call({"mkisofs", "-J", "-R", "-v", "-V", "bootstrap", "-A", "bootstrap", "-ldots", "-l", "-allow-lowercase", "-allow-multidot", "-o", ISO_BASE, ISO_ESXI })

    def iso_builder_kvm(self):
        """function to build iso"""
        call(["mkisofs", "-J", "-R", "-v", "-V", "bootstrap", "-A", "bootstrap", "-ldots", "-l", "-allow-lowercase", "-allow-multidot", "-o", ISO_BASE, ISO_KVM ])
