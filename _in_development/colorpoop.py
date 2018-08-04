# IN DEVELOPMENT. Intended for use in colorGrowth.py, but could be imported into any other python file.

import random
import numpy as np

class coordinate:
	# slots for allegedly higher efficiency re: https://stackoverflow.com/a/49789270
	__slots__ = ["x", "y", "maxX", "maxY", "RGBcolor", "isAlive", "isConsumed", "emptyNeighbors"]
	def __init__(self, x, y, maxX, maxY, RGBcolor, isAlive, isConsumed, emptyNeighbors):
		self.x = x;	self.y = y;	self.RGBcolor = RGBcolor; self.isAlive = isAlive;	self.isConsumed = isConsumed
		# Adding all possible empty neighbor values even if they would result in values out of bounds of image (negative or past maxX or maxY), and will check for and clean up pairs with out of bounds values after:
		tmpList = [ (x-1, y-1), (x-1, y), (x-1, y+1), (x, y-1), (x, y+1), (x+1, y-1), (x+1, y), (x+1, y+1) ]
			# List of possible neighbor relative coordinates for any coordinate (unless the coordinate is at a border):
			# x-1, y-1	:	left, up		ONE
			# x-1, y	:	left			TWO
			# x-1, y+1	:	left, down		THREE
			# x, y-1	:	up				FOUR
			# x, y+1	:	down			FIVE
			# x+1, y-1	:	right, up		SIX
			# x+1, y	:	right			SEVEN
			# x+1, y+1	:	right, down		EIGHT
			# -~-~ I DOUBLE-CHECKED and verified that all intialized values in tmpList in this class initalize according to this list.
		# make lists of all tuples that contain out of range values, then use the list to delete those tuples from the list of tuples; re: https://www.quora.com/How-do-you-search-a-list-of-tuples-in-Python
		deleteList = []
		for element in tmpList:
			if -1 in element:
				deleteList.append(element)
		for element in tmpList:		# TO DO: debug whether I even need this; the print never happens:
			if (maxX+1) in element:
				deleteList.append(element)
		for element in tmpList:
			if (maxY+1) in element:
				deleteList.append(element)
		# reduce deleteList to a list of unique tuples (in case of duplicates, which can lead us to attempt to remove something that ins't there, which throws an exception and stops the script) :
		deleteList = list(set(deleteList))
		# the deletions:
		for no in deleteList:
			tmpList.remove(no)
		# finallu initialize the intended object member from that built list:
		self.emptyNeighbors = list(tmpList)
	def getRNDemptyNeighbors(self):
		random.shuffle(self.emptyNeighbors)		# shuffle the list of empty neighbor coordinates
		nNeighborsToReturn = np.random.random_integers(0, len(self.emptyNeighbors))		# Decide how many to pick
		rndNeighborsToReturn = []		# init an empty array we'll populate with neighbors and return
		# iterate over nNeighborsToReturn items in shuffled self.emptyNeighbors and add them to a list to return:
		for pick in range(0, nNeighborsToReturn):
			rndNeighborsToReturn.append(self.emptyNeighbors[pick])
		return rndNeighborsToReturn