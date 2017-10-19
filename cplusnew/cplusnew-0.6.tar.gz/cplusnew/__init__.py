import os
import subprocess
import re


def main(proj):
	createFolders(proj)
	createFiles(proj)

def createFolders(proj):
	folders = ['bin', 'build', 'doc', 'include', 'lib', 'src', 'test']
	os.system('mkdir -p {}/{}'.format( proj,' {}/'.format(proj).join(folders) ))

def createFiles(proj):
	files = ['CMakeLists.txt', 'src/main.cpp']
	os.system('touch {} '.format( ' {}/'.format(proj).join(files) ))

	fillCMakeLists(proj)

def fillCMakeLists(proj):

	stdfill = [	"include_directories(include)", 
				"file(GLOB SOURCES \"src/*.cpp\")", 
				"set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY \${CMAKE_BINARY_DIR}/../lib)",
				"set(CMAKE_LIBRARY_OUTPUT_DIRECTORY \${CMAKE_BINARY_DIR}/../lib)",
				"set(CMAKE_RUNTIME_OUTPUT_DIRECTORY \${CMAKE_BINARY_DIR}/../bin)"
			]

	regex = b"(\d+\.)?(\d+\.)?(\*|\d+)"
	output = subprocess.check_output("cmake -version", shell=True)
	version = re.search(regex, output).group(0)

	cmakev = "cmake_minimum_required(VERSION {})".format(version)
	project = "project({})".format(proj)
	execu = "add_executable({} \${{SOURCES}})".format(proj.lower())

	os.system("echo \"{}\" > {}/CMakeLists.txt".format(cmakev,proj))
	os.system("echo \"{}\" >> {}/CMakeLists.txt".format(project,proj))

	os.system("echo \"{}\" >> {}/CMakeLists.txt".format("\n".join(stdfill),proj))

	os.system("echo \"{}\" >> {}/CMakeLists.txt".format(execu,proj))


