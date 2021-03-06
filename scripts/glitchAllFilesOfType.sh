# DESCRIPTION
# Invokes a script that corrupts all files of a given extension in the directory from which this script is invoked, producing N glitched image file variants for each file, output to a /_glitched folder. See USAGE for options. Written specifically for the purpose of deliberately making glitch art out of e.g. .jpg files, but it may produce "good" results for a variety of file formats. OR, with some code change, invokes BM.exe (Byte Molester, a free tool).

# USAGE
# Pass this script four parameters, being:
# $1 a file extension (without the .) for file types in the current directory which you want to produce glitched variants of
# $2 the number of glitched images per image you wish to make.
# $3 what percent of each file to corrupt (1 to 100)

# The following command, for example, will make 10 corrupted copies of every jpg in the current path, corrupting each copy by 2 percent:
# thisScript.sh jpg 10 2

gfind \*.$1 > _alles.txt
# I WASTED A CURSEDLY LARGE PORTION OF MY BREATH AND TOIL before figuring out I need to do the following:
dos2unix _alles.txt
# strip off ./ at start as it messes up later glitchThisFile.sh call:
sed -i 's/\.\/\(.*\)/\1/g' _alles.txt

if [ ! -d _glitched ]; then mkdir _glitched; fi

while read element
do
			echo corrupting file $element . . .
	cp "$element" ./_glitched/
	# Corrupt the file $2 times.
	cd ./_glitched
			corrupt_file_copy=0
	for x in $( seq $2 )
		do
				corrupt_file_copy=$((corrupt_file_copy + 1))
				echo generating corrupt file copy number $corrupt_file_copy for $element . . .
		glitchThisFile.sh "$element" $3
		done
	rm "$element"
	cd ..
			# another option, which would be done without a loop; use bm.exe, to be found in this repository: https://github.com/earthbound19/_ebdev
			# bm.exe "$element" bm.exe $1 -x jpg -u 100 -r 12 -t 1 -s 9 -a 5 -v -m +-
done < _alles.txt
rm ./_alles.txt

# because my windows Cygwin install can be a buggy moron about permissions:
# chmod 777 ./_glitched/*