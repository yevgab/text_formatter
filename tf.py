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
import random

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
        self.align = A_FILL
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
        if re.match(r"^\?\w+\ +.*", line) != None:
            self.ProcessCommand(line)
        else:
            self.FormatLine(line)
            if self.left == 0:
                self.PageClose()

    def FormatLine(self, line):
        if self.fn_lines > 0:
            self.FormatFNLine(line)
            self.fn_lines -= 1
            return
        if self.align == A_AS_IS:
            self.PrintLine(line, False)
            return

        line = line.strip()
        if line == "":
            self.Flush()
            return

        line = self.prev_line + ' ' + line
        cw = self.w - self.offset[0] - self.offset[1]
        if self.first_line:
            cw += self.indent
       
        while len(line) >= cw:
            s, line = self.LineCut(line, cw)
            if s == "":
                self.PrintLine(line, False)
                break
            # Отформатировать строку в соответствии с текущими 
            # настройками выравнивания
            s = self.LineAlign(s, cw)
            # Вывести строку в стандартный вывод
            self.first_line = False
            cw = self.w - self.offset[0] - self.offset[1]
            self.PrintLine(s)

        else:
            self.prev_line = line

    def PrintLine(self, line, add_interval = True):
        if self.left == 0:
            self.PageClose()

        print(line)
        self.left -= 1
        if add_interval:
            for l in range(self.interval - 1):
                if self.left > 0:
                    print("")
                    self.left -= 1

    def PrintErr(self, line):
        print(line)

    def PrintSym(self, sym):
        print(sym)

    def LineAlign(self, s, normal_str = True):
        if normal_str:
            ln = self.w - self.offset[0] - self.offset[1]
            if self.first_line:
                ln -= self.indent
        else:
            # TODO: calculate ln for footnotes (flag normal_str as false)
            pass

        if self.align == A_RIGHT:
            s = s.rjust(ln)

        elif self.align == A_CENTER:
            s = s.center(ln)

        elif self.align == A_FILL:
            # Разбить строку на слова
            ww = s.split()
            # Посчитать суммарную длину всех слов
            wln = 0
            for w in ww:
                wln += len(w)
            # Определить минимальное количество пробелов в строке
            min_s = int((ln - wln) / (len(ww) - 1))
            # Расставить в случайные позиции оставшиеся пробелы
            sp = ln - wln - min_s * (len(ww) - 1)
            spp = set()
            while sp > 0:
                sppl = len(spp)
                spp.add(random.randint(0, len(ww) - 2))
                if len(spp) > sppl:
                    sp -= 1
            s = ww[0]
            for p, w in enumerate(ww[1:]):
                if p in spp:
                    s += " "
                s += w.rjust(len(w) + min_s)


        if normal_str:
            s = s.ljust(ln + self.offset[1])
            if self.first_line:
                s = s.rjust(ln + self.offset[0] + self.indent)
            else:
                s = s.rjust(ln + self.offset[0])
                
        return s

    def Offset(self, s):
        if self.offset[0] != 0:
            s = " " * self.offset[0] + s
        if self.offset[1] != 0:
            s += " " * self.offset[1]

    def Interval(self, s):
        s += "\n" * (self.interval - 1) 

    def LineCut(self, line, cw):
        # Отрезать от строки подстроку шириной не более текущей ширины
        # параграфа по пробелам
        
        last_space = line.rfind(' ', 0, cw)
        if last_space >= 0:
            s = line[:last_space]
            line = line[last_space + 1:]
        else:
            s = ""

        return s, line
              
    def FormatFNLine(self, line):
        pass

    def PageInit(self):
        pass

    def PageClose(self, not_start_new_page = False):
        self.PrintSym('\f')
        self.left = self.h
        if not not_start_new_page:
            self.PageInit()
        

    def RemoveCRLF(self, line):
        pos = line.find('\n')
        if pos != -1:
            line = line[:pos]
        pos = line.find('\r')
        if pos != -1:
            line = line[:pos]
        return line

    def Flush(self, close_document = False):
        if self.left - (self.interval - 1) == 0:
            self.PageClose()

        if self.align == A_CENTER or self.align == A_RIGHT:
            self.PrintLine(self.LineAlign(self.prev_line))
        else:
            self.PrintLine(self.prev_line)
        
        self.prev_line = ""
        self.first_line = True

        if close_document:
            self.PrintFNotes()

    def PrintFNotes(self):
        pass
        
    def ProcessCommand(self, line):
        m = re.match(r"^\?(\w+)\ +.*", line)
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
            self.PrintErr("Unknown command: " + cmd)
        
    def CmdSize(self, line):
        pass
    
    def CmdAlign(self, line):
        m = re.match(r"^\?align\ +(left|right|center|fill|as_is){1}", line)
        if m != None:
            align = m.group(1)
            if align == "left":
                self.Flush()
                self.align = A_LEFT
            elif align == "right":
                self.Flush()
                self.align = A_RIGHT
            elif align == "center":
                self.Flush()
                self.align = A_CENTER
            elif align == "fill":
                self.Flush()
                self.align = A_FILL
            elif align == "as_is":
                self.Flush()
                self.align = A_AS_IS          
        else:
            self.PrintErr("Invalid align type: " + line)

    def CmdPar(self, line):
        pass

    def CmdOffset(self, line):
        m = re.match(r"^\?offset\ + \d", line)
        n = re.match(r"^\?offset\ + \,\ + \d", line)
        if m != None:
            self.offset[0] = int(m.group(1))
            #kill me please
            #tried converting to the string of having variables assigned
            #doesn't work
            self.Flush
            self.Offset
        if n != None:
            self.offset[1] = int(n.group(1))
            #same for this one
            self.Flush
            self.Offset

    def CmdInterval(self, line):
        m = re.match(r"^\?interval\ +\d{1}", line)
        self.interval = m.group(1)
        if m != None:
            self.Flush
            self.Interval

    def CmdFeed(self, line):
        pass

    def CmdFeedLines(self, line):
        pass

    def CmdPageBreak(self, line):
        self.PageClose()

    def CmdLeft(self, line):
        self.Flush()
        m = re.match(r"^\?left\ +(\d+){1}", line)
        if m != None:
            try:
                ll = int(m.group(1))
            except ValueError as err:
                self.PrintErr("Invalid left parameter in command [" + line
                    + "] :" + err)
                return
            if ll > self.left:
                self.PageClose()
        else:
            self.PrintErr("Invalid left command: " + line)

    def CmdHeader(self, line):
        pass

    def CmdPNum(self, line):
        pass

    def CmdBr(self, line):
        self.Flush()

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
    
    tf.Flush()



main()