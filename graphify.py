#!python

'''
Desired format:
	<thread_name>, <block name>, <start_time>, <duration>, <color>
'''
import numpy as np
import json
import matplotlib
import matplotlib.pyplot as plt
import sys
import os
import pandas
from collections import Counter

if (len(sys.argv) != 2):
	print ("Usage:\n  convertJsonToCSV.py filepath.json")
	sys.exit()

filepath = sys.argv[1]
print (f'Processing {filepath}')
json_file = open(filepath,"r")
data = json.loads(json_file.read())
json_file.close()

'''Building block ID to color map'''
idColorMap = dict()
for block in data["blockDescriptors"]:
	idColorMap[block["id"]] = block["color"]


def processChildrenRecursive(children):
	blocks = []
	for key in children:
		if "children" in key:
			blocks = blocks + processChildrenRecursive(key["children"])
		else:
			sanitizedName = "".join(x for x in key["name"] if x.isalnum())
			blocks.append({"name":sanitizedName,"start":key["start"], "duration":(key["stop"] - key["start"]), "color":(idColorMap[key["descriptor"]])})
	return blocks

'''Building dictionary of thread names to blocks'''
threadBlocksMap = dict()
for thread in data["threads"]:
	sanitizedName = "".join(x for x in thread["threadName"] if x.isalnum())
	if "children" in thread:
		threadBlocksMap[sanitizedName] = processChildrenRecursive(thread["children"])

filename, ext = os.path.splitext(filepath)

csvFilename = f'{filename}.csv'
csvFile = open(csvFilename, 'w')
for thread in threadBlocksMap:
	print(f'Processing thread {thread}')
	for block in threadBlocksMap[thread]:
		csvFile.write(f'{thread},"{block["name"]}",{block["start"]},{block["duration"]},{block["color"]}\n')


data = np.genfromtxt(csvFilename, dtype='str', delimiter=",")

matplotlib.rcParams.update({'font.size': 6})

threads = data[:,0]
threadsUnique = np.unique(threads)

resultFolder = f'{filename}_results'
os.makedirs(resultFolder, exist_ok=True)

for thread in threadsUnique:
	print(f'  Processing blocks for {thread}')
	thread_blocks = data[data[:,0] == thread][:,1]
	blockCounts = Counter(thread_blocks)
	dataframe = pandas.DataFrame.from_dict(blockCounts, orient='index')
	fig = dataframe.plot(kind='bar').get_figure()
	fig.suptitle(f'Call frequency for {thread}')
	fig.savefig(f'{resultFolder}/{filename}_{thread}_frequency.png', bbox_inches='tight')
	plt.close()

blocks = data[:,1]
blockCounts = Counter(blocks)
dataframe = pandas.DataFrame.from_dict(blockCounts, orient='index')
fig = dataframe.plot(kind='bar').get_figure()
fig.suptitle("Call frequency")
fig.savefig(f'{resultFolder}/{filename}_frequency.png', bbox_inches='tight')
plt.close()

'''Histograms of block durations'''
for block in np.unique(blocks):
	sanitizedName = "".join(x for x in block if x.isalnum())
	durations = data[data[:,1] == block][:,3]
	durationsInSeconds = [float(x) / 1000000 for x in durations]
	plt.hist(durationsInSeconds, bins=10)
	plt.title(sanitizedName)
	plt.savefig(f'{resultFolder}/{filename}_{sanitizedName}_hist.png', bbox_inches='tight')
	plt.close()
