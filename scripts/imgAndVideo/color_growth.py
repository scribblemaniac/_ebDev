"""Renders a PNG image like bacteria that mutate color as they spread.

Output file names are based on the date and time and random characters.
Inspired and drastically evolved from color_fibers.py, which was horked and adapted
from https://scipython.com/blog/computer-generated-contemporary-art/

# USAGE
Run this script without any parameters, and it will use a default set of parameters:
python thisScript.py
To see available parameters, run this script with the -h switch:
python thisScript.py -h

# DEPENDENCIES
python 3 with numpy and pyimage modules installed (and maybe others--see the
import statements).

# KNOWN ISSUES
See help for --RANDOM_SEED.

# TO DO
See comments under the same heading in this module.

"""

# TO DO:
# - Refactor algorithm for better efficiency if possible
#   - Examine whether and why exponential slowdown occurs over the run of the script, and whether
#     it is something in --RECLAIM_ORPHANS that does this. Symptom: newly_painted_coords as
#     reported by print_progress(newly_painted_coords) stays in a roughly
#     constant neighborhood from about halfway through the render to the end, but it may be taking
#     longer and longer to render that same number of coordinates. I think my math/model for
#     reclaiming coordinates may have something to do with that. Could I do some math _like_
#     that used in counting and resetting coordinates to report in
#     print_progress(newly_painted_coords), but with reclaiming orphans?
#     - I think the slowdown is from checking newly allocated coords are not in allocd_coords.
#      That set gets larger as the image progresses, so it would make sense that checking a
#      larger set takes longer toward the end of the render. Do I really even need such a set?
#      Couldn't I only check the unallocd_coords set and know that if it's not in that set,
#      it is an allocated coordinate (so that I don't even need an allocd_coords set at all)?
#    - Option to have RECLAIM_ORPHANS do its work only once (without reactivating continued
#      painting) when STOP_AT_PERCENT is reached?
#    - Develop scripted tests of all possible switch combinations, with timing baseline
#      and improvement checks.
# - See if compiled/transpiled versions of this are faster. In tests:
#  - pyinstaller compiled packages were ~the same speed. Not exciting.
# - Make default variables that are tuples and lists either those or strings, not both
#   for (consistency). If strings, you'll want to remove redundant str() conversion in help.
#   - Destroy -n option and associated functionality because of the problems described in the
#   help for that option. I would rather that I or others be forced to script repeat runs of
#   this script, which is more unixy (leave that function to another program) and to fix this
#   I'd have to refactor this to mess with sys.argv[] to save the new deterministically
#   generated seed to .cgp files at each new image creation loop which just seems unduly messy.
# - Fix "KNOWN ISSUE" described in help for --RANDOM_SEED.
# - Option and function to explicitly set start coords from set of tuple coordinates
# - Initialize COLOR_MUTATION_BASE by random selection from a .hexplt color scheme
# - Option to set start coords color mutation bases from .hexplt color scheme (would override)
#   initialization from set of tuple coords
# - Option to suppress progress print to save time
# - Fixes re pylint comments at end, also things listed in development code with TO DO comments
# - Option: instead of randomly mutating color for each individual chosen neighbor coordinate,
#   mutate them all to the same new color. This would be more efficient, and might make colors
#   more banded/ringed/spready than streamy. It would also visually indicate coordinate mutation
#   more clearly. Do this or the other option (mutate each, so each can be different) based on
#   an option check.
#  - option to randomly alternate that method as you go
#  - option to set the random chance for using one or the other
# - Add a --NO_DELIST_NEIGHBORS option to make coords fight for space as mentioned in this commit: https://github.com/earthbound19/_ebDev/commit/16dfa0718fea630c919836c7d2326e2bdcbabb83
# - Major new feature? : Initialize canvas[] from an image, pick a random coordinate from the
#   image, and use the color at that coordinate both as the origin coordinate and the color at
#   that coordinate as COLOR_MUTATION_BASE. Could also be used to continue terminated runs with
#   the same or different parameters.
# - Major new feature: use multiple CPU cores, or parallelizing the algorithm (one thread per
#   mutation from an origin coordinate). Whether it would be advantageous or even feasible would
#   be answered by the attempt. Re: https://superuser.com/a/679685
#   https://stackoverflow.com/a/1743350 (which points to https://www.parallelpython.com/)


# CODE
import datetime
import random
import argparse
import ast
import os.path
import sys
import re
import subprocess
import shlex
import numpy as np
from PIL import Image


# Defaults which will be overriden if arguments of the same name are provided to the script:
NUMBER_OF_IMAGES = 1
WIDTH = 400
HEIGHT = 200
RSHIFT = 5
STOP_AT_PERCENT = 1
SAVE_EVERY_N = 0
START_COORDS_RANGE = (1, 13)
GROWTH_CLIP = (0, 5)
SAVE_PRESET = True
# BACKGROUND color options;
# any of these (uncomment only one) are made into a list later by ast.literal_eval(BG_COLOR) :
# BG_COLOR = "[157,140,157]"        # Medium purplish gray
BG_COLOR = "[252,251,201]"        # Buttery light yellow
RECLAIM_ORPHANS = True


