#!python

'''
Desired format:
	<thread_name>, <block name>, <start_time>, <duration>, <color>
'''

import json
import sys
import os

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
		if key == "children":
			blocks.append(processChildrenRecursive(key))
		else:
			blocks.append({"name":key["name"], "start":key["start"], "duration":(key["stop"] - key["start"]), "color":(idColorMap[key["descriptor"]])})
	return blocks

'''Building dictionary of thread names to blocks'''
threadBlocksMap = dict()
for thread in data["threads"]:
	if "children" in thread:
		threadBlocksMap[thread["threadName"]] = processChildrenRecursive(thread["children"])

filename, ext = os.path.splitext(filepath)

csvFile = open(f'{filename}.csv', 'w')
for thread in threadBlocksMap:
	print(f'Processing thread {thread}')
	for block in threadBlocksMap[thread]:
		csvFile.write(f'{thread},{block["name"]},{block["start"]},{block["duration"]},{block["color"]}\n')
