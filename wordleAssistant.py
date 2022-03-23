import re
import readline
import time

from collections import defaultdict

known = ["" for i in range(5)]
notSets = [set() for i in range(5)]
somewhere = set()
runningList = set()
knownAndSomewhere = defaultdict(int)

# Using previous and current inputs, continue to pare down the list of possible words
# using RegEx matching 
def assessGuess(guessList):
	knownAndSomewhereCurrent = defaultdict(int)

	# Parse out the guessed letters and result for each
	# Check the "no" results after processing all known and somewhere 
	# So that words aren't accidentally eliminated
	for i in range(5):
		letter = guessList[i][0]
		result = guessList[i][1]

		# Letter was green, this is the only letter that can go in this spot
		# Increment the count of times this letter appears in the word
		if guessList[i][1] == "g":
			known[i] = letter
			knownAndSomewhereCurrent[letter] += 1

		# Letter was yellow, it is in the word but not in this position
		# Increment the count of times this letter appears in the word 
		# Add this letter to the notSet for this position
		elif result == "y":
			notSets[i].add(letter)
			somewhere.add(letter)
			knownAndSomewhereCurrent[letter] += 1

	# Parse through results again to check for "no" (gray) results
	for i in range(5):
		letterList = [char for char in guessList[i]]
		letter = guessList[i][0]
		result = guessList[i][1]

		# Letter was gray so it is not in the word at all, or if yellow/green elsewhere, 
		# IS in the word but not more than a given number
		if result == "n":
			# If the letter is known to be somewhere else in the word, only add it to 
			# the not set for this position
			if letter in knownAndSomewhereCurrent:
				notSets[i].add(letter)
			# If the letter does not appear elsewhere in the word, add to all not sets
			else:
				for j in range(5):
					notSets[j].add(letter)

	# If we now know there are more occurences of the letter than we did before, update 
	# the running count of occurences
	for letter in knownAndSomewhereCurrent:
		if knownAndSomewhereCurrent[letter] > knownAndSomewhere[letter]:
			knownAndSomewhere[letter] = knownAndSomewhereCurrent[letter]

	# Create a RegEx of the letters we are certain about;
	# whose place is known or that are known to NOT appear in a certain position or the word at all
	certainPattern = ""
	for i in range(5):
		if known[i] != "":
			certainPattern += known[i]
		else:
			notString = ''.join(notSets[i])
			certainPattern += "[^" + notString + "]"


	certainRegex = re.compile(certainPattern)

	# Determine which words don't match the RegEx and should be removed from the possible set
	remove = set()
	for word in runningList:
		if not certainRegex.match(word):
			remove.add(word)
	for word in remove:
		runningList.remove(word)

	# For each of max 5 letters known to appear (either known or unknown location),
	# create a regex to catch words with that letter appearing the number of times expected
	# Any words with the letter appearing in the wrong position(s) have already been eliminated
	for unknown in somewhere:
		somewherePattern = ".*"
		for i in range(knownAndSomewhere[unknown]):
			somewherePattern += ("%c.*" % unknown)
		somewhereRegex = re.compile(somewherePattern)

		# Determine which words don't match the RegEx and should be removed from the possible set
		remove = set()
		for word in runningList:
			if not somewhereRegex.match(word):
				remove.add(word)

		for word in remove:
			runningList.remove(word)

	# If there are no possible words left (due to incomplete word list in "five_letter_words") 
	# or user error, exit
	# If only one possible word left, prompt user to try it and exit on response
	# Otherwise, display stats and words and prompt user for next guess 
	if len(runningList) == 0:
		print("Sorry, no words found matching those restrictions :(")
		exit(0)
	elif len(runningList) == 1:
		word = runningList.pop()
		guess = input("\nOnly one possible word! Is it %s? (y/n): " % word.upper()).lower()
		if guess == "y":
			print("\n!!!!!!!!!!!!!!\nWordle solved!\n!!!!!!!!!!!!!!\n")
			time.sleep(1)
			exit(0)
		else:
			print("\nSorry, no other words matching your restrictions.")
			time.sleep(1)
			exit(0)
	else:
		printStats()
		printRunningList()

	status = ""
	for i in range(5):
		if known[i] != "":
			status += known[i].upper() + " "
		else:
			status += "_ "
	print("STATUS: %s\n" % status)