# START OPTIONS AND GLOBALS
PARSER = argparse.ArgumentParser(description='Renders a PNG image like bacteria that produce\
random color mutations as they grow over a surface. Output file names are after the date plus\
random characters. Inspired by and drastically evolved from colorFibers.py, which was horked\
and adapted from https://scipython.com/blog/computer-generated-contemporary-art/')
PARSER.add_argument('-n', '--NUMBER_OF_IMAGES', type=int, help='How many images to generate.\
Default ' + str(NUMBER_OF_IMAGES) +'. WARNING: if you want to be able to later deterministially\
re-create a high resolution image which happens to be e.g. the 40th in a series where n=40\
(using this -n switch with the --RANDOM_SEED switch), that may be time costly (because the\
determinant of that 40th image factors all pseudo-randomness used for all prior images), and\
you may wish to not do that. You may wish to set -n 1 for high resolution images (only make\
one image per run in that case). NOTE: A portion of the code for this script may have its\
"loop mode" altered, resulting in different image evolution either more stringy/meandering\
coordinate evolution or not). See "LOOP MODE OPTIONS" in the comments in this script.')
PARSER.add_argument('--WIDTH', type=int, help='WIDTH of output image(s). Default '\
+ str(WIDTH) + '.')
PARSER.add_argument('--HEIGHT', type=int, help='HEIGHT of output image(s). Default '\
+ str(HEIGHT) + '.')
PARSER.add_argument('-r', '--RSHIFT', type=int, help='Vary R, G and B channel values randomly\
in the range negative this value or positive this value. Note that this means the range is\
RSHIFT times two. Defaut ' + str(RSHIFT) + '.')
PARSER.add_argument('-b', '--BG_COLOR', type=str, help='Canvas color. Expressed as a python\
list or single number that will be assigned to every value in an RGB triplet. If a list, give\
the RGB values in the format \'[255,70,70]\' (if you add spaces after the commas, you must\
surround the parameter in single or double quotes). This example would produce a deep red, as\
Red = 255, Green = 70, Blue = 70). A single number example like just 150 will result in a\
medium-light gray of [150,150,150] (Red = 150, Green = 150, Blue = 150). All values must be\
between 0 and 255. Default ' + str(BG_COLOR) + '.')
PARSER.add_argument('-c', '--COLOR_MUTATION_BASE', type=str, help='Base initialization color\
for pixels, which randomly mutates as painting proceeds. If omitted, defaults to whatever\
BG_COLOR is. If included, may differ from BG_COLOR. This option must be given in the same\
format as BG_COLOR.')
PARSER.add_argument('--RECLAIM_ORPHANS', type=str, help='With higher --VISCOSITY, coordinates\
can be painted around (by coordinate and color mutation of surrounding coordinates) but never\
themselves painted. This option coralls these orphan coordinates and, after all other living\
coordinates evolve (die), revives these orphans. If there are orphans after that, it repeats,\
and so on, until every coordinate is painted. Default on. To disable pass --RECLAIM_ORPHANS\
False or --RECLAIM_ORPHANS 0.')
PARSER.add_argument('--STOP_AT_PERCENT', type=float, help='What percent canvas fill to stop\
painting at. To paint until the canvas is filled (which can take extremely long for higher\
resolutions), pass 1 (for 100 percent). If not 1, value should be a percent expressed as a\
decimal (float) between 0 and 1 (e.g 0.4 for 40 percent. Default ' + str(STOP_AT_PERCENT) +\
'. For high --failedMutationsThreshold or random walk (neither of which is implemented at\
this writing), 0.475 (around 48 percent) is recommended. Stop percent is adhered to\
approximately (it could be much less efficient to make it exact).')
PARSER.add_argument('-a', '--SAVE_EVERY_N', type=int, help='Every N successful coordinate and\
color mutations, save an animation frame into a subfolder named after the intended final art\
file. To save every frame, set this to 1, or to save every 3rd frame set it to 3, etc. Saves\
zero-padded numbered frames to a subfolder which may be strung together into an animation of\
the entire painting process (for example via ffmpegAnim.sh). May substantially slow down\
render, and can also create many, many gigabytes of data, depending. ' + str(SAVE_EVERY_N) +\
' by default. To disable, set it to 0 with: -a 0 OR: --SAVE_EVERY_N 0')
PARSER.add_argument('-s', '--RANDOM_SEED', type=int, help='Seed for random number generators\
(random and numpy.random are used). Default generated by random library itself and added to\
render file name for reference. Can be any integer in the range 0 to 4294967296 (2^32). If\
not provided, it will be randomly chosen from that range (meta!). If --SAVE_PRESET is used,\
the chosen seed will be saved with the preset .cgp file. KNOWN ISSUE at this writing:\
 evidently functional differences between random generators of different versions of Python\
 and/or Python on different platforms produce different output from the same random seed.')
PARSER.add_argument('-q', '--START_COORDS_N', type=int, help='How many origin coordinates to\
begin coordinate and color mutation from. Default randomly chosen from range in\
--START_COORDS_RANGE (see). Random selection from that range is performed *after* random\
seeding by --RANDOM_SEED, so that the same random seed will always produce the same number\
of start coordinates. I haven\'t tested whether this will work if the number exceeds the\
number of coordinates possible in the image. Maybe it would just overlap itself until\
they\'re all used?')
PARSER.add_argument('--START_COORDS_RANGE', help='Random integer range to select a random\
number of --START_COORDS_N if --START_COORDS_N is not provided. Default ('\
+ str(START_COORDS_RANGE[0]) + ',' + str(START_COORDS_RANGE[1]) + '). Must be provided in\
that form (a string surrounded by double quote marks (for Windows) which can be evaluated to\
 a python tuple), and in the range 0 to 4294967296 (2^32), but I bet that sometimes\
 nothing will render if you choose a max range number orders of magnitude higher than the\
 number of pixels available in the image. I probably would never make the max range higher\
 than (number of pixesl in image) / 62500 (which is 250 squared). Will not be used if\
 [-q | START_COORDS_N] is provided.')
