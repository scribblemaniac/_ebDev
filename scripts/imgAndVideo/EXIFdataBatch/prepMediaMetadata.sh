# DESCRIPTION: Prepares image metadata text file for insertion into images via exiftool (I forget the command or batch that does that; TO DO: implement that.)

# USAGE: CORRECT. SEE DESCRIPTION. Run this from a cygwin prompt in a directory with images in the directory tree for which you wish to create custom metadata ~_MD_ADDS.txt files which another script will use to set image metadata tags. NOTE: for videos, copy the generated title into the description field of the final metadata source file.

# DEV NOTE: if you make only temporary changes to this for ripping art, revert the changes so there aren't a lot of extraneous repository commits of unnecessary changes.

# Q. Should those be _FINAL_ and _EXPORTED_, not _FINAL and _EXPORTED ? :
# _MTPL=_FINAL
_MTPL=_EXPORTED_

# NOTE: cygpath use else err next:
metaDataTemplatePath=`cygpath -u "C:\_devtools\scripts\imgAndVideo\EXIFdataBatch\metaDataTemplates"`
	# Pick and uncomment one:
	metaDataTemplateFile=customImageMetadataTemplate.txt
	# metaDataTemplateFile=electricSheep_CC_by_sa_template.txt
	# metaDataTemplateFile=fractalFlame_template.txt
	# metaDataTemplateFile=DrawnColorVectorArtMetadataTemplate.txt
	# metaDataTemplateFile=vectorRandomColorAnimTemplate.txt
	# metaDataTemplateFile=TFTMdraftMetadataTemplate.txt
metaDataTemplate=$metaDataTemplatePath/$metaDataTemplateFile

cygwinFind . -iname \*$_MTPL*.mp4 -o -iname \*$_MTPL*.tif -o -iname \*$_MTPL*.tiff -o -iname \*$_MTPL*.png -o -iname \*$_MTPL*.psd  -o -iname \*$_MTPL*.psb -o -iname \*$_MTPL*.ora -o -iname \*$_MTPL*.rif -o -iname \*$_MTPL*.riff -o -iname \*$_MTPL*.jpg -o -iname \*$_MTPL*.jpeg -o -iname \*$_MTPL*.gif -o -iname \*$_MTPL*.bmp -o -iname \*$_MTPL*.cr2 -o -iname \*$_MTPL*.raw  -o -iname \*$_MTPL*.crw -o -iname \*$_MTPL*.pdf  -o -iname \*$_MTPL*.svg > imagesMetadataPrepList.txt

cygwinFind . -iname \*"$_MTPL"var*.mp4 -o -iname \*"$_MTPL"var*.tif -o -iname \*"$_MTPL"VAR*.tiff -o -iname \*"$_MTPL"VAR*.png -o -iname \*"$_MTPL"VAR*.psd -o -iname \*"$_MTPL"*.psb -o -iname \*"$_MTPL"VAR*.ora -o -iname \*"$_MTPL"VAR*.rif -o -iname \*"$_MTPL"VAR*.riff -o -iname \*"$_MTPL"VAR*.jpg -o -iname \*"$_MTPL"VAR*.jpeg -o -iname \*"$_MTPL"VAR*.gif -o -iname \*"$_MTPL"VAR*.bmp -o -iname \*"$_MTPL"VAR*.cr2 -o -iname \*"$_MTPL"VAR*.raw  -o -iname \*"$_MTPL"VAR*.crw -o -iname \*"$_MTPL"VAR*.pdf -o -iname \*"$_MTPL"VAR*.svg >> imagesMetadataPrepList.txt
				# FORMER CODE:
				# cygwinFind . -iname \*$_MTPL*.tif > imagesMetadataPrepList.txt
				# cygwinFind . -iname \*"$_MTPL"var_*.tif >> imagesMetadataPrepList.txt


# dev reference; for to do the preceding line but with many differtent file types:
# use prefix=\*_FINAL*		~finalvar~			?	;		OR an or regex if poss.?	:
	# cygwinFind . -iname \*.tif -o -iname \*.tiff -o -iname \*.png -o -iname \*.psd -o -iname \*.ora -o -iname \*.rif -o -iname \*.riff -o -iname \*.jpg -o -iname \*.jpeg -o -iname \*.gif -o -iname \*.bmp -o -iname \*.cr2 -o -iname \*.raw  -o -iname \*.crw -o -iname \*.pdf > imageFilesList.txt
# OR: just list _all_ image files to text file, then reduce it to list _final / _finalvar name-tagged file names only?
# Because all those necessary searches can lead to duplicate listings, sort everything and trim duplicates:
sort imagesMetadataPrepList.txt > temp1.txt
uniq temp1.txt > temp2.txt
	# Remove ./ from start of file li . . neh.
	# sed i- 's/^\.\/\(.*\)/g' temp2.txt
rm imagesMetadataPrepList.txt temp1.txt
mv temp2.txt imagesMetadataPrepList.txt

echo starting metadata prep . . .

