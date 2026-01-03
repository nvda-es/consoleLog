@cls
@echo off
scons --clean
scons pot
git init
git add --all
git commit -m "2026.01.03"
git push -u origin master
#git tag 1.4
#git push --tags
pause