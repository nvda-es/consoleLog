@echo off
chcp 65001 >nul
setlocal EnableExtensions

REM ============================================================
REM NVDA Add-on Tools (V2) - más robusto contra "No se esperaba X..."
REM - Subir cambios (add/commit/push)
REM - Build del add-on (scons)
REM - Tag + push + release (gh) y adjuntar asset si existe
REM ============================================================

echo ============================================================
echo   NVDA Add-on Tools - Git + Release + Build (SCons)
echo ============================================================

REM --- Comprobar que estamos dentro de un repo git
git rev-parse --is-inside-work-tree >nul 2>&1
if errorlevel 1 goto :ERR_NOT_GIT

REM --- Comprobar que git existe
where git >nul 2>&1
if errorlevel 1 goto :ERR_NO_GIT

:MENU
echo.
echo ===================== MENÚ =====================
echo  1) Subir cambios (git add + commit + push)
echo  2) Generar complemento (scons)
echo  3) Crear tag + crear release y publicarla (git + gh)
echo  4) Salir
echo =================================================
choice /c 1234 /n /m "Elige una opción (1-4): "
if errorlevel 4 goto :END
if errorlevel 3 goto :TAG_RELEASE
if errorlevel 2 goto :BUILD
if errorlevel 1 goto :PUSH
goto :MENU


:PUSH
echo.
echo ===================== SUBIR CAMBIOS =====================
git status

set "MSG="
set /p MSG="Mensaje de commit (obligatorio): "
if "%MSG%"=="" goto :ERR_EMPTY_COMMIT

git add -A
if errorlevel 1 goto :ERR_GIT_ADD

git diff --cached --quiet
if not errorlevel 1 goto :ERR_NO_STAGED

git commit -m "%MSG%"
if errorlevel 1 goto :ERR_GIT_COMMIT

for /f "usebackq delims=" %%B in (`git rev-parse --abbrev-ref HEAD 2^>nul`) do set "BRANCH=%%B"
if "%BRANCH%"=="" set "BRANCH=master"

echo Haciendo push de la rama "%BRANCH%"...
git push -u origin "%BRANCH%"
if errorlevel 1 goto :ERR_GIT_PUSH

echo [OK] Cambios subidos correctamente.
goto :MENU


:BUILD
echo.
echo ===================== GENERAR COMPLEMENTO =====================

call :ENSURE_SCONS
if errorlevel 1 goto :MENU

echo Ejecutando scons...
scons
if errorlevel 1 goto :ERR_SCONS

call :FIND_LATEST_ADDON
if errorlevel 1 (
	echo [WARN] scons terminó, pero no encontré ningún *.nvda-addon en la carpeta actual.
	goto :MENU
)

echo [OK] Complemento generado: "%LATEST_ADDON%"
goto :MENU


:TAG_RELEASE
echo.
echo ===================== TAG + RELEASE =====================

set "TAG="
set /p TAG="Introduce el tag (ej: v1.0.0): "
if "%TAG%"=="" goto :ERR_EMPTY_TAG

git tag -a "%TAG%" -m "%TAG%"
if errorlevel 1 goto :ERR_TAG_CREATE

git push origin "%TAG%"
if errorlevel 1 goto :ERR_TAG_PUSH

where gh >nul 2>&1
if errorlevel 1 (
	echo [OK] Tag creado y enviado.
	echo      No encuentro "gh" (GitHub CLI), así que no puedo crear la release desde aquí.
	echo      Si tu repo tiene workflow de release por tag, GitHub Actions puede encargarse.
	goto :MENU
)

gh auth status >nul 2>&1
if errorlevel 1 goto :ERR_GH_AUTH

REM Intentar build para adjuntar asset (si se puede)
call :ENSURE_SCONS
if errorlevel 1 goto :RELEASE_NO_ASSET

scons
if errorlevel 1 goto :RELEASE_NO_ASSET

call :FIND_LATEST_ADDON
if errorlevel 1 goto :RELEASE_NO_ASSET

echo Creando release y subiendo asset...
gh release create "%TAG%" "%LATEST_ADDON%" --title "%TAG%" --generate-notes
if errorlevel 1 goto :ERR_GH_RELEASE

echo [OK] Release creada y publicada con asset.
goto :MENU


:RELEASE_NO_ASSET
echo Creando release (sin asset)...
gh release create "%TAG%" --title "%TAG%" --generate-notes
if errorlevel 1 goto :ERR_GH_RELEASE

echo [OK] Release creada y publicada (sin asset).
goto :MENU


REM ============================================================
REM Subrutinas
REM ============================================================

:ENSURE_SCONS
where scons >nul 2>&1
if not errorlevel 1 exit /b 0

echo [INFO] "scons" no está en PATH. Intentando instalar con pip (usuario)...
where py >nul 2>&1
if errorlevel 1 exit /b 1

py -m pip install --user scons markdown >nul 2>&1
if errorlevel 1 exit /b 1

where scons >nul 2>&1
if errorlevel 1 exit /b 1

exit /b 0


:FIND_LATEST_ADDON
set "LATEST_ADDON="
for /f "usebackq delims=" %%F in (`dir /b /a:-d /o:-d "*.nvda-addon" 2^>nul`) do (
	set "LATEST_ADDON=%%F"
	goto :FOUND_ADDON
)
exit /b 1

:FOUND_ADDON
exit /b 0


REM ============================================================
REM Errores
REM ============================================================

:ERR_NOT_GIT
echo [ERROR] Esto no parece un repositorio git (no estoy dentro de un work-tree).
goto :END

:ERR_NO_GIT
echo [ERROR] No encuentro "git" en PATH. Instala Git y abre una consola nueva.
goto :END

:ERR_EMPTY_COMMIT
echo [ERROR] El mensaje de commit no puede estar vacío.
goto :MENU

:ERR_GIT_ADD
echo [ERROR] Falló "git add -A".
goto :MENU

:ERR_NO_STAGED
echo [ERROR] No hay cambios en staging para commitear.
goto :MENU

:ERR_GIT_COMMIT
echo [ERROR] Falló "git commit".
goto :MENU

:ERR_GIT_PUSH
echo [ERROR] Falló "git push".
goto :MENU

:ERR_SCONS
echo [ERROR] Falló "scons".
goto :MENU

:ERR_EMPTY_TAG
echo [ERROR] El tag no puede estar vacío.
goto :MENU

:ERR_TAG_CREATE
echo [ERROR] No se pudo crear el tag (¿ya existe?).
goto :MENU

:ERR_TAG_PUSH
echo [ERROR] No se pudo enviar el tag a origin.
goto :MENU

:ERR_GH_AUTH
echo [ERROR] "gh" no está autenticado. Ejecuta: gh auth login
goto :MENU

:ERR_GH_RELEASE
echo [ERROR] Falló la creación de la release con gh.
goto :MENU


:END
echo.
echo [FIN]
endlocal
exit /b 0
