#!/usr/bin/python
# -*- coding: utf-8 -*-

# Licensed under the GPL v3
# Written by arand
# Inspired by Alex Mandel's script snippets at https://bugs.launchpad.net/launchpad/+bug/139855
# This is my biggest project in python to date, it is KLUDGE beyond imagination.
# On Debian-like systems the package python-launchpadlib is required

import sys
import os
from launchpadlib.launchpad import Launchpad

archs = ["i386"]
releases = ["lucid", "maverick", "natty", "oneiric"]

if len(sys.argv) < 3:
    print "Usage: ppastats owner ppaname1 [ppaname2 ...]"
    sys.exit(1)

owner_name = sys.argv[1]
ppas = sys.argv[2:]

stats = {}

for ppa in ppas:
	cachedir = os.path.expanduser("~/.launchpadlib/cache/")

	launchpad = Launchpad.login_anonymously('ppastats', 'production', cachedir, version='devel')
	owner = launchpad.people[owner_name]
	archive = owner.getPPAByName(name=ppa)

	for arch in archs:
		for release in releases:
			distro_arch_series = "https://api.launchpad.net/devel/ubuntu/" + release + "/" + arch

			for binary in archive.getPublishedBinaries(status='Published', distro_arch_series=distro_arch_series):
				totals = binary.getDailyDownloadTotals()
				for date, downloads in totals.items():
					if date not in stats:
						stats[date] = dict([(r, 0) for r in releases])
					stats[date][release] = downloads
