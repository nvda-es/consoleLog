@cls
@echo off
scons --clean
scons pot
git init
git add --all
git commit -m "Preparación  versión 1.4 y NVDA 2025.1 Lanzamiento"
git push -u origin master
git tag 1.4
git push --tags
pause