PARSER.add_argument('--GROWTH_CLIP', type=str, help='Affects seeming "thickness"\
 (or viscosity) of the liquid. A Python tuple expressed as a string (must be surrounded by\
 double quote marks for Windows). Default ' + str(GROWTH_CLIP) + '. In growth into\
 adjacent coordinates, the maximum number of possible neighbor coordinates to grow into is\
 8 (which may only ever happen with a start coordinate: in practical terms, the most\
 coordinates that may usually be expanded into is 7). The first number in the tuple is\
 the minimum number of coordinates to randomly select, and the second number is the\
 maximum. The second must be greater than the first. The first may be lower than 0 and\
 will be clipped to 1, making selection of only 1 neighbor coordinate more common. The\
 second number may be higher than 8 (or the number of available coordinates as the case\
 may be), and will be clipped to the maximum number of available coordinates, making\
 selection of all available coordinates more common. If the first number is a positive\
 integer <= 7, at least that many coordinates will always be selected when possible. If the\
 second number is a positive integer >= 1, at most that many coordinates will ever be selected.\
 A negative first number or low first number clip will tend toward a more evenly spreading\
 liquid appearance, and a lower second number clip will cause a more stringy/meandering/splatty\
 path or form\ (as it spreads less uniformly). With an effectively more viscous clip like\
 "(2, 4)", smaller streamy/flood things may traverse a distance faster. Some tuples make\
 --RECLAIM_ORPHANS quickly fail, some make it virtually never fail.')
PARSER.add_argument('--SAVE_PRESET', type=str, help='Save all parameters (which are passed to\
this script) to a .cgp (color growth preset) file. If provided, --SAVE_PRESET must be a string\
representing a boolean state (True or False or 1 or 0). Default '+ str(SAVE_PRESET) +'.\
The .cgp file can later be loaded with the --LOAD_PRESET switch to create either new or\
identical work from the same parameters (whether it is new or identical depends on the\
switches, --RANDOM_SEED being the most consequential). This with [-a | --SAVE_EVERY_N] can\
recreate gigabytes of exactly the same animation frames using just a preset. NOTES:\
--START_COORDS_RANGE and its accompanying value are not saved to config files, and the\
resultantly generated [-q | --START_COORDS_N] is saved instead. Note: you may add arbitrary\
 text (such as notes) to the second and subsequent lines of a saved preset, as only the first\
 line is used.')
PARSER.add_argument('--LOAD_PRESET', type=str, help='A preset file (as first created by\
--SAVE_PRESET) to use. Empty (none used) by default. Not saved to any preset. At this\
writing only a single file name is handled, not a path, and it is assumed the file is in\
the current directory. NOTE: use of this switch discards all other parameters and loads all\
parameters from the preset. A .cgp preset file is a plain text file on one line, which is a\
collection of SWITCHES to be passed to this script, written literally the way you would pass\
them to this script.')

# START ARGUMENT PARSING
# DEVELOPER NOTE: Throughout the below argument checks, wherever a user does not specify
# an argument and I use a default (as defaults are defined near the start of working code
# in this script), add that default switch and switch value pair to sys.argv, for use by
# the --SAVE_PRESET feature (which saves everything except for the script path ([0]) to
# a preset). I take this approach because I can't check if a default value was supplied
# if I do that in the PARSER.add_argument function --
# http://python.6.x6.nabble.com/argparse-tell-if-arg-was-defaulted-td1528162.html -- so what
# I do is check for None (and then supply a default and add to argv if None is found).
# The check for None isn't literal: it's in the else: clause after an if (value) check
# (if the if check fails, that means the value is None, and else: is invoked) :
print('~-')
print('~- Processing any arguments to script . . .')
ARGS = PARSER.parse_args()      # When this function is called, if -h or --help was passed
                                # to the script, it will print the description and all
                                # defined help messages.

# IF A PRESET file is given, load its contents (which should be a collection of CLI
# switches for this script itself) and pass them to a new running instance of this script,
# then exit this script:
if ARGS.LOAD_PRESET:
    LOAD_PRESET = ARGS.LOAD_PRESET
    print('LOAD_PRESET is', LOAD_PRESET)
    # print('path to this script itself is', sys.argv[0])
    print('Attempting to load subprocess of this script with the SWITCHES in LOAD_PRESET . . .')
    with open(LOAD_PRESET) as f:
        SWITCHES = f.readline()
    subprocess.call(shlex.split('python ' + repr(sys.argv[0]) + ' ' + SWITCHES))
    # sys.argv[0] is the path to this script.
    # repr() found at: http://code.activestate.com/recipes/65211-convert-a-string-into-a-raw-string/#c5
    # repr() fixes some problem with shlex.split string handling of Windows paths.
    print('Subprocess hopefully completed successfully. Will now exit script.')
    sys.exit()

# If a user supplied an argument (so that NUMBER_OF_IMAGES has a value (is not None), use that:
if ARGS.NUMBER_OF_IMAGES:
    # It is in argv already, so it will be used by --SAVE_PRESET:
    NUMBER_OF_IMAGES = ARGS.NUMBER_OF_IMAGES
# If not, leave the default as it was defined, and add to sys.argv for reasons given above:
else:
    sys.argv.append('-n')
    sys.argv.append(str(NUMBER_OF_IMAGES))

if ARGS.WIDTH:
    WIDTH = ARGS.WIDTH
else:
    sys.argv.append('--WIDTH')
    sys.argv.append(str(WIDTH))

if ARGS.HEIGHT:
    HEIGHT = ARGS.HEIGHT
else:
    sys.argv.append('--HEIGHT')
    sys.argv.append(str(HEIGHT))

