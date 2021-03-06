# DESCRIPTION
# Lossy transcodes all video files in the current directory (doesn't scan subdirectories) into mp4s compatible with Sony Vegas 12.

# USAGE
# Invoke this with one paramater, being the extension of videos you wish to encode to Sony Vegas compatible video.
# Vcompat = compatible with Sony (V)egas video editing software. 2016-04-26 9:46 PM -RAH

# DEPENDENCIES
# gfind (gnu find), ffmpeg, a 'nixy environment.


# CODE
# DEV NOTES
# lossless encode, adapted from: http://www.konstantindmitriev.ru/blog/2014/03/02/how-to-encode-vegas-compatible-h-264-file-using-ffmpeg/
# Re encoding quality: -q 0 is lossless, -q 23 is default, and -q 51 is worst.
# Re: https://trac.ffmpeg.org/wiki/Encode/H.264

additionalParams_one="-preset slow -tune animation"
# additionalParams_two="-pix_fmt yuv420p"
# Makes a video matte by scaling down a bit and placing on a dark dark violet background:
# additionalParams_three="-vf scale=-1:1054:force_original_aspect_ratio=1,pad=1920:1080:(ow-iw)/2:(oh-ih)/2:color=1a171e"

arr=(`gfind . -maxdepth 1 -type f -iname \*.$1 -printf '%f\n'`)
for filename in ${arr[@]}
do
	fileNameNoExt=${filename%.*}
	targetFile="$fileNameNoExt".mp4
	# CHECK if target render already exists. If it does, skip render and notify user. Otherwise render.
	if [ -e $targetFile ]
	then
				echo Target render file $targetFile already exists\; will not overwrite\; SKIPPING RENDER.
	else
				echo Target render file $targetFile does not exist\; RENDERING.
		ffmpeg -i "$filename" $additionalParams_one $additionalParams_two $additionalParams_three -c:v libx264 -crf 17 -b:a 192k -ar 48000 $targetFile
				# ffmpeg -y -i "$filename" -map 0:v -vcodec copy "filename"_temp.mp4
	fi
done

# COMMAND THAT removes audio:
# ffmpeg -y -i __corrupted_1pct_2016_10_22__03_23_54__639469500__out.mp4_utvideo.avi -map 0:v -c:v libx264 -crf 12 -pix_fmt yuv420p __corrupted_1pct_2016_10_22__03_23_54__639469500__out.mp4_utvideo.mp4