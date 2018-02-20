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
HV_TOP    = 4
HV_BOTTOM = 5
H_NONE   = -1

# arabic|roman|letter
PNUM_ARABIC = 0
PNUM_ROMAN  = 1
PNUM_LETTER = 2

MIN_PAGE_SIZE = (20, 20) # h, w




class TextFormat():
    def __init__(self, w = 72, h = 40):
        self.w = w
        self.h = h
        self.left = self.h
        self.align = A_LEFT
        self.header_hpos = H_NONE
        self.header_vpos = H_NONE
        self.header_h = 0
        # header_pos determines the line from header_h in which the header 
        # will be displayed
        self.header_pos = 0
        self.header_text = ""
        self.indent = 0
        self.offset = (0, 0)
        self.space = 0
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

        if self.prev_line != "":
            line = self.prev_line + ' ' + line 
        cw = self.w - self.offset[0] - self.offset[1]
        if self.first_line:
        #    self.FeedLines(self.space)
            cw -= self.indent
       
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
        print("")
        print("  >>> ERROR: " + line)
        print("")

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
            if len(ww) > 1:
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

    def HeaderForm(self):
        if self.header_hpos == H_NONE or self.header_h == 0:
            return
        
        if self.header_vpos == HV_BOTTOM:
            print("="*self.w)

        if self.header_text != "":
            h = self.header_text + " "
        else:
            h = ""

        h += self.GetPNum()

        if self.header_hpos == H_RIGHT:
            h = h.rjust(self.w)
        elif self.header_hpos == H_CENTER:
            h = h.center(self.w)
        elif self.header_hpos == H_SMART:
            if self.pnum % 2 == 0:
                h = h.rjust(self.w)
        
        for i in range(self.header_h):
            if i + 1 == self.header_pos:
                print(h)
            else:
                print("")
        
        if self.header_vpos == HV_TOP:
            print("="*self.w)
        

        
    def GetPNum(self):
        return str(self.pnum)
        

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
        self.left = self.h - self.header_h - 1
        if self.header_vpos == HV_BOTTOM:
            self.HeaderForm()
        self.pnum += 1
        if not not_start_new_page:
            if self.header_vpos == HV_TOP:
                self.HeaderForm()
            self.PageInit()
        

    def RemoveCRLF(self, line):
        pos = line.find('\n')
        if pos != -1:
            line = line[:pos]
        pos = line.find('\r')
        if pos != -1:
            line = line[:pos]
        return line

    def FeedLines(self, n, add_interval = True):
        for i in range(n):
            if self.left > 0:
                self.PrintLine("", False)
            if add_interval and self.left > 0:
                self.PrintLine("")

    def Flush(self, close_document = False):
        if self.left == 0:
            self.PageClose()

        self.PrintLine(self.LineAlign(self.prev_line))
        
        self.prev_line = ""
        self.FeedLines(self.space)
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
        m = re.match(r"^\?size\ +(\d+)?,\ *(\d+)?", line)
        if m != None:
            if m.group(1) != None:
                h = int(m.group(1))
                if h < MIN_PAGE_SIZE[0]:
                    self.PrintErr("Page height coudn't be less than " + str(MIN_PAGE_SIZE[0]))
                    h = self.h
            else:
                h = self.h
            if m.group(2) != None:
                w = int(m.group(2))
                if w < MIN_PAGE_SIZE[1]:
                    self.PrintErr("Page width coudn't be less than " + str(MIN_PAGE_SIZE[1]))
                    w = self.w
            else:
                w = self.w
            if self.left > 0:
                self.Flush()
                flushed = True
            else:
                flushed = False
            # Сравнить новые размеры с текущими размерами
            # Если новые размеры меньше чем текущие,
            if h < self.h or w < self.w:
                # то закрываем абзац, если есть свободное место
                # и закрываем страницу, и открывем новую.
                self.PageClose(False)
                self.h, self.w = h, w
                self.PageInit()
            else:
                self.h, self.w = h, w
            if not flushed:
                self.Flush()
        else:
            self.PrintErr("Invalid size command: " + line)
    
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
        m = re.match(r"^\?par\ +(\d+)?,\ *(-?\d+)?", line)
        if m != None:
            self.Flush()
            if m.group(1) != None:
                sp = int(m.group(1))
                if sp >= 0 and sp <= int(self.h/2):
                    self.space = sp
            if m.group(2) != None:
                ind = int(m.group(2))
                if (ind >= 0 and ind <= int(self.w/6)) or (ind < 0 and abs(ind) <= self.offset[0]):
                    self.indent = ind
            #needs fixing 
            #indent is not stable across lines


    def CmdOffset(self, line):
        m = re.match(r"^\?offset\ +(\d+)?,\ *(\d+)?", line)
        if m != None:
            self.Flush()
            if m.group(1) != None:
                try:
                    off = int(m.group(1))
                    if off >= 0 and off < int(self.w / 3):
                        self.offset = (off, self.offset[1])
                except ValueError as err:
                    self.PrintErr("Invalid left offset value " + m.group(1) +" : " + err)
            if m.group(2) != None:
                try:
                    off = int(m.group(2))
                    if off >= 0 and off < int(self.w / 3):
                        self.offset = (self.offset[0], off)
                except ValueError as err:
                    self.PrintErr("Invalid right offset value " + m.group(1) + " : " + err)
        else:
            self.PrintErr("Invalid offset command [" + line + "]")

    def CmdInterval(self, line):
        m = re.match(r"^\?interval\ +(\d+){1}", line)
        if m != None:
            try:
                newInt = int(m.group(1))
            except ValueError as err:
                self.PrintErr("Could not get an interval parameter due to " + err)
                return
            self.Flush()
            if newInt >= 0 and newInt != self.interval:
                self.interval = newInt
        else:
            self.PrintErr("Invalid interval command [" + line + "]")

    def CmdFeed(self, line):
        m = re.match(r"^\?feed\ +(\d+){1}", line)
        if m != None:
            try:
                n = int(m.group(1))
            except ValueError as err:
                self.PrintErr("Could not get a feed parameter due to " + err)
                return
            self.Flush()
            if n >= 0 and n < int(self.h/3):
                self.FeedLines(n)
        else:
            self.PrintErr("Invalid feed command [" + line + "]")

    def CmdFeedLines(self, line):
        m = re.match(r"^\?feed_lines\ +(\d+){1}", line)
        if m != None:
            try:
                n = int(m.group(1))
            except ValueError as err:
                self.PrintErr("Could not get a feed lines parameter due to " + err)
                return
            self.Flush()
            if n >= 0 and n < int(self.h/3):
                self.FeedLines(n, False)
        else:
            self.PrintErr("Invalid feed lines command [" + line + "]")

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
        m = re.match(r"^\?header\ +(\d+){1},\ *(\d+){1},\ *(left|right|center|smart){1},\ *(top|bottom){1},\ *(.*)", line)
        if m != None:
            try:
                hh = int(m.group(1))
                if hh <= 5:
                    self.header_h = hh
                else:
                    self.PrintErr("Header height is out of bounds")
            except ValueError as err:
                self.PrintErr("Could not get a header height parameter due to " + err)
                return

            try:
                hp = int(m.group(2))
                if hp >= 1 and hp <= self.header_h:
                    self.header_pos = hp
                else:
                    self.header_pos = 1
                    self.PrintErr("Your header position is outside of header boundaries")
            except ValueError as err:
                self.PrintErr("Could not get a header position hight parameter due to " + err)
                return

            self.header_text = m.group(5)
            if m.group(3) == "right":
                self.header_hpos = H_RIGHT
            elif m.group(3) == "center":
                self.header_hpos = H_CENTER
            elif m.group(3) == "smart":
                self.header_hpos = H_SMART
            elif m.group(3) == "left":
                self.header_hpos = H_LEFT

            if m.group(4) == "top":
                self.header_vpos = HV_TOP
            else:
                self.header_vpos = HV_BOTTOM
            
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