if ARGS.RSHIFT:
    RSHIFT = ARGS.RSHIFT
else:
    sys.argv.append('--RSHIFT')
    sys.argv.append(str(RSHIFT))

if ARGS.BG_COLOR:
    # For preset saving, remove spaces and write back to sys.argv, so a preset saved by
    # --SAVE_PRESET won't cause errors:
    BG_COLOR = ARGS.BG_COLOR
    BG_COLOR = re.sub(' ', '', BG_COLOR)
    IDX = sys.argv.index(ARGS.BG_COLOR)
    sys.argv[IDX] = BG_COLOR
else:
    sys.argv.append('-b')
    sys.argv.append(BG_COLOR)
# Convert BG_COLOR (as set from ARGS.BG_COLOR or default) string to python list for use
# by this script, re: https://stackoverflow.com/a/1894296/1397555
BG_COLOR = ast.literal_eval(BG_COLOR)

if ARGS.COLOR_MUTATION_BASE:        # See comments in ARGS.BG_COLOR handling. Handled the same.
    COLOR_MUTATION_BASE = ARGS.COLOR_MUTATION_BASE
    COLOR_MUTATION_BASE = re.sub(' ', '', COLOR_MUTATION_BASE)
    IDX = sys.argv.index(ARGS.COLOR_MUTATION_BASE)
    sys.argv[IDX] = COLOR_MUTATION_BASE
    COLOR_MUTATION_BASE = ast.literal_eval(COLOR_MUTATION_BASE)
else:       # Write same string as BG_COLOR, after the same silly string manipulation as
            # for COLOR_MUTATION_BASE, but more ridiculously now _back_ from that to
            # a string again:
    BG_COLOR_TMP_STR = str(BG_COLOR)
    BG_COLOR_TMP_STR = re.sub(' ', '', BG_COLOR_TMP_STR)
    sys.argv.append('-c')
    sys.argv.append(BG_COLOR_TMP_STR)
    # In this case we're using a list as already assigned to BG_COLOR:
    COLOR_MUTATION_BASE = list(BG_COLOR)
    # If I hadn't used list(), COLOR_MUTATION_BASE would be a reference to BG_COLOR (which
    # is default Python list handling behavior with the = operator), and when I changed either,
    # "both" would change (but they would really just be different names for the same list).
    # I want them to be different.

# purple = [255, 0, 255]    # Purple. In prior commits of this script, this has been defined
# and unused, just like in real life. Now, it is commented out or not even defined, just
# like it is in real life.

if ARGS.RECLAIM_ORPHANS:
    RECLAIM_ORPHANS = ast.literal_eval(ARGS.RECLAIM_ORPHANS)
else:
    sys.argv.append('--RECLAIM_ORPHANS')
    sys.argv.append(str(RECLAIM_ORPHANS))

if ARGS.STOP_AT_PERCENT:
    STOP_AT_PERCENT = ARGS.STOP_AT_PERCENT
else:
    sys.argv.append('--STOP_AT_PERCENT')
    sys.argv.append(str(STOP_AT_PERCENT))

if ARGS.SAVE_EVERY_N:
    SAVE_EVERY_N = ARGS.SAVE_EVERY_N
else:
    sys.argv.append('-a')
    sys.argv.append(str(SAVE_EVERY_N))
if ARGS.RANDOM_SEED:
    RANDOM_SEED = ARGS.RANDOM_SEED
else:
    RANDOM_SEED = random.randint(0, 4294967296)
    sys.argv.append('--RANDOM_SEED')
    sys.argv.append(str(RANDOM_SEED))
# Use that seed straightway:
random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)

    # BEGIN STATE MACHINE "Megergeberg 5,000."
    # DOCUMENTATION.
    # Possible combinations of these variables to handle; "coords" means START_COORDS_N,
    # RNDcoords means START_COORDS_RANGE:
    # --
    # ('coords', 'RNDcoords') : use coords, delete any RNDcoords
    # ('coords', 'noRNDcoords') : use coords, no need to delete any RNDcoords. These two:
    # if coords if RNDcoords.
    # ('noCoords', 'RNDcoords') : assign user-provided RNDcoords for use (overwrite defaults).
    # ('noCoords', 'noRNDcoords') : continue with RNDcoords defaults (don't overwrite defaults).
    # These two: else if RNDcoords else. Also these two: generate coords independent of
    # (outside) that last if else (by using whatever RNDcoords ends up being (user-provided
    # or default).
    # --
    # I COULD just have four different, independent "if" checks explicitly for those four
    # pairs and work from that, but this is more compact logic (fewer checks)
    # (a tenuous justification).
if ARGS.START_COORDS_N:        # If --START_COORDS_N is provided by the user, use it..
    START_COORDS_N = ARGS.START_COORDS_N
    print('Will use the provided --START_COORDS_N, ', START_COORDS_N)
    if ARGS.START_COORDS_RANGE:
        # .. and delete any --START_COORDS_RANGE and its value from sys.argv (as it will
        # not be used and would best not be stored in the .cgp config file via --SAVE_PRESET:
        IDX = sys.argv.index(ARGS.START_COORDS_RANGE)
        del sys.argv[IDX-1]         # Why does index() return a one-based index for a
                                    # zero-based index list?!
        del sys.argv[IDX-1]         # Note that the element at the same index is deleted
                                    # twice because after the first is deleted, the second
                                    # moves to the index of the first.
        print('** NOTE: ** You provided both [-q | --START_COORDS_N] and --START_COORDS_RANGE,\
 but the former overrides the latter (the latter will not be used). This program removed\
 the latter from the sys.argv parameters list.')
