REM DESCRIPTION: _setBinPaths.bat adds custom paths to the system PATH (Windows). NOTE: BINPATHS.txt must have a blank line after the last entry, or this batch will fail (and combined two intended defferent lines on the same line in a result). [DESCRIBE MORE WHEN THIS SCRIPT IS DONE.] Reads from BINPATHS.txt and EXTERNALPATHS.txt, which you may populate with custom paths, one per line, no semicolon. Adds the paths in those files to the system PATH variable (Windows), and optionally deletes invalid paths, using the modpath.exe utility.

REM DEPENDENCIES: The modpath.exe tool which I found in the uninstall folder of ImageMagick :) and I don't know where it's from. I presume (perhaps unwisely) that it's free software.

REM LICENSE: I release this work to the Public Domain. 09/24/2015 09:18:03 PM -RAH

ECHO OFF
REM Just in case, that'll be there:
ECHO %PATH% > PATH_backup.txt

REM should end up atting this path: C:\_devtools\bin\gnuCoreUtilsWin32\bin
REM SET PATH=%PATH%;\%CD%\bin\gnuCoreUtilsWin32\bin
REM ECHO %PATH%
REM PAUSE

TYPE BINPATHS.txt > temp.txt
TYPE EXTERNALPATHS.txt >> temp.txt
		REM No workie when attempted add by modpath.exe; see REM comment in that text file:
		REM TYPE win7defaultPATHs.txt >> temp.txt

REM the magic uniqify and sort commands:
%CD%\bin\gnuCoreUtilsWin32\bin\sort.exe temp.txt > temp2.txt
	REM NOTE: I'd had the -u flag on the next line; that messes up my intent (it does not print lines that have duplicates, it only prints unique lines. FACE PALM. ALSO: after I RT_M I learned it only detects *adjacent* duplicate lines. GEH!
%CD%\bin\gnuCoreUtilsWin32\bin\uniq temp2.txt > allPathsTemp.txt
REM ECHO Ready to modify PATH.

FOR /F "delims=*" %%A IN (allPathsTemp.txt) DO (
	REM Optional, if you want this to clean up invalid paths in the list which you may have in your path PATH already ;) :
	REM NOTE: If you don't want this deleting anything in the path, comment out the next two lines!
	REM IF NOT EXIST "%%A" modpath /del %%A
	REM IF NOT EXIST "%%A" ECHO Deleted invalid directory in PATH: %%A >> setPathsLog.txt
IF NOT EXIST %%A ECHO Could not find path: %%A >> setPathsLog.txt
IF EXIST %%A ECHO Found path: %%A >> setPathsLog.txt
REM NOTE: without the quote marks on the next line, it won't add directories that include spaces ( ). It will work if the first %%A doesn't have quote marks (and will mess up sorting if they do, it seems--odd).
IF EXIST %%A %CD%\bin\modpath /add "%%A"
IF EXIST %%A ECHO Added directory to PATH: "%%A"
)

DEL temp.txt
DEL temp2.txt
DEL allPathsTemp.txt

REM ===========
REM NOT IMPLEMENTED, if ever it will be; would be in the for loop:

REM DEVELOPMENT HISTORY:
REM 2015 09 25? -- First version?
REM 2015-11-12 Bug fix to include necessary paths on run (had assumed so many .exes were in the same path.
REM 2015-12-20 Add bug comment to comments at start of file