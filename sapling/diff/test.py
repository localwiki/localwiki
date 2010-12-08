'''
Created on Oct 26, 2010

@author: mivanov
'''
from diff_match_patch import diff_match_patch

dmp = diff_match_patch()
dmp.Diff_Timeout = 0.01
dmp.Diff_EditCost = 4

diff = dmp.diff_main('Front Page', 'Awesome Page', False)
print diff
dmp.diff_cleanupSemantic(diff)
print diff