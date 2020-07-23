set -e

echo "./lint.sh"
./lint.sh
echo "djaveCodeHealth/are_widgets_tested.py"
python djaveCodeHealth/are_widgets_tested.py
./manage.py test
./manage.py web_test test