else:        # If --START_COORDS_N is _not_ provided by the user..
    if ARGS.START_COORDS_RANGE:
        # .. but if --START_COORDS_RANGE _is_ provided, assign from that:
        START_COORDS_RANGE = ast.literal_eval(ARGS.START_COORDS_RANGE)
        STR_PART = 'from user-supplied range ' + str(START_COORDS_RANGE)
    else:        # .. otherwise use the default START_COORDS_RANGE:
        STR_PART = 'from default range ' + str(START_COORDS_RANGE)
    START_COORDS_N = random.randint(START_COORDS_RANGE[0], START_COORDS_RANGE[1])
    sys.argv.append('-q')
    sys.argv.append(str(START_COORDS_N))
    print('Using', START_COORDS_N, 'start coordinates, by random selection ' + STR_PART)
    # END STATE MACHINE "Megergeberg 5,000."

if ARGS.GROWTH_CLIP:        # See comments in ARGS.BG_COLOR handling. Handled the same.
    GROWTH_CLIP = ARGS.GROWTH_CLIP
    GROWTH_CLIP = re.sub(' ', '', GROWTH_CLIP)
    IDX = sys.argv.index(ARGS.GROWTH_CLIP)
    sys.argv[IDX] = GROWTH_CLIP
    # For optional code at the end of the script that renames to parameter demo file names:
    growth_clip_tst_file_name = re.sub('\(', '', GROWTH_CLIP)
    growth_clip_tst_file_name = re.sub('\)', '', growth_clip_tst_file_name)
    growth_clip_tst_file_name_base = '__' + re.sub(',', '_', growth_clip_tst_file_name) + '__'
    zax_blor = ('%03x' % random.randrange(16**6))
    png_rename = growth_clip_tst_file_name_base + '__' + zax_blor + '.png'
    cgp_rename = growth_clip_tst_file_name_base + '__' + zax_blor + '.cgp'
    mp4_rename = growth_clip_tst_file_name_base + '__' + zax_blor + '.mp4'
    GROWTH_CLIP = ast.literal_eval(GROWTH_CLIP)
else:
    temp_str = str(GROWTH_CLIP)
    temp_str = re.sub(' ', '', temp_str)
    sys.argv.append('--GROWTH_CLIP')
    sys.argv.append(temp_str)

if ARGS.SAVE_PRESET:
    SAVE_PRESET = ast.literal_eval(ARGS.SAVE_PRESET)
else:
    sys.argv.append('--SAVE_PRESET')
    sys.argv.append(str(SAVE_PRESET))

if SAVE_PRESET:
    SCRIPT_ARGS_STR = sys.argv[1:]
    SCRIPT_ARGS_STR = ' '.join(str(element) for element in SCRIPT_ARGS_STR)
# END ARGUMENT PARSING

ALL_PIXELS_N = WIDTH * HEIGHT
TERMINATE_PIXELS_N = int(ALL_PIXELS_N * STOP_AT_PERCENT)

# START COORDINATE CLASS
class Coordinate:

    """

    Intended for use with a dict indexed by tuple coordinates, to generate images as described
    in this modules' main docstring. yx_tuple is a tuple representing a Y and X coordinate (in
    the intended final image). x and y are passed to class on init and used to set that tuple.
    max_x and max_y are the X and Y max dimension of the image (image size). color
    is the rendered color in the final image. unallocd_neighbors is the set of neighboring
    coordinates which have never been allocated for use ("use" being filled with a color).

    """

    # slots for allegedly higher efficiency re: https://stackoverflow.com/a/49789270
    __slots__ = ["yx_tuple", "x", "y", "max_x", "max_y", "color", "unallocd_neighbors"]
    def __init__(self, x, y, max_x, max_y, color):
        self.yx_tuple = (y, x)
        self.x = x
        self.y = y
        self.color = color
        # Adding all possible empty neighbor values even if they would result in values out
        # of bounds of image (negative or past max_x or max_y), and will check for and clean up
        # pairs with out of bounds values after:
        self.unallocd_neighbors = {(y-1, x-1), (y, x-1), (y+1, x-1), (y-1, x), (y+1, x), (y-1, x+1),
                                (y, x+1), (y+1, x+1)}
        to_remove = set()
        for element in self.unallocd_neighbors:
            if -1 in element:
                to_remove.add(element)
        for element in self.unallocd_neighbors:
            if element[1] == max_x:
                to_remove.add(element)
        for element in self.unallocd_neighbors:
            if element[0] == max_y:
                to_remove.add(element)
        # the deletions:
        for remove_this in to_remove:
            self.unallocd_neighbors.remove(remove_this)
    def get_rnd_unallocd_neighbors(self):
        """Returns both a set() of randomly selected empty neighbor coordinates to use
        immediately, and a set() of neighbors to use later."""
        # init an empty set we'll populate with neighbors (int tuples) and return:
        rnd_neighbors_to_ret = set()
        if self.unallocd_neighbors:        # If there is anything left in unallocd_neighbors:
            # START VISCOSITY CONTROL.
            # Decide how many to pick:
            n_neighbors_to_ret = np.random.randint(GROWTH_CLIP[0], GROWTH_CLIP[1] + 1)
            if n_neighbors_to_ret < 0:
                n_neighbors_to_ret = 1
            if n_neighbors_to_ret > len(self.unallocd_neighbors):
                n_neighbors_to_ret = len(self.unallocd_neighbors)
            # END VISCOSITY CONTROL.
            rnd_neighbors_to_ret = set(random.sample(self.unallocd_neighbors, n_neighbors_to_ret))
        return rnd_neighbors_to_ret, self.unallocd_neighbors
