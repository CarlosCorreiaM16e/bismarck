#! /usr/bin/python

#----------------------------------------------------------------------
def read_file_as_lines( filename ):
    f = open( filename, "r" )
    lines = f.readlines()
    f.close()
    return lines

#----------------------------------------------------------------------
