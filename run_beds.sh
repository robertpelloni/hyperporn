cd ~/workspace/hyperporn
PYTHONIOENCODING=utf-8 python rebuild_nohyp.py beds > beds_build.log 2>&1
echo "EXIT=$?" >> beds_build.log
