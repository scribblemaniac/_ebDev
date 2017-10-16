# DESCRIPTION
This repository was previously entitled _devtools.

A collection of scripts (most of them developed by me) which I use for development of many kinds--at this writing, mostly visual art development on Windows. It heavily relies on various 'nix/cygwin utilities, which at this writing you can obtain via a URL provided later in this document.

I believe that everything not created by me in this archive is at least freely available and open source. If you are the copyright owner of anything in this archive and wish for it to be removed, please contact me and I will do so.

[http://earthbound.io/contact](http://earthbound.io/contact "http://earthbound.io/contact")

09/02/2015 07:29:00 PM -RAH

# INSTALLATION AND USAGE

## _ebSuperBin dependencies

From a cygwin (or adapt for another 'nixy environment on Windows, or for similar utilities on a Mac) run the following commands. For my preferences on Windows, right from your windows drive root via the Cygwin terminal:

apt-cyg install p7zip
wget http://earthbound.io/dist/_ebSuperBin.7z
p7zip -d ./_ebSuperBin.7z

--which will extract that in a folder (per the archive) ./_ebSuperBin

OR instead of wget use curl:
apt-cyg install curl
curl http://earthbound.io/dist/_ebSuperBin.7z

Clone ane make use of _setBinBaths.bat from https://github.com/earthbound19/_ebPathMan, which will permanently modify your path to include all relevant paths in this archive. OR examine and use getDevEnv.sh per the comments therein.

The tools and scripts in this repository are subject to high flux, because I edit and develop them as I use them, and/or because I freely add or remove utilities from this archive.

## TO DO
- Move this TO DO list to project tracker at gitHub.
- Update all scripts that could use it to exploit the method of reading from $HOME/_devToolsPath.txt used in randomVerticalColorStripes.sh
- Update getDevEnv.sh to use the same mechanism

## ARCHIVE HISTORY
- 03/13/2016 04:20:39 PM Dramatically expanded/reorganized to include a lot more that I'm using, and have developed and/or moved. -RAH
- 09/02/2015 08:42:48 PM This was initially a project of only font development scripts. I upgraded it to be a repository of executables and scripts I use (and wrote). -RAH
