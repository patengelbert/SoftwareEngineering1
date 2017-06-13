# To change this template, choose Tools | Templates
# and open the template in the editor.

from Tkinter import *
import tkFont
from tkFileDialog import *
from tkMessageBox import *
import math
#from tkinter.ttk import *
# To change this template, choose Tools | Templates
# and open the template in the editor.

from collections import defaultdict



class Emulate:
    mem = defaultdict(int)
    acc = 0
    pc = 0
    mar = 0
    mdr = 0
    ir = 0
    isfetch = 1
    status = 0
    run_status = 0
    allradix = 10
    membutton=0

    codes = {0:'LDA',1:'STA',2:'ADD',3:'SUB',4:'JMP',5:'JGE',6: 'JNE',7:'STP',
        8:'XXX',9:'XXX',10:'XXX',11:'XXX',12:'XXX',13:'XXX',14:'XXX',15:'STP'}
    funcs = {0: (lambda x:x.ldax), 1:(lambda x:x.stax), 2:lambda x:x.addx,
        3:lambda x:x.subx, 15:lambda x:x.nop, 7:lambda x:x.nop}
    jump_list = {'JMP': (lambda a: 1),'JNE':(lambda a: a!=0),'JEQ':(lambda a: a==0),
        'JGE':(lambda a: a >= 0)}

    def changeallradix(self):
        self.allradix = self.mem[0].Radixes[self.allradix]
        self.membutton['text']= self.mem[0].Rdisp[(self.allradix)]
        for i in self.mem:
            self.mem[i].radix = self.allradix
            self.mem[i].update()

    def nop(self,operand):
        pass


    def ldax(self,operand):
        self.check_operand(operand)
        self.set_mar(operand)
        self.acc.change(self.mem[operand].value)

    def stax(self,operand):
        self.check_operand(operand)
        self.set_mar(operand)
        self.mem[operand].change(self.acc.value)


    def addx(self,operand):
        self.check_operand(operand)
        self.set_mar(operand)
        self.acc.change(self.acc.value+self.mem[operand].value)

    def subx(self,operand):
        self.check_operand(operand)
        self.set_mar(operand)
        self.acc.change(self.acc.value-self.mem[operand].value)

    def check_operand(self,operand):
        if operand not in self.mem:
            print "Error: "+str(operand)+" is not a valid memory address."
            exit()

    def operand(self):
        return self.ir.value & 0xfff

    def opcode(self):
        return self.ir.value // 2**12

    def mnemonic(self):
        return self.codes[self.ir.value // 2**12]

    def fetch(self):
        self.set_mar(self.pc.value)
        self.update_status();
        self.ir.change(self.mem[self.mar].value)
        if self.mnemonic()=="STP":
            self.run_status = 0 # STP instruction
            self.isfetch = 1
            return
        if self.mnemonic() in self.jump_list: # jump instr
            if self.jump_list[self.mnemonic()](self.acc.value):
                self.pc.change(self.operand()) # if condition is TRUE
                self.isfetch = 1
            else:
                self.pc.change((self.pc.value+1) % (2**16))
                self.isfetch = 1
        else:
            self.pc.change((self.pc.value+1) % (2**16))
            self.isfetch = 0

    def update_status(self):
        if self.isfetch:
            self.status["text"]="FETCH Completed"
        else:
            self.status["text"]="EXECUTE Completed"

    def execute(self):
        self.update_status()
        self.funcs[self.opcode()](self)(self.operand())
        self.isfetch = 1

    def cycle(self):
        if self.isfetch:
            self.fetch()
        else:
            self.execute()

    def instr(self):
        self.cycle()
        if not self.isfetch:
            self.cycle()

    def auto_start(self):
        self.run_status=1
        self.auto()

    def auto(self):
        self.cycle()
        if self.run_status:
            autobutton.after(500,self.auto)

    def stop(self):
        self.run_status = 0

    def set_mar(self, addr):
        self.mem[self.mar].frame['background']='white'
        self.mar = addr
        self.mem[self.mar].frame['background'] = 'yellow'


emu = Emulate()
nnn=0





class regbox:
    Radixes = {10:16,16:8,8:2,2:0,0:10}

    Rtype = {10:'d',16:'X',8:'o',2:'b'}

    Rlength = {10:'5',16:'04',8:'06',2:'016'}

    Rdisp = {10:'dec',16:'hex',8:'oct',2:'bin',0:'asm'}

    Codes_inv = {}

    for (a,h) in  Emulate.codes.items():
        Codes_inv[h] = a

    def lookup(self,op,operand):
        x = operand.strip('&')
        if op not in self.Codes_inv:
            return (0,1)
        return (self.Codes_inv[op]*2**12+(int(x,16) % 2**12)),0

    def parse(self,str,radix):
        w = str.split()
        if len(w) == 2 and self.radix == 0:
            return self.lookup(w[0],w[1])
        elif radix == 0:
            return (0,1)
        elif len(w) != 1:
            return (0,1)
        else:
            return int(w[0],self.radix) % 2**16,0


    def changeradix(self):
        self.radix = self.Radixes[self.radix]
        self.update()

    def update(self):
        if self.radix == 0:
            s = Emulate.codes[self.value // 2**12]+ " &" + '{0:03X}'.format(
                                                    self.value & 0xfff)
        else:
            wspec = self.Rlength[self.radix]
            s = ('{0:'+wspec+self.Rtype[self.radix]+'}').format(self.value)
        self.textvalue.set(s)
        self.button['text']= self.Rdisp[(self.radix)]

    def change(self,value):
        self.value=value
        self.update()



    def change_value(self, *dummy):
        s = self.textvalue.get()
        (v,err) = self.parse(s,self.radix)
        if err:
            pass
        else:
            self.value = v
            self.update()

    def __init__(self,parent,name,radix):
        self.textvalue = ''
        self.frame = LabelFrame(parent,borderwidth=4, text=name, relief='solid')
        self.button=Button( self.frame,text=self.Rdisp[radix],
            command=self.changeradix,width=0)
        self.textvalue = StringVar()
        self.box = Entry(self.frame,width=16,foreground='blue',textvariable=self.textvalue)
        self.box['font']='-size 8'
        self.radix = radix
        global nnn
        self.value=0
        self.name=name
        self.textvalue.trace('w',self.change_value)
        self.update()
        self.box.grid(column=1,row=0)
        self.button.grid(column=0,row=0)


def arithhelp():
    top = Toplevel()
    top.title("About this application...")
    txt = Text(top, wrap='word')
    txt.insert('1.0',"""
This application illustrates addition in binary (bin), \
hexadecimal (hex), and decimal (dec).

Each number is displayed simultaneously in all three representations.

Each hexadecimal digit is displayed above the \
4 binary digits which correspond.

Note that leading zeros do not alter the value of a number and are optional.

Click on any digit to change its value - this will change all three \
representations of the number and also the result.

The signed/unsigned button determines whether the bit pattern is \
interpreted as an unsigned or 2's complement signed number. This changes \
the decimal display but not the binary or hex. Signed and unsigned are two \
different interpretations of the same machine number. Click on the sign \
or space one position to the left of the decimal number to negate the number \
in signed mode only.

The 32 bit/16 bit/8 bit button alters the machine size of the number. \
Smaller sizes will sign extend to larger only if in signed mode. The number \
will be truncated (with posible change of sign in signed mode) if moved from \
larger to smaller size.

Note that addition is identical whether the number is interpreted signed or \
unsigned, and results in the correct signed or unsigned answer unless there \
is overflow.

The decimal result will be coloured red on overflow.
""")
    txt.pack()

    button = Button(top, text="OK", command=top.destroy)
    button.pack()




class machine_number:
    def __init__(self,fr, num,row,col,sign=0,ro=0, bits=32):
        assert num >= 0 and num < 2**32
        self.n = num
        self.row=row
        self.col=col
        self.fr=fr
        self.ro=ro
        self.sign = sign
        self.bits=bits
        self.disp(1)

    def readsigned(self):
        if self.sign and self.n >= 2**(self.bits-1):
            return self.n - 2**self.bits
        else:
            return self.n

    def setbits(self,bits):
        self.n = self.readsigned() & (2**bits-1)
        self.bits = bits
        self.disp()


    def update(self,width,bit, x):
        assert bit >= 0 and bit <=self.bits-1 and width>=0 and width+bit<=self.bits
        if width:
            mask = (2**(width)-1) << bit
            self.n = self.n & (mask^(2**self.bits-1))
            self.n = self.n | (x << bit)
        else: #radix = 10, special case
            decade = 10**bit
            dig = (self.n // decade)%10
            self.n += (x-dig)*decade

    def change(self,d,i,radix):
        if d == '+' and self.readsigned() < 0:
            self.n = 2**self.bits - self.n
        if d == '-' and self.readsigned > 0:
            self.n = 2**self.bits - self.n
        if d in range(16):
            invert = 0
            if radix == 10 and self.readsigned() < 0:
                invert = 1
                self.n = 2**self.bits - self.n
            wd = {2:1,8:3,16:4,10:0}
            self.update(wd[radix],i,d)
            if invert:
                self.n = 2**self.bits - self.n
        self.n = self.n & (2**self.bits-1)
        propagate()
        self.disp()

    def read(self):
        return self.n

    def disp(self,init=0):
        row=self.row
        col=self.col
        dradix(self.fr,2,row+1,col+32,1,self,init)
        if init:
            Label(self.fr,text="      ").grid(row=row,column=col+33)
        dradix(self.fr,16,row,col+32,4,self,init)
        if init:
            Label(self.fr,text="      ").grid(row=row,column=col+43)
        dradix(self.fr,-10 if self.sign else 10,row,col+55,1,self,init)

    def setcolour(self,colour):
        for i in range(56-11,56):
            tb = list(self.fr.grid_slaves(row=self.row,column=self.col+i))
            assert len(tb)==1
            tb=tb[0]
            tb['foreground']=colour

def setbits(bits):
    m1.setbits(bits)
    m2.setbits(bits)
    m3.setbits(bits)



def memarray(frame,top, bottom, radix):
    subf = Frame(frame)
    for i in range(top, bottom):
        emu.mem[i] = regbox(subf,"MEM["+str(i)+"]",radix)
        emu.mem[i].frame.grid(row=i%10,column=1+i//10,padx=2,pady=1)
    emu.membutton = Button(subf,text=regbox.Rdisp[radix],
            command=emu.changeallradix,width=0)
    emu.membutton.grid(row=bottom+1, column=1,columnspan=2)
    emu.max_mem = bottom
    return subf


def cpu(frame):
    cpu = LabelFrame(frame,borderwidth=4, text='CPU',relief='solid', padx=4,pady=10)
    emu.acc = regbox(cpu,"ACC",10)
    emu.acc.frame.grid(row=2,column=1)
    emu.pc = regbox(cpu,"PC",16)
    emu.ir = regbox(cpu,"IR",0)
    emu.pc.frame.grid(row=1,column=1,pady=20,padx=10)
    emu.ir.frame.grid(row=1,column=2,rowspan=3,padx=20)
    fill(cpu,10,10).grid(row=3,column=1)
    Label(cpu, text='ALU',font='-size 20',relief='solid',borderwidth=4,pady=5).grid(padx=10,row=5,
                                    column=1,columnspan=2,ipadx=10,ipady=10)
    return cpu

def fill(frame, x, y):
    return Canvas(frame, width=y,height=x)

class ParseError(Exception):
    pass


def loadfile():
    try:
        fn = askopenfilename()
        f = open(fn)
        mlist = f.readlines()
        for m in mlist:
            x = m.split()
            if len(x) != 2:
                print "Error in line:",m
                raise ParseError
            else:
                addr = int(x[0],16)
                data = int(x[1],16)
                if addr > emu.max_mem:
                    print "Error: data location ",addr," is larger than max value of ",max_mem
                    raise Exception
                if data >= 2**16:
                    print "Error: data location ",addr," is larger than &FFFF"
                    raise Exception
            emu.mem[addr].change(data)
            emu.pc.change(0)
            emu.acc.change(0)
            emu.status[text]='Starting...]'
    except ParseError:
        print "Error in file parsing"
    except Exception:
        print "Unknown error in file loading"

def set_digit(fr,e,numb,radix,i):
    assert i <= 31 and i >= 0
    xv = 0
    yv = 0
    if numb.ro: return
    mb = Menubutton(fr)
    men = Menu(mb,tearoff=0)
    if i == 10 and radix == 10:
         men.add_command ( label = '+',
                            command=lambda:numb.change('+',i,radix) )
         if numb.sign:
            men.add_command ( label = '-',
                                command=lambda:numb.change('-',i,radix) )
    else:
        for d in range(radix):
            men.add_command ( label = digtostr(d),
                            command=lambda d=d:numb.change(d,i,radix) )
    men.post(x=e.x_root,y=e.y_root)

def digtostr(dig):
    tr = {10:'A',11:'B',12:'C',13:'D',14:'E',15:'F'}
    assert dig >= 0 and dig < 16
    if dig in tr:
        return tr[dig]
    else:
        return str(dig)

def dradix(fr,radix,row,col,sep,numb,init):
    i=0
    sign = 0
    n = numb.read()
    if radix == -10:
        radix = 10
        if n >= 2**(numb.bits-1):
            n = 2**numb.bits - n
            sign = 1
    while i < 11 or ((radix !=10) and (i < 32)) :
        dig = n % radix
        n = n // radix
        dig = digtostr(dig)
        for j in range(sep):
            if i+j==10 and radix == 10:
                dig = '-' if sign else ' '
            if i+j >= numb.bits and radix != 10:
                dig = ' '
            if init:
                w = 3 if ((i+j) % 4) == 3 else 1
                w = 1 if radix == 10 else w
                tb = Label(fr,text=dig if j==0 or dig==' ' else '-',width=w,anchor='e', font=fr.customFont)
                tb.grid(row=row,column=col-i-j,sticky='e')
            else:
                tb = list(fr.grid_slaves(row=row,column=int(col-i-j)))
                assert len(tb)==1
                tb=tb[0]
                tb['text']= dig if j==0 or dig == ' ' else '-'
            if j == 0:
                tb.bind("<Button-1>", lambda e,i=i: set_digit(fr,e,numb,radix,i))
        i+=sep
    if init:
        tb = Label(fr,text={2:'(bin)',16:'(hex)',10:'(dec)'}[radix],width=5,anchor='e')
        tb.grid(row=row,column=col-11 if radix==10 else col-32,sticky='e')



def gridpad(fr, r, c, width=0,height=0):
    Label(fr,text='',width=width,height=height).grid(row=r,column=c)

def propagate():
    m3.n = (m1.n+m2.n) % 2**m3.bits
    m3.disp()
    print m1.n,m2.n,m3.n
    print m1.readsigned(), m2.readsigned(),m3.readsigned()
    if m3.readsigned() != m1.readsigned()+m2.readsigned(): #overflow
        m3.setcolour('red')
    else:
        m3.setcolour('black')

def swapsign():
    x = 1-m3.sign
    m3.sign = x
    m2.sign = x
    m1.sign = x
    propagate()
    m1.disp()
    m2.disp()
    swapsign_button['text'] = 'Signed' if x else 'Unsigned'

def swapbits():
    sw = {32:16,16:8,8:32}
    setbits(sw[m3.bits])
    bits_button['text']=str(m1.bits)+ " bit"

def displaysum( sign):
    tk=Toplevel()
    tk.title("Binary and hexadecimal arithemetic demo for EE2/ISE1")
    tk.grid()
    DIGITFONT = tkFont.Font(family="Helvetica", size=16)
    global m1,m2,m3,swapsign_button,bits_button
    fr = Canvas(tk, relief='solid', borderwidth=0)
    fr.customFont = DIGITFONT
    fr.grid()
    m1=machine_number(fr,0x0,row=0,col=2,sign=0)
    gridpad(fr,2,0,1,1)
    Label(fr,text='+',font=fr.customFont).grid(row=2,column=40)
    m2=machine_number(fr,0x0,row=3,col=2,sign=0)
    gridpad(fr,5,0,2,2)
    Label(fr,text='=',font=fr.customFont).grid(row=5,column=40)
    m3=machine_number(fr,0x0,row=6,col=2,ro=1,sign=0)
    frb = Frame(fr,borderwidth=0)
    frb.grid(row=8,column=46,columnspan=10)
    Button(frb,text="Help",command=arithhelp).grid(row=0,column=0,pady=10)
    swapsign_button=Button(frb,text="Unsigned",command=swapsign, foreground='blue', width=8)
    bits_button=Button(frb,text=str(m1.bits)+" bit",command=swapbits, foreground='blue', width=8)
    bits_button.grid(row=0,column=1)
    swapsign_button.grid(row=0,column=2)
    Button(frb,text="Exit",command=tk.destroy, foreground='red').grid(row=0,column=3)
    tk.mainloop()

def im(markup):
    words = markup.split('[]')
    print words


def emuhelp():
    top = Toplevel()
    top.title("About this application...")
    txt = Text(top, wrap='word')
    txt.insert('1.0',"""
This application emulates MU0 execution, displaying memory & register contents.

The button in each register/memory box, and below all memory boxes, switches \
numeric display mode (hex/bin/dec). Display can also be in MU0 assembler (asm).

In each cycle the memory location being read or written is highlighted yellow.

Memory locations or registers can be changed by typing in boxes

Cycle - advance one cycle

Instr - advance one instruction

Auto - animate execution

Stop - stop animation

Load - load memory locations with program from text file and reset PC, ACC to 0

File format: each line contains memory address followed by memory contents. \
All numbers are written in hex, e.g.:
0 1234
1 7000
2 2001
""")
    txt.pack()

    button = Button(top, text="OK", command=top.destroy)
    button.pack()



def emulate(top, bottom):
    global autobutton,emu
    tk=Toplevel()
    tk.title("MU0 demo for EE2/ISE1")
    frame = Canvas(tk, relief='solid', borderwidth=0)
    frame.grid()
    frame.create_rectangle(0,0,450,800)
    cpu(frame).grid(column=1, row=1, rowspan=10)
    memarray(frame,top,bottom,16).grid(row=1,column=3,padx=20,pady=20)
    emu.status = Label(frame, text="Starting...")
    emu.status.grid(row=3,column=1)
    fill(frame,0,100).grid(column=2, row=1)
    Button(frame,text="Cycle",command=lambda : emu.cycle()).grid(row=4,column=0)
    Button(frame,text="Instr",command = lambda:emu.instr()).grid(row=5,column=0)
    autobutton = Button(frame,text="Auto",command=lambda : emu.auto_start())
    autobutton.grid(row=6,column=0)
    Button(frame,text="Stop",command=lambda : emu.stop()).grid(row=7,column=0)
    Button(frame,text="Exit",command=tk.destroy, foreground='red').grid(row=5,column=1)
    Button(frame,text="LOAD",command=loadfile, foreground='blue').grid(row=6,column=1)
    Button(frame,text="Help",command=emuhelp, foreground='green').grid(row=7,column=1)
    tk.mainloop

def gui():
    tk=Tk()
    top = Frame(tk, relief='solid')
    tk.title("Demos")
    top.grid()
    Button(top,text="MU0",command=lambda: emulate(0,20),
        anchor='center').grid(row=2,column=0,pady=10)
    Button(top,text="Binary & hexadecimal arithmetic",command=lambda:displaysum(1),
        anchor='center').grid(row=1,column=0, columnspan=2,pady=10,padx=10)
    Button(top,text="Exit",command=tk.destroy, foreground='red',
        anchor='center').grid(row=2,column=1)
    tk.mainloop()

gui()

__author__="tomcl"
__date__ ="$29-Jun-2010 20:41:03$"
