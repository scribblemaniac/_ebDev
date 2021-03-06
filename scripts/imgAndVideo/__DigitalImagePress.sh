# USAGE: comment out steps unecessary for your current run of the image press (this script). Then run the script. Also NOTE comments in ALL CAPS in this script.

# FIRST, USE; PREFERRED: http://sourceforge.net/projects/file-folder-ren/?source=typ_redirect with MetamorphoseBadFileNameCharacterRemoval.cfg (and adjust the search/select folder as necessary), to remove unwanted characters from file names. NOTE: When it asks about creating a t_e_m_p folder, you may answer no (it only creates a folder maintaining the folder structure of the renamed files, which you may paste back into the root operating folder. Depending on circumstance, you may want to do that).
		# Deprecated (formerly preferred):
						# cleanup_bad_fileNames__RenameFiles2.3b.exe (*without* using the white spaces option) and file_renamer_install_flex73.exe respectively to remove all special characters and replace all spaces with underscores. NOTE: it freaks out unless you put a \ at the end of the path to scan. THEN, use fixIMGnames.sh, which fails on some or perhaps too many special characters repair :/ but that is mitigated by using the first mentioned tools. FAIL for that, but in development: cleanupGarbageFileNames.sh
				# THE ABOVE accomplished with the next two lines:
				# renameFiles.exe
				# fixIMGnames.sh

# NOTE: metamorphose2 is not used because of a strange bug listing files to be renamed (it shows an entirely wrong target file name which is from anoter file name in the tree).

# TO DO: Revise this to describe how metamorphose is needed for folder renames and ftun.sh for this (I think--test that?)--and to also call ftun.sh
# TO DO: update documentation in comments and have it refer to an outside file (move relevant comments from here to said file).
# TO DO: Move the relevant instructions from bunnieselow, or all of them, into echo statements in the files to which they relate, for cases of using those files independent of this script.
# TO DO? : split this into two scripts (one for file name and metadata fixup, another for custom metadata creation), and update documentation referencing the (to be former) file name of this script accordingly.

echo "!============================================================"
	echo "WARNING: Before using this script, ensure all file names in your execution path do not have any console-unfriendly characters in their file names, including no spaces (replace those with underscores). OTHERWISE, this script will not work as hoped. This script will first attempt to run metamorphose (see https://sourceforge.net/projects/file-folder-ren/files/Metamorphose/1.1.2%20stable/ ). Load the Metamorphose1BadFileNameCharacterRemoval_step01.cfg configuration into metamorphose, adjust the search folder as necessary, and execute it. Then reload the file list, and repeat this with ~02.cfg, and any others after that. ALTERNATE option for this: manually use the Flexible Renamer program, operating only on folders, with the regex in badCharsFRregex.txt, replacing with _. ALSO, to include all files in subdirectories, look for a \"walk\" checkbox and tick it. If metamorphose fails to open from this script, you will have a chance to abort this script. NOTE: if metamorphose gives you a permissions or other access error, it may be that a path name is too long. Shorten it up or temporarily move a long folder name to a root dir, then run this script against that temporarily moved folder. ALSO NOTE: you might additionally or alternately try ftun.sh."
	echo "Do you wish to run this script?"
	echo "!============================================================"
# TO DO:
# Update this (non-working anyway for whatever reason--it *did* work before) prompt with that to be found at: http://stackoverflow.com/a/3232082/1397555
	echo "IF YOU HAVE READ the above warning, type the number corresponding to your answer, then press <enter>. If you haven't read the warning, your answer is 2 (No)."
	select yn in "Yes" "No"
	do
		case $yn in
			Yes ) echo Dokee-okee! Working . . .; break;
			No ) echo D\'oh!; exit;
		esac
	done
cmd /c "C:\Program Files (x86)\metamorphose\metamorphose.exe"
	echo "!============================================================"
	echo "Run of metamorphose.exe attempted. Do you wish to continue running this script?"
	echo "!============================================================"
	echo "TYPE THE NUMBER CORRESPONDING TO YOUR ANSWER, then press <enter>. If you are not sure, your answer is 2 (No)."
	select yn in "Yes" "No"
	do
		case $yn in
			Yes ) echo Dokee-okee! Working . . .; break;
			No ) echo D\'oh!; exit;
		esac
	done

# COMMENT OUT OR USE PER NEED:
# dateByFileName.sh
# dateByMetaData.sh
numberFilesByLabel.sh

echo "As instructed by the echo from the end of numberFilesByLabel.sh, examine the files created by that batch, and if you are ready to continue, select 1. If you are not ready, make adjustments and manually run said ~.sh script until you are ready, then select 1, or select 2 to terminate this script, and examine the source to determine what to do next."
	echo "!============================================================"
	echo "DO YOU WISH TO CONTINUE running this script?"
	select yn in "Yes" "No"
	do
		case $yn in
			Yes ) echo Dokee-okee! Working . . .; break;
			No ) echo D\'oh!; exit;
		esac
	done

archiveMetadata.sh
imgMetaDataTo7z.bat
prepMediaMetadata.sh
mediaTagAndDist.sh

echo __DigitalImagePress.sh run COMPLETED.