#!/usr/bin/python
# -*- coding: utf-8 -*-

# Licensed under the GPL v3
# Written by arand
# Cleaned up by Mike Ivanov
# Matplotlib implementation by Paul Ivanov
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

    launchpad = Launchpad.login_anonymously('ppastats', 'production',
            cachedir, version='devel')
    owner = launchpad.people[owner_name]
    archive = owner.getPPAByName(name=ppa)
    getPB = archive.getPublishedBinaries

    for arch in archs:
        for release in releases:
            base = "https://api.launchpad.net/devel/ubuntu/"
            url = base + release + "/" + arch

            binaries = getPB(status='Published', distro_arch_series=url)
            for binary in binaries:
                totals = binary.getDailyDownloadTotals()
                for date, downloads in totals.items():
                    if date not in stats:
                        stats[date] = dict([(r, 0) for r in releases])
                    stats[date][release] = downloads

try:
    import numpy as np
    import matplotlib
    # prevent interactive pop-up
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.dates import datestr2num

    dates = datestr2num(stats)
    # 2d array to store totals by release and by date
    all = np.array([[stats[x][r] for x in stats] for r in releases])

    a=1. # alpha
    kwargs = dict(linewidth=0,color='g', alpha=a, align='center')
    ax = plt.subplot(1,1,1)
    ax.xaxis_date()
    for i,r in enumerate(releases):
        if i==0:
            prev = all.sum(0)
        prev=prev-all[i]
        kwargs.update(alpha=a,label=r,bottom=prev)
        ax.bar(dates, all[i],**kwargs)
        a*=.66
    plt.gcf().autofmt_xdate()
    l = plt.legend()
    l.set_frame_on(False)
    ax.set_ylabel("Downloads")
    # Liberate axis!
    ax.yaxis.tick_left()
    ax.xaxis.tick_bottom()
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.draw()
    plt.savefig("_".join([owner_name, ppa, 'downloads.png']))

    print "Totals by date:"
    for d,t in zip(stats,all.sum(0))[::-1]:
        print "%4d :"%t,d
    print "Totals by release:"
    for r,t in zip(releases,all.sum(1)):
        print '%4d :'%t,r
    print "Total downloads: ", all.sum()
except ImportError:
    # Couldn't import matplotlib, let's do the old thing
    for date, downloads in reversed(stats.items()):
        print date, downloads