# END COORDINATE CLASS

def birth_coord(color, tuple_to_alloc, unallocd_coords, allocd_coords, canvas):
    """color is a list of RGB values e.g. [255,0,255]. unallocd_coords and allocd_coords
    are sets. canvas is a dict of Coordinate objects. As these are all passed by reference
    (the default Python way), so the sets and dict are manipulated directly by the function."""
    # Move tuple_to_alloc out of unallocd_coords and into allocd_coords, depending:
    if tuple_to_alloc in unallocd_coords and tuple_to_alloc not in allocd_coords:
        unallocd_coords.remove(tuple_to_alloc)
        allocd_coords.add(tuple_to_alloc)
        # Give that new living coord, IN canvas[], a parent color (to later mutate from):
        canvas[tuple_to_alloc].color = color
        # Remove the coord corresponding to tuple_to_alloc from the unallocd_neighbors lists
        # of all available neighbor coords (if it appears in those set()s), so that in later use
        # of those empty neighbor set()s, we won't erroneously attempt to be reuse the coord:
        tmp_set_one = set(canvas[tuple_to_alloc].unallocd_neighbors)
        for search_coord in tmp_set_one:
            if tuple_to_alloc in canvas[search_coord].unallocd_neighbors:
                canvas[search_coord].unallocd_neighbors.remove(tuple_to_alloc)
    return tuple_to_alloc

def coords_set_to_image(canvas, HEIGHT, WIDTH, image_file_name):
    """Creates and saves image from dict of Coordinate objects, HEIGHT and WIDTH definitions,
    and a filename string."""
    tmp_array = []
    for i in range(0, HEIGHT):
        coords_row = []
        for j in range(0, WIDTH):
            coords_row.append(canvas[(i, j)].color)
        tmp_array.append(coords_row)
    tmp_array = np.asarray(tmp_array)
    image_to_save = Image.fromarray(tmp_array.astype(np.uint8)).convert('RGB')
    image_to_save.save(image_file_name)

def print_progress(newly_painted_coords):
    """Prints coordinate plotting statistics (progress report)."""
    print('newly painted : total painted : target : canvas size : reclaimed orphans') 
    print(newly_painted_coords, ':', painted_coordinates, ':',\
    TERMINATE_PIXELS_N, ':', ALL_PIXELS_N, ':', orphans_to_reclaim_n)
# END GLOBAL FUNCTIONS
# END OPTIONS AND GLOBALS


"""START MAIN FUNCTIONALITY."""
print('Will generate ', NUMBER_OF_IMAGES, ' image(s).')

# Loop making [-n | NUMBER_OF_IMAGES] images.
for n in range(1, (NUMBER_OF_IMAGES + 1)):        # + 1 because it iterates n *after* the loop.
    animation_save_counter_n = 0
    animation_frame_counter = 0

    # A dict of Coordinate objects which is used with tracking sets to fill a "canvas:"
    canvas = {}
    # A set of coordinates (tuples, not Coordinate objects) which are free for the taking:
    unallocd_coords = set()
    # A set of coordinates (again tuples) which are set aside (allocated) for use:
    allocd_coords = set()
    # A set of coordinates (again tuples) which have been color mutated and may no longer
    # coordinate mutate:
    filled_coords = set()

    # Initialize canvas dict and unallocd_coords set (canvas being a dict of Coordinates with
    # tuple coordinates as keys:
    for y in range(0, HEIGHT):        # for columns (x) in row)
        for x in range(0, WIDTH):        # over the columns, prep and add:
            canvas[(y, x)] = Coordinate(x, y, WIDTH, HEIGHT, BG_COLOR)
            unallocd_coords.add((y, x))

    # Initialize allocd_coords set by random selection from unallocd_coords (and remove
    # from unallocd_coords):
    # for i in range(0, START_COORDS_N):
# TO DO: check if things here and here would be faster for getting a random sample:
# https://medium.freecodecamp.org/how-to-get-embarrassingly-fast-random-subset-sampling-with-python-da9b27d494d9
# https://stackoverflow.com/a/15993515/1397555
    RNDcoord = random.sample(unallocd_coords, START_COORDS_N)
    for coordX in RNDcoord:
        birth_coord(COLOR_MUTATION_BASE, coordX, unallocd_coords, allocd_coords, canvas)

    report_stats_every_n = 3
    report_stats_nth_counter = 0

    # Create unique, date-time informative image file name. Note that this will represent
    # when the painting began, not when it ended (~State filename will be based off this).
    now = datetime.datetime.now()
    time_stamp = now.strftime('%Y_%m_%d__%H_%M_%S__')
    # Returns three random lowercase hex characters:
    rndStr = ('%03x' % random.randrange(16**6))
    file_base_name = time_stamp + rndStr + '_colorGrowth-Py'
    image_file_name = file_base_name + '.png'
    state_img_file_name = file_base_name + '-state.png'
    anim_frames_folder_name = file_base_name + '_frames'

    # If SAVE_EVERY_N has a value greater than zero, create a subfolder to write frames to;
    # Also, initailize a varialbe which is how many zeros to pad animation save frame file
    # (numbers) to, based on how many frames will be rendered:
    if SAVE_EVERY_N > 0:
        pad_file_name_numbers_n = len(str(TERMINATE_PIXELS_N))
        os.mkdir(anim_frames_folder_name)

    # If bool set saying so, save arguments to this script to a .cgp file with the target
    # render base file name:
    if SAVE_PRESET:
        file = open(file_base_name + '.cgp', "w")
        file.write(SCRIPT_ARGS_STR)
        file.close()

    # ----
    # START IMAGE MAPPING
    painted_coordinates = 0
    # With higher VISCOSITY some coordinates can be painted around (by other coordinates on
    # all sides) but coordinate mutation never actually moves into that coordinate. The
    # result is that some coordinates may never be "born." this set and associated code
    # revives orphan coordinates:
    potential_orphan_coords_two = set()
    # used to reclaim orphan coordinates every N iterations through the
    # `while allocd_coords` loop:
    base_orphan_reclaim_multiplier = 0.015
    orphans_to_reclaim_n = 0
    coords_painted_since_reclaim = 0
    # These next two variables are used to ramp up orphan coordinate reclamation rate
    # as the render proceeds:
    print('Generating image . . . ')
    newly_painted_coords = 0        # This is reset at every call of print_progress()
    while allocd_coords:
        # NOTE: There are two options for looping here. Mode 0 (which was the first developed
        # mode) makes a copy of allocd_coords, and loops through that. The result is that the
        # loop doesn't continue because of changes to allocd_coords (as it is working on a
        # copy which becomes outdates as the loop progresses). Mode 1 loops through
        # allocd_coords itself, and since this loop changes allocd_coords, it makes the
        # loop run longer. In mode 1 similar color meanders more (runaway streams of color
        # are possible). It also finishes the image faster. Mode 1 spreads more uniformly
        # (with less possibility of runaway streams. Which mode produces more interesting
        # and beautiful results is subjective and for me depends also on target resolution.
