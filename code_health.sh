set -e

# You can make sure code you're working on doesn't get submitted by accident by
# putting the literal string DO NOT SUBMIT anywhere.
echo "Testing for DO NOT SUBMIT."
echo "If this fails with 'No such file' or something, thats what it is."
# -r recursive, -I ignore binary files, -i ignore case, -n show the line
# number. I found the directory names by just runnin ls -a -l in this here
# script one time. bash is a mystery to me. This was the only way I figured out
# how to fail when grep found a thing.
$(! grep -r -I -i -n --exclude-dir=migrations --exclude-dir=.heroku --exclude-dir=.sprettur --exclude-dir=.profile.d --exclude-dir=.git --exclude-dir=.venv --exclude=test.sh --exclude=code_health.sh --exclude=README.md 'DO NOT SUBMIT\|import pdb')

echo "./lint.sh"
./lint.sh
echo "djaveCodeHealth/are_widgets_tested.py"
python djaveCodeHealth/are_widgets_tested.py
./manage.py test
./manage.py web_test test
echo "./manage.py raise_if_errors_or_problems"
./manage.py raise_if_errors_or_problems
