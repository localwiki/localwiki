import os, sys

root = sys.argv[1]

print 'Putting dummy comment in all blank __init__.py files ...'
for path, dirs, files in os.walk(root):
  inits = [os.path.join(path, f) for f in files if f == '__init__.py']
  blank_inits = [f for f in inits if not os.path.getsize(f)]
  for i in blank_inits:
    f = open(i, 'w')
    f.write('# For debhelper brokenness, making this file non-blank\n')
    f.close()
      