# LOOP MODE OPTIONS.
         # For loop mode 0, uncomment the next two lines of code, and comment out the third
         # line after that. For mode 1, comment out the next two lines, and uncomment the
         # third line after that:
        copy_of_allocd_coords = set(allocd_coords)
        for coord in copy_of_allocd_coords:    # Mode 0, test run time: 0m34.241s
        # for coord in allocd_coords:       # Mode 1, test run time: 0m32.502s
            # Remove that to avoid wasted calculations (so many empty tuples passed
            # to birth_coord) :
            allocd_coords.remove(coord)
            if coord not in filled_coords:
                # Mutate color--! and assign it to the color variable (list) in the Coordinate object:
                canvas[coord].color = canvas[coord].color + np.random.randint(-RSHIFT, RSHIFT + 1, size=3) / 2
                # print('Colored coordinate (y, x)', coord)
                canvas[coord].color = np.clip(canvas[coord].color, 0, 255)
                new_allocd_coords_color = canvas[coord].color
                filled_coords.add(coord)        # When a coordinate has its color mutated, it dies.
                painted_coordinates += 1
                newly_painted_coords += 1
                coords_painted_since_reclaim += 1
                # The first returned set is used straightway, the second optionally shuffles
                # into the first after the first is depleted:
                rnd_new_coords_set, potential_orphan_coords_one = canvas[coord].get_rnd_unallocd_neighbors()
                for coordZurg in rnd_new_coords_set:
                    birth_coord(new_allocd_coords_color, coordZurg, unallocd_coords, allocd_coords, canvas)
# Potential and actual orphan coordinate handling:
#                Set color in Coordinate object in canvas dict via potential_orphan_coords_one:
                for coordGronk in potential_orphan_coords_one:
                    canvas[coordGronk].color = new_allocd_coords_color
                # set union (| "addition," -ish) :
                potential_orphan_coords_two = potential_orphan_coords_two | potential_orphan_coords_one
#        Conditionally reclaim orphaned coordinates. Code here to reclaim coordinates gradually (not in spurts as at first coded) is harder to read and inelegant. I'm leaving it that way. Because GEH, DONE.
        if RECLAIM_ORPHANS:
            # removes elements from potential_orphan_coords_two which are in filled_coords
            # (to avoid reusing coordinates) ; set subtraction; orphanCoords declared here:
            orphanCoords = potential_orphan_coords_two - filled_coords
            # decide how many orphans to reclaim; use int() to avoid decimals:
            orphans_to_reclaim_n = int(coords_painted_since_reclaim * base_orphan_reclaim_multiplier)
            coords_painted_since_reclaim = 0
            # clip that to acceptable range if necessary:
            if orphans_to_reclaim_n <= 0:
                orphans_to_reclaim_n = 1
            if orphans_to_reclaim_n > len(orphanCoords):
                orphans_to_reclaim_n = len(orphanCoords)
            # get those orphans and then move them into allocd_coords:
# TO DO: more efficient sampling than creating a list here, if possible:
            tmp_set = set(random.sample(orphanCoords, orphans_to_reclaim_n))
            # The while loop will continue if there's anything in allocd_coords;
            # set "addition" with |  :
            allocd_coords = allocd_coords | tmp_set
            # print('Reclaimed', orphans_to_reclaim_n, 'orphan coordinates.')