currdir=`pwd`
mapfile -t imagesMetadataPrepArray < imagesMetadataPrepList.txt
for element in "${imagesMetadataPrepArray[@]}"
do
		# echo Preparing image metadata from template and image file name $element . . .
					# DEPRECATED, because much as I hate it, putting like-named files into a new subfolder will cause path length errors in windows:
					# imagePath=`expr match "$element" '\(.*\)\/.*'`
					# if [ -a $imagePath/_metadataAdditions ]
		imagePath=`expr match "$element" '\(.*\)\/.*'`
		imageFileNameNoExt=`expr match "$element" '.*\/\(.*\)\..*'`
		metaDataAdditionsTextFile=$imagePath/$imageFileNameNoExt\_MD_ADDS.txt
				# NOTE: the following check previously didn't behave as wanted, because I erroneously checked for $imagePath/$metaDataAdditionsTextFile:
		if [ -a $metaDataAdditionsTextFile ]
		then
			# DO NOT OVERWRITE THE EXISTING FILE
			echo =~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~
			echo Would-be newly created metadata additions text file already exists \($metaDataAdditionsTextFile\). Will not overwrite.
		else
			# CREATE AND DO STUFF with the new file
			echo CREATING METADATA PREP FILE $currdir\/$metaDataAdditionsTextFile\ . . .
			# Write file name to text file and alter for human readability via text search-replacements:
			echo $imageFileNameNoExt > temp.txt
				# TO DO: other text replacements besides the following?
				sed -i 's/_[fF][iI][nN][aA][lL]//g' temp.txt
				sed -i 's/_[fF][iI][nN][aA][lL][vV][aA][rR]/Variation of/g' temp.txt
				sed -i 's/FFlib/Filter Forge library/g' temp.txt
				sed -i 's/FF\([0-9]\{1,\}..\)/Filter Forge library \1/g' temp.txt
				sed -i 's/pre\([0-9]\{1,\}\)/preset \1/g' temp.txt
				# Delete any leading whitespace from name field:
				tr '_' ' ' < temp.txt > temp2.txt
				sed -i 's/^\s\{1,\}//g' temp2.txt
					# ALSO WORKS on that last line: ~   [[:space:]]    instead of    \s
				sed -i 's/^[vV][aA][rR] /Variation of /g' temp2.txt
					# Thanks to: http://stackoverflow.com/a/10771857 :
			imagePreparedTitle=$( < temp2.txt)
				# Alas, there is no MWG mapping of ObjectName/Title; this is an IPTC only thing; which is another reason the final distribution image will be renamed to the image title:
			echo \-IPTC:ObjectName\=\"$imagePreparedTitle\" > temp.txt
			# Create stub metadata file using (modified) filename for title and metadata template:
			cat temp.txt $metaDataTemplate > $metaDataAdditionsTextFile
			rm temp.txt temp2.txt
			# So the tag to be added doesn't get munged onto the same line as the last tag:
			printf "\n" >> $metaDataAdditionsTextFile
# TO DO? Add this snarf? : https://iptc.org/standards/newscodes/groups/
			echo \-EXIF:ImageHistory\=\"Exported or copied from master file\: $element\" >> $metaDataAdditionsTextFile
			# Open the metadata prep file and corresponding image file in the default programs, to make any necessary metadata prep. changes:
			echo =~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~
			read -n 1 -p "After you press any key, the metadata text file $metaDataAdditionsTextFile and corresponding image \"$element\" will open. There will be a short pause before it opens. Edit and save the opened prep text file, then close it and the image. Another prompt (if any) will appear here."
			cygstart $element
				# Because delays loading the text file into an editor (COMPUTER SCIENCE?!) can cause image viewer focus problems; force-focus the image for 2 seconds, by way of a pause:
			sleep 2
			cygstart $metaDataAdditionsTextFile
			echo =~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~
		fi
done


# ~-~-~-~-~-~-~-~-~-~-
# probably outdated dev notes and code, re VIDEO METADATA:
# ECHO OFF
# NOTE: For this batch to work properly, the parameter passed to it must be surrounded by double quote marks.
# mp4 Tags available to exiftool are the same as for quicktime, listed here: http://www.sno.phy.queensu.ca/~phil/exiftool/TagNames/QuickTime.html
# Other info for exiftool and mp4: http://130.15.24.88/exiftool/forum/index.php?topic=6318.0
# Tags available to add/update via ffmpeg are listed at: http://wiki.multimedia.cx/index.php?title=FFmpeg_Metadata#QuickTime.2FMOV.2FMP4.2FM4A.2Fet_al.
# We're using: title, artist, keywords (for tags), description, copyright, and GenreID 4415 ("movies|special interest")
# the optional -overwrite_original parameter specifies not to create a backup file.

# exiftool -P -copyright="This work is an original creation created and owned by Richard Alexander Hall. All rights reserved." -category="Experimental" -description="Rapid animated color noise scaled up many times preserving hard edges. Contrived from RGB values obtained from random.org. Could be used in various layering/compositing modes to add randomness to animated abstractions (e.g. to produce color fluctuation in an animated canvas, or to repeat in a ten hour animation with nyan cat music, to show to a toddler strapped into a chair, to provide them euphoria/a meltdown). " -artist="Richard Alexander Hall" -keywords="abstract, animation, art, abstract art, noise, color noise" -title=%1 %1

# exiftool %1 > %1_tagInfo.txt

# use these (they write to valid fields):
# -MWG:Description="this is a thing"
# ~-~-~-~-~-~-~-~-~-~-


# DEVELOPMENT HISTORY:
# BEFORE NOW: SO MANY CODE. SO COMPUTER SCIENCE. SO WOW.
# 2016-04-26 10:27 PM: regex title prep from filename. Add support for many image file types. One-handed programming in broken radius surgery recovery duress. -RAH
# 05/09/2016 02:39:48 AM Tweaks in tandem with imgTagAndDist.sh dev/debugging. -RAH