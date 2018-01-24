import os
from subprocess import call



call(["mkisofs", "-J", "-R", "-v", "-V", "'bootstrap'", "-A", "'bootstrap'", "-ldots", "-l", "-allow-lowercase", "-allow-multidot", "-o", "/home/ubuntu/automic/static/KVM/bootstrap-archive-kvm.iso", "./static/KVM/bootstrap"])