# TO DO: I might like it if this stopped saving new frames after every coordinate was
# colored (it can (always does?) save extra redundant frames at the end;
        # Save an animation frame if that variable has a value:
        if SAVE_EVERY_N:
            if (animation_save_counter_n % SAVE_EVERY_N) == 0:
                strOfThat = str(animation_frame_counter)
                img_frame_file_name = anim_frames_folder_name + '/' + strOfThat.zfill(pad_file_name_numbers_n) + '.png'
                coords_set_to_image(canvas, HEIGHT, WIDTH, img_frame_file_name)
                # Increment that *after*, for image tools expecting series starting at 0:
                animation_frame_counter += 1
            animation_save_counter_n += 1

        # Save a snapshot/progress image and print progress:
        if report_stats_nth_counter == 0 or report_stats_nth_counter == report_stats_every_n:
            # print('Saving prograss snapshot image ', state_img_file_name, ' . . .')
            coords_set_to_image(canvas, HEIGHT, WIDTH, state_img_file_name)
            print_progress(newly_painted_coords)
            newly_painted_coords = 0
            report_stats_nth_counter = 1
        report_stats_nth_counter += 1

        # This will terminate all coordinate and color mutation at an arbitary number of mutations.
        if painted_coordinates >= TERMINATE_PIXELS_N:
            print('Painted coordinate termination count', painted_coordinates, 'reached (or recently exceeded). Ending paint algorithm.')
            break
    # END IMAGE MAPPING
    # ----

    # Save final image file and delete progress (state, temp) image file:
    print('Saving image ', image_file_name, ' . . .')
    coords_set_to_image(canvas, HEIGHT, WIDTH, image_file_name)
    print('Created ', n, ' of ', NUMBER_OF_IMAGES, ' images.')
    os.remove(state_img_file_name)
# END MAIN FUNCTIONALITY.


# OPTIONAL, sys cd into anim frames subfolder and invoke ffmpegAnim.sh to make an animation
# and/or rename files to GROWTH_CLIP parameter demo files names:
# os.chdir(anim_frames_folder_name)
# subprocess.call('ffmpegAnim.sh 30 30 7 png', shell = True)
# subprocess.call('open _out.mp4', shell=True)
# Danger Will Robinson! :
# subprocess.call('rm *.png', shell=True)
# OPTIONAL, TO RENAME THE OUTPUT files to a GROWTH_CLIP parameter demo file; ASSUMES only one image made:
# mv_png_command = 'mv ../' + image_file_name + ' ../' + png_rename
# mv_cgp_command = 'mv ../' + file_base_name + '.cgp ../' + cgp_rename
# mv_mp4_command = 'mv ./_out.mp4 ' + '../' + mp4_rename
# subprocess.call(mv_png_command, shell=True)
# subprocess.call(mv_cgp_command, shell=True)
# subprocess.call(mv_mp4_command, shell=True)
# os.chdir('..')
# subprocess.call('rm -rf ' + anim_frames_folder_name, shell = True)


# MUCH BETTERER REFERENCE:
# arr = np.ones((HEIGHT, WIDTH, 3)) * BG_COLOR
# # THAT ARRAY is organized as [down][across] OR [y][x] OR [HEIGHT - n][WIDTH - n] OR [row][column]; re the following numpy / PIL-compatible list of lists of lists of numbers and debug print to help understand the structure:
# arr[2][3] = [255,0,255]        # y (down) = 1, x (across) = 2 (actual coordinates are +1 each because of zero-based indexing)
# for y in range(0, HEIGHT):
#    print('- y HEIGHT (', HEIGHT, ') iterator ', y, 'in arr[', y, '] gives:\n', arr[y])
#    for x in range(0, WIDTH):
#        print(' -- x WIDTH (', WIDTH, ') iterator ', x, 'in arr[', y, '][', x, '] gives:', arr[y][x])

# Duplicating that structure with a list of lists:
# imgArr = []        # Intended to be a list of lists
# for y in range(0, HEIGHT):        # for columns (x) in row)
#    tmp_set = []
#    for x in range(0, WIDTH):        # over the columns, prep and add:
#        tmp_set.append(Coordinate(x, y, WIDTH, HEIGHT, BG_COLOR, False, False, None))
#    imgArr.append(tmp_set)

# Printing the second to compare to the first for comprehension:
# print('------------')
# for y in range(0, HEIGHT):
#    print('-')
#    for x in range(0, WIDTH):
#        print(' -- imgArr[y][x].yx_tuple (imgArr[', y, '][', x, '].yx_tuple) is:', imgArr[y][x].yx_tuple)
#        print(' ALSO I think the empty neighbor coordinate list in the Coordinate object at [y][x] can be used with this list of lists structure for instant access of neighbor coordinates?! That list here is:', imgArr[y][x].unallocd_neighbors, ' . . .')
#        rndEmptyNeighborList = imgArr[y][x].get_rnd_unallocd_neighbors()
#        print(' HERE ALSO is a random selection of those neighbors:', rndEmptyNeighborList)


# pylint errors or warnings I care about:
# color_growth.py:401:26: W0621: Redefining name 'y' from outer scope (line 518) (redefined-outer-name)
# color_growth.py:401:23: W0621: Redefining name 'x' from outer scope (line 519) (redefined-outer-name)
# color_growth.py:455:31: W0621: Redefining name 'filled_coords' from outer scope (line 514) (redefined-outer-name)
# color_growth.py:455:16: W0621: Redefining name 'allocd_coords' from outer scope (line 511) (redefined-outer-name)
# color_growth.py:455:44: W0621: Redefining name 'canvas' from outer scope (line 507) (redefined-outer-name)
# color_growth.py:475:41: W0621: Redefining name 'WIDTH' from outer scope (line 64) (redefined-outer-name)
# color_growth.py:475:25: W0621: Redefining name 'canvas' from outer scope (line 507) (redefined-outer-name)
# color_growth.py:475:33: W0621: Redefining name 'HEIGHT' from outer scope (line 65) (redefined-outer-name)
# color_growth.py:475:48: W0621: Redefining name 'image_file_name' from outer scope (line 543) (redefined-outer-name)
# color_growth.py:475:0: C0103: Argument name "HEIGHT" doesn't conform to snake_case naming style (invalid-name)
# color_growth.py:475:0: C0103: Argument name "WIDTH" doesn't conform to snake_case naming style (invalid-name)
# color_growth.py:498:0: W0105: String statement has no effect (pointless-string-statement)