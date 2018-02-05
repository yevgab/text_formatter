# Project: Text Formatter, task from Charles Wetherell book
#
# https://github.com/yevgab/text_formatter.git
#
# dr.doberman, EnesGUL, Faf_Faf, yevgab
#
"""
tf is the main module that manages the application
"""

import argparse
import sys
import codecs
import re

class TextFormat():
    def __init__(self):
        self.w = 72
        self.h = 40
        self.left = self.h
    
    def ProcessLine(self, line):
        line = self.RemoveCRLF(line)
        if re.match("^\?\w+\ +.*", line) != None:
            self.ProcessCommand(line)
        else:
            print(line)
            self.left -= 1
            if self.left == 0:
                print('\f')
                self.left = self.h

    def RemoveCRLF(self, line):
        pos = line.find('\n')
        if pos != -1:
            line = line[:pos]
        pos = line.find('\r')
        if pos != -1:
            line = line[:pos]
        return line
    
    def ProcessCommand(self, line):
        m = re.match("^\?(\w+)\ +.*", line)
        if m != None:
            cmd = m.group(1)
            if cmd == "align":
                self.CmdAlign(line)
            elif cmd == "size":
                self.CmdSize(line)
            elif cmd == 
        else:
            cmd = "Unknown Command"
        print("Command found:", cmd)

    def CmdAlign(self, line):
        pass




    




def main():
    """ Application entry point """
    parser = argparse.ArgumentParser()
    parser.add_argument("-f")
    args = parser.parse_args()
    if args.f != None:
        try: 
            inf = open(args.f, encoding = "UTF8")
        except OSError as err:
            print("Could not open file", args.f, "due to", err)
            sys.exit(1)
    else:
        inf = sys.stdin
    
    tf = TextFormat() 

    for l in inf:
        tf.ProcessLine(l)



main()
