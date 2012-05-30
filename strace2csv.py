#!/usr/bin/python

#
# pystrace -- Python tools for parsing and analysing strace output files
#
#
# Copyright 2012
#      The President and Fellows of Harvard College.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 3. Neither the name of the University nor the names of its contributors
#    may be used to endorse or promote products derived from this software
#    without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE UNIVERSITY AND CONTRIBUTORS ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE UNIVERSITY OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.
#
#
# Contributor(s):
#   Peter Macko (http://eecs.harvard.edu/~pmacko)
#

import getopt
import os.path
import sys

import strace


#
# Escape a string
#
def escape(s, quote='"'):
	'''
	Escape a string
	'''
	r = ""
	if s is None: return ""
	if type(s) == int: return str(s)
	if type(s) == float: return str(s)
	for c in str(s):
		if c == quote: r += quote
		r += c
	return quote + r + quote


#
# Return an escaped string from the string array
#
def str_array_get_and_escape(array, index):
	'''
	Return an escaped string from the string array
	'''

	if index < len(array):
		s = array[index]
		return escape(s)
	else:
		return ""


#
# Convert to a .csv
#
def convert2csv(input_file, output_file=None, separator=','):
	'''
	Convert to a .csv
	
	Arguments:
	  input_file  - the input file, or None for standard input
	  output_file - the output file, or None for standard output
	  separator   - the separator
	'''

	# Open the files
	
	if input_file is not None:
		f_in = open(input_file, "r")
	else:
		f_in = sys.stdin
	
	if output_file is not None:
		f_out = open(output_file, "w")
	else:
		f_out = sys.stdout
	
	
	# Process the file
	
	strace_stream = strace.StraceInputStream(f_in)
	first = True
	
	for entry in strace_stream:
		
		if first:
			first = False
			if strace_stream.have_pids:
				f_out.write("PID%s" % separator)
			f_out.write(("TIMESTAMP%sSYSCALL%sSPLIT%sARGC%sARG1%sARG2%sARG3" \
					+ "%sARG4%sARG5%sARG6%sRESULT%sELAPSED\n")
				% (separator, separator, separator, separator, separator, \
						separator, separator, separator, separator, separator,\
						separator))
		
		
		# Print
		
		if entry.was_unfinished:
			s_was_unfinished = "1"
		else:
			s_was_unfinished = "0"
		if entry.elapsed_time is not None:
			s_elapsed_time = "%0.6f" % entry.elapsed_time
		else:
			s_elapsed_time = ""
		
		if strace_stream.have_pids:
			f_out.write("%d%s" % (entry.pid, separator))
		f_out.write("%0.6f%s\"%s\"%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s%s\n"
			% (entry.timestamp, separator, entry.syscall_name, separator,
			   s_was_unfinished, separator,
			   len(entry.syscall_arguments), separator,
			   str_array_get_and_escape(entry.syscall_arguments, 0), separator,
			   str_array_get_and_escape(entry.syscall_arguments, 1), separator,
			   str_array_get_and_escape(entry.syscall_arguments, 2), separator,
			   str_array_get_and_escape(entry.syscall_arguments, 3), separator,
			   str_array_get_and_escape(entry.syscall_arguments, 4), separator,
			   str_array_get_and_escape(entry.syscall_arguments, 5), separator,
			   escape(entry.return_value), separator, s_elapsed_time))


	# Close the files

	if f_out is not sys.stdout:
		f_out.close()
	strace_stream.close()


#
# Print the usage information
#
def usage():
	sys.stderr.write('Usage: %s [OPTIONS] [FILE]\n\n'
		% os.path.basename(sys.argv[0]))
	sys.stderr.write('Options:\n')
	sys.stderr.write('  -h, --help         Print this help message and exit\n')
	sys.stderr.write('  -o, --output FILE  Print to file instead of the standard output\n')


#
# The main function
#
# Arguments:
#   argv - the list of command-line arguments, excluding the executable name
#
def main(argv):

	input_file = None
	output_file = None
	

	# Parse the command-line options

	try:
		options, remainder = getopt.gnu_getopt(argv, 'ho:',
			['help', 'output='])
		
		for opt, arg in options:
			if opt in ('-h', '--help'):
				usage()
				return
			elif opt in ('-o', '--output'):
				output_file = arg
		
		if len(remainder) > 1:
			raise Exception("Too many options")
		elif len(remainder) == 1:
			input_file = remainder[0]
	except Exception as e:
		sys.stderr.write("%s: %s\n" % (os.path.basename(sys.argv[0]), e))
		sys.exit(1)
	
	
	# Convert to .csv

	try:
		convert2csv(input_file, output_file)
	except IOError as e:
		sys.stderr.write("%s: %s\n" % (os.path.basename(sys.argv[0]), e))
		sys.exit(1)


#
# Entry point to the application
#
if __name__ == "__main__":
	main(sys.argv[1:])
