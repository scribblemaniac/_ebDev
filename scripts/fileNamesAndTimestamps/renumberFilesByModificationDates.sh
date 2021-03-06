# DESCRIPTION
# Renames all files of a given extension (via parameter) in the path from which this script is called--renames them to zero-padded numbers matching the number of digit columns of the count of all said files. Same as renumberFiles.sh with the added condition that files will be sorted by creation date (oldest first, or ascending). WARNINGS: 1) use this only in directories where you actually want _all_ files of the given extension renamed by numbers. 2) If any of your file names are numeric-only (e.g. 005.png) *before* you run this script against them, files may disappear via overwrite, effectively erasing that file by replacing it with new content. For example, a file named 005.png may be overwritten when a file named someOtherFile.png is renamed to 005.png, overwriting the original file named 005.png.

# USAGE
# With this script in your $PATH, invoke it from a terminal, passing it one paramater, being the file extension (without a dot) that you wish for it to operate on, e.g.:
# renumberFiles.sh png

# NOTE: this will choke on file names with console-unfriendly characters e.g. spaces, parenthesis and probably others.

# TO DO
# Give this script a warning y/n prompt?

# CODE
echo Hi persnonzez!!!!!!!!!!!!!!! HI!! -Nem

# Get count of files we want, and from that digits to pad to.
# The necessity of deleting leading blank space is because of Mac. Re: https://stackoverflow.com/a/30927885 : GYAH! This doom was had 2018-04-19 Thursday 07:33 PM:
filesCount=`gfind \*.$1 -maxdepth 1 | wc -l | tr -d ' '`
digitsToPadTo=${#filesCount}

# Create array to use to loop over files. Sort by modified date stamp re genius breath yon: https://superuser.com/a/294164
filesArray=`gfind \*.bak -printf '%T@ %p\0' | sort -zk 1n | sed -z 's/^[^ ]* //' | tr '\0' '\n'`

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
# 06/27/2018 06:09:20 AM adapt from renumberFiles.sh (with one line changed after adapting the former to changes from this).
