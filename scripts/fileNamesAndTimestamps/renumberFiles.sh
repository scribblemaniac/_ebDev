# DESCRIPTION
# Renames all files of a given extension (via parameter) in the path from which this script is called--renames them to zero-padded numbers matching the number of digit columns of the count of all said files. WARNINGS: 1) use this only in directories where you actually want _all_ files of the given extension renamed by numbers. 2) If any of your file names are numeric-only (e.g. 005.png) *before* you run this script against them, files may disappear via overwrite, effectively erasing that file by replacing it with new content. For example, a file named 005.png may be overwritten when a file named someOtherFile.png is renamed to 005.png, overwriting the original file named 005.png.

# USAGE
# With this script in your $PATH, invoke it from a terminal, passing it one paramater, being the file extension (without a dot) that you wish for it to operate on, e.g.:
# renumberFiles.sh png

# NOTE: this will choke on file names with console-unfriendly characters e.g. spaces, parenthesis and probably others.

# TO DO? give this script a warning y/n prompt.
# TO DO? Make the option to move all renamed files in the path to the root folder this is invoked from a parameter option?


# CODE
echo Hi persnonzez!!!!!!!!!!!!!!! HI!! -Nem

# Get count of files we want, and from that digits to pad to. Use sort because ls doesn't do sensible sorting on some platforms:
filesCount=`gfind . -maxdepth 1 -iname \*.$1 | sort | wc -l`
digitsToPadTo=`expr $filesCount : '.*'`

# Create array to use to loop over files.
filesArray=`gfind . -maxdepth 1 -iname "*.$1" | sort`

counter=0
for filename in ${filesArray[@]}
do
	counter=$((counter + 1))
	countString=`printf "%0""$digitsToPadTo""d\n" $counter`
			# echo old file name is\: $filename
			# echo new file name is\: $countString.$1
	mv $filename $countString.$1
done

# DEVELOPMENT HISTORY
# 2018/04/19 Take `mapfile` out (fails on Mac) and create array in-memory. Wrangle how to get digitsToPadTo value meanwhile. (Do it before.)
# 2016/07/17 I wish it hadn't taken me a silly half hour (more?) to write this. It used to be it would take much longer, so there's that. -RAH
# 2016/10/12 7:16 PM Fixed bug (via workaround) for echo bug that throws in extra \r charactesr in some situations.