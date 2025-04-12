@cls
@echo off
scons --clean
scons pot
git init
git add --all
git commit -m "v1.4 add TR lan"
git push -u origin master
#git tag 1.4
#git push --tags
pause