# Print out the list of possible words remaining
def printRunningList():
	print("\n\nPOSSIBLE WORDS\n--------------", end='')

	# Keep track of current first letter to put words starting with different letters on separate lines
	currentLetter = ""
	for word in sorted(runningList):
		if word[0] != currentLetter:
			currentLetter = word[0]
			word = "\n%s" % word
		print("%s " % word, end='')
	print("\n")


# Print out some stats about the letter percentages of remaining possible words
def printStats():
	# Create a list of dictionaries to store letter counts in, and an inverse
	letterCountDicts = [defaultdict(float) for i in range(5)]
	letterCountInverseDicts = [defaultdict(list) for i in range(5)]

	# Create a dictionary to store overall counts in, and an inverse
	overallCountDict = defaultdict(float)
	overallCountInverseDict = defaultdict(list)

	# We don't want to include known letters in the overall stats
	totalSpots = 5
	for i in range(5):
		if known[i] != "":
			totalSpots -= 1

	# Total number of letters there should be
	lettersPerSpot = float(len(runningList))
	totalLetters = lettersPerSpot * totalSpots

	# Determine the number of times each letter appears in each position 1-5 in the possible words
	for word in runningList:
		for i in range(5):
			letterCountDicts[i][word[i]] += 1

	# For each letter and each spot, determine their percent occurence in that spot 
	# Create a new dictionary where percent is the key and the letters are the values,
	# So that we can sort on highest percent
	# At the same time, keep an overall count of letter occurences and create a similar
	# dictionary based on the percents
	for i in range(5):
		for k, v in letterCountDicts[i].items():
			if known[i] == "":
				overallCountDict[k] += v
			percent = round((v / lettersPerSpot) * 100, 2)
			letterCountInverseDicts[i][percent].append(k)

	for k, v in overallCountDict.items():
		percent = round((v / totalLetters) * 100, 2)
		overallCountInverseDict[percent].append(k)

	print("\nLETTER PERCENT APPEARANCE IN REMAINING WORDS\n--------------------------------------------", end='')


	for i in range(5):
		print("\nSPOT %d | " % (i+1), end='')
		for k, v in reversed(sorted(letterCountInverseDicts[i].items())):
			for letter in v:
				print("%c : %.2f%%  " % (letter, k), end='')

	print("\n\nOVERALL FOR UNDETERMINED SPOTS | ", end='')
	for k, v in reversed(sorted(overallCountInverseDict.items())):
		for letter in v:
			print("%c : %.2f%%  " % (letter, k), end='')
 

def main():
	print("============================\nWelcome to WordleAssistant!\n============================")
	time.sleep(1)
	print("Input your wordle guess as each of the five letters followed by the result")
	time.sleep(1)
	print("Use the following letters to indicate the result G = green, Y = yellow, N = no (gray)")
	time.sleep(1)
	print("Example: For guess S T A R E, where S was Green, T was Yellow, and A R E were Gray, input\nsG tY aN rN eN\n")
	time.sleep(1)
	with open("five_letter_words") as f:
		for word in f:
			runningList.add(word.strip())

	for i in range(5):
		valid = False
		while not valid:
			guess = ""
			try:
				guess = input("Enter guess %d and results : " % (i+1)).lower().strip()
				if guess == "exit" or guess == "exit()":
					exit(0)
			except KeyboardInterrupt:
				print("\n")
				exit(0)

			# Make sure the entry is valid. It should contain 5 "spots" and 2 chars per spot. 
			# Only alpha chars should be used. Only g, n, y should be present in second position for each spot.
			guessList = guess.split(" ")
			if len(guessList) == 5:
				someInvalid = False
				for spot in guessList:
					spotReqs = re.compile("[a-z]{1}[gny]{1}")
					if len(spot) != 2 or not spotReqs.match(spot):
						someInvalid = True
				if not someInvalid:
					assessGuess(guessList)
					valid = True
			if not valid:
				print("\nInvalid input. Try again.")

	print("\nTime to make your final guess! Good luck!")
	exit(0)

if __name__ == "__main__":
    main()