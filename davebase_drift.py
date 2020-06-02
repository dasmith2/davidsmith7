"""
davebase is a foundation. But in order to test a foundation, you actually have
to build something on it. So as I'm building daveSPACE, I of course have to
make lots of changes to foundation files. It's much easier to just modify
foundation files right in daveSPACE as opposed to the more technically correct
but painful

cd davebase
# Make my changes
git commit -a -m .
git push
cd davespace
git commit -a -m .
git pull upstream master

So I created this tool to handle the situation. It sees which files are in
davebase, then looks at the files in davespace to see if there are any
differences. If there are, it offers to copy the contents of whichever file was
modified more recently to the other file. """
import os
import re
from shutil import copyfile


def fix_drift(davebase_root_dir, derived_root_dir):
  for (davebase_dir, d, davebase_files) in os.walk(davebase_root_dir):
    if re.compile(r'__pycache__|\.venv|\.git').findall(davebase_dir):
      continue
    for file_name in davebase_files:
      davebase_full_path = '{}/{}'.format(davebase_dir, file_name)
      filename, file_extension = os.path.splitext(davebase_full_path)
      if file_extension in ['.pyc', '.swp']:
        continue
      derived_full_path = davebase_full_path.replace(
          davebase_root_dir, derived_root_dir)
      if not os.path.exists(derived_full_path):
        prompt = '{} is missing. What should I do? (c)opy or (s)kip: '.format(
            derived_full_path)
        if get_input(prompt, ['c', 's']) == 'c':
          copyfile(davebase_full_path, derived_full_path)
      elif file_extension in ['.jpg', '.png']:
        continue
      elif file_name.find('this_site_') == 0 or file_name.find('local_') == 0:
        # As you can see, the convention is that davebase may declare
        # this_site_<whatever>.<whatever> as a placeholder to be overwritten by
        # the child sites. These files are explicitly meant to be modified and
        # shouldn't be considered drift.
        continue
      davebase_content = get_content(davebase_full_path)
      davebase_modified = os.path.getmtime(davebase_full_path)
      derived_content = get_content(derived_full_path)
      derived_modified = os.path.getmtime(derived_full_path)
      if davebase_content != derived_content:
        # Usually the case
        most_recent_path = derived_full_path
        most_recent_content = derived_content
        less_recent_path = davebase_full_path
        less_recent_content = davebase_content
        if davebase_modified > derived_modified:
          # But not always
          most_recent_path = davebase_full_path
          most_recent_content = davebase_content
          less_recent_path = derived_full_path
          less_recent_content = derived_content
        print('{} was modified more recently'.format(most_recent_path))
        print('diff -Naur {} {}'.format(less_recent_path, most_recent_path))
        while True:
          prompt = (
              'Should I replace {} with {}? (y)es (n)o (p)rint them: ').format(
                  less_recent_path, most_recent_path)
          got = get_input(prompt, ['y', 'n', 'p'])
          if got == 'y':
            write_content(less_recent_path, most_recent_content)
            print('')
            break
          elif got == 'p':
            print('\n{}\n'.format(less_recent_path))
            print(less_recent_content)
            print('==========================\n{}\n'.format(most_recent_path))
            print(most_recent_content)


def get_input(prompt, options):
  got = None
  while got not in options:
    got = input(prompt)
    if got in options:
      return got
    else:
      print('\n{} is not valid option.\n'.format(got))


def get_content(path):
  return open(path, 'r').read()


def write_content(path, content):
  open(path, 'w').write(content)


if __name__ == '__main__':
  parent_dir = os.getcwd().split('/')[-1]
  if parent_dir == 'davebase':
    print('Run davebase_drift.py from the derived project, not from davebase')
  else:
    fix_drift('../davebase', '.')
