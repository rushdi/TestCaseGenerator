*** Settings ***
Documentation	 	Current Testcase Documentation
...Chapter Number	1.2.0.1
...ID	V&VM101
...Test Case Title	Vector Addition
...Test Case Description	Randomly take two 64 bit values and make input file then pass to the vector addition function for the output. The system also create reference output file then it will check output and refereance output for the system.

Library		SSHLibrary
Library		OperatingSystem
Library		Process

Resource		input.txt

Resource		resource.txt

Resource		referenceOutput.txt

Resource		output.txt

*** Test Cases ***

Case 1: Login to Remote Machine
	[Documentation]		Login to Remote Machine with username and password
	Open Connection		${Remote Host}
	Login		${Remote Username}		${Remote Password}

Case 2: Create Folder to Remote Machine
	[Documentation]		Create Folder to Remote Machine with mode 777
	Execute Command		${Directory Created Command} ${Remote Path}${Created Remote Folder Name}		both
	Sleep		3s

Case 3: Copy File to Remote Machine
	[Documentation]		Copy All Files Source to Remote Machine
	Put File		${Source Path}${Source Folder Name}${Copy Source File Name}		${Remote Path}${Created Remote Folder Name}		mode=0770
	Sleep		3s

Case 4: Execute Testcase to Remote Machine
	[Documentation]		Execute Testcase to Remote Machine
	Execute Command		python ${Execute Remote File Name}		both

Case 5: Copy File to Source Machine
	[Documentation]		Copy All Files Remote Machine to Source
	Get File		${Remote Path}${Created Remote Folder Name}${Copy Target File Name}		${Source Path}${Source Folder Name}/
	Sleep		3s

Case 6: Delete File from Remote Machine
	[Documentation]		Delete All Files from Remote Machine
	Remove File		${Remote Path}${Delete Remote Folder Name}${Delete Remote File Name}

Case 7: Logout from Remote Machine
	[Documentation]		Logout from Remote Machine
	Close All Connections
	Sleep		3s

Case 8: Checking Value in Source Machine
	[Documentation]		Compare output with reference output
	${x}=		Run Process		python		../src/controller/valueCompare.py		print 'Execute python'
