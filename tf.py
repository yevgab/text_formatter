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

# fill|left|right|center|as_is
A_FILL   = 0
A_LEFT   = 1
A_RIGHT  = 2
A_CENTER = 3
A_AS_IS  = 4

# left|right|center|smart, top|bottom
H_LEFT   = 0
H_RIGHT  = 1
H_CENTER = 2
H_SMART  = 3
H_TOP    = 4
H_BOTTOM = 5
H_NONE   = -1

# arabic|roman|letter
PNUM_ARABIC = 0
PNUM_ROMAN  = 1
PNUM_LETTER = 2




class TextFormat():
    def __init__(self, w = 72, h = 40):
        self.w = w
        self.h = h
        self.left = self.h
        self.align = A_LEFT
        self.header_pos = H_NONE
        self.indent = 0
        self.offset = (0, 0)
        self.space = (0, 0)
        self.interval = 1
        self.pnum_type = PNUM_ARABIC
        self.pnum = 1
        self.pnum_prefix = ""
        self.prev_line = ""
        self.first_line = True
        self.fn_lines = 0
        self.fn_w = self.w
        self.fn = []

    def ProcessLine(self, line):
        line = self.RemoveCRLF(line)
        if re.match("^\?\w+\ +.*", line) != None:
            self.ProcessCommand(line)
        else:
            self.FormatLine(line)
            if self.left == 0:
                self.PageClose()

    def FormatLine(self, line):
        if self.fn_lines > 0:
            self.FormatFNLine(line)
            self.fn_line -= 1
            return
        if self.align == A_AS_IS:
            print(line)
            self.left -= 1
            return
        line = self.prev_line + ' ' + line
        if self.first_line:
            ind = self.indent
        else:
            ind = 0
        cw = self.w - self.offset[0] - self.offset[1] - ind
        while len(line) >= cw:
            s, line = self.LineCut(line, cw)
            if s == "":
                print(line)
                break
            # Отформатировать строку в соответствии с текущими 
            # настройками выравнивания
            s = self.LineAlign(s)
            # Вывести строку в стандартный вывод
            print(s)

    def LineAlign(self, s):
        return s

    def LineCut(self, line, cw):
        # Отрезать от строки подстроку шириной не более текущей ширины
        # параграфа по пробелам
        
        last_space = line.rfind(' ', 0, cw)
        if last_space >= 0:
            s = line[:last_space]
            line = line[last_space:]
        else:
            s = ""

        return s, line
              
    def FormatFNLine(self, line):
        pass

    def PageInit(self):
        pass

    def PageClose(self):
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
            if cmd == "size":
                self.CmdSize(line)
            elif cmd == "align":
                self.CmdAlign(line)
            elif cmd == "par":
                self.CmdPar(line)
            elif cmd == "offset":
                self.CmdOffset(line)
            elif cmd == "interval":
                self.CmdInterval(line)
            elif cmd == "feed":
                self.CmdFeed(line)
            elif cmd == "feed_lines":
                self.CmdFeedLines(line)
            elif cmd == "page_break":
                self.CmdPageBreak(line)
            elif cmd == "left":
                self.CmdLeft(line)
            elif cmd == "header":
                self.CmdHeader(line)
            elif cmd == "p_num":
                self.CmdPNum(line)
            elif cmd == "br":
                self.CmdBr(line)
            elif cmd == "footnote":
                self.CmdFootnote(line)
            elif cmd == "alias":
                self.CmdAlias(line)
                
        else:
            cmd = "Unknown Command"
        print("Command found:", cmd)

        
    def CmdSize(self, line):
        pass
    
    def CmdAlign(self, line):
        pass

    def CmdPar(self, line):
        pass

    def CmdOffset(self, line):
        pass

    def CmdInterval(self, line):
        pass

    def CmdFeed(self, line):
        pass

    def CmdFeedLines(self, line):
        pass

    def CmdPageBreak(self, line):
        pass

    def CmdLeft(self, line):
        pass

    def CmdHeader(self, line):
        pass

    def CmdPNum(self, line):
        pass

    def CmdBr(self, line):
        pass

    def CmdFootnote(self, line):
        pass

    def CmdAlias(self, line):
        pass  



def main():
    """ Application entry point """
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", help = "File to process. If empty stdin will be used.")
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
