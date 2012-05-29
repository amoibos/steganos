#! /usr/bin/env python
#encoding:UTF-8

# Copyright 2012, Daniel Oelschlegel <amoibos@gmail.com>
# License: 2-clause BSD

try:
    import Image
except ImportError:
    print "please install pil"

#TODOs:   
#     :   full unicode and binary support
#     :   flexible bit length(default 1bit per color component)
#     :   save also file name
#     :   tk gui
#     :   better encryption support, currently simple XOR implemented
#     :   advanced header, mutiple files
#     :   better, faster, shorter code

#unicode tests, binary tests
#error handling
#check behaviour for l and p mode
#optimal variable size

__author__ = "Daniel Oelschlegel"
__copyright__ = "Copyright 2012, " + __author__
__credits__ = [""]
__license__ = "BSD"
__version__ = "0.1"

class Steganos(object):
    # save unnecessary computations
    SELECT = (128, 64, 32, 16, 8, 4, 2, 1)
    # 4 bytes for the payload size
    MAX_TEXT_SIZE = 4
    INFINITY = 1 << 30
    
    def __init__(self, filename, password=''):
        self._image = Image.open(filename)
        # current color tuple
        self._position = self._headerSize() * 8 // len(self._image.getbands())
        # current component of color tuple
        self._band = self._headerSize() * 8 % len(self._image.getbands())
        # payload length
        self._size = 0
        self._password = password
        # all color tuples
        self._data = list(self._image.getdata())
    
    def _headerSize(self):
        return Steganos.MAX_TEXT_SIZE
    
    def _reset(self, position=0, band=0):
        self._position = position
        self._band = band
    
    def currentSize(self):
        return self._size
        
    def currentPassword(self):
        return self._password
    
    def maxDataSize(self):
        width, height = self._image.size
        calc = max(width * height * len(self._image.getbands()) // 8 - self._headerSize(), 
                   Steganos.INFINITY)
        return calc

    def freeDataSize(self):
        return max(self.maxDataSize() - len(self._image.getbands()) * (self._position + 1), 0)

    def update(self, text, header=False):
        if not header and self.freeDataSize() < len(text):
            return
        if not header:
            if self._password != '':
                text = self._encrypt(text)
            if self._size + len(text) + self._headerSize() > self.maxDataSize():
                return
            self._size += len(text)
        color = list(self._data[self._position]) 
        bandNumber = len(self._image.getbands())       
        for char in text:
            for bit in xrange(8):  
                if (ord(char) & Steganos.SELECT[bit]) != 0:
                    color[self._band] |= 1
                else:
                    color[self._band] &= ~1
                self._data[self._position] = tuple(color)
                self._band += 1
                if self._band == bandNumber:
                    self._band = 0
                    self._position += 1
                    color = list(self._data[self._position])  
        
    def extract(self):
        self._reset()
        text = ''
        bit = code = charcnt = 0
        self._size = Steganos.INFINITY
        for self._position in xrange(Steganos.INFINITY):
            color = self._data[self._position]
            for self._band in xrange(len(color)):
                if (color[self._band] & 1) != 0:
                    code += Steganos.SELECT[bit]
                bit += 1
                if bit == 8:
                    text += chr(code)
                    bit = code = 0
                    charcnt += 1
                    if self._size == Steganos.INFINITY and \
                        len(text) == self._headerSize():
                        # retrieve payload size from header
                        self._size = (ord(text[0]) << 24) + (ord(text[1]) << 16)
                        self._size += (ord(text[2]) << 8) + ord(text[3])
                        text = ''
                        charcnt = 0
                    elif charcnt == self._size:
                        break
            # for continuation after extracting          
            if charcnt == self._size:
                if self._band + 1 == len(color):
                    self._band = 0
                    self._position += 1
                else:
                    self._band += 1 
                break
        if self._password != '':
            text = self._decrypt(text)
        return text
    
    def _encrypt(self, text):
        start = self._size % len(self._password)
        key = (self._password * 2)[start:start + len(self._password)]
        cipher = ''
        for pos in xrange(len(text)):
            cipher += chr(ord(text[pos]) ^\
                ord(key[pos % len(self._password)]))
        return cipher
        
    def _decrypt(self, text):
        cipher = ''
        for pos in xrange(len(text)):
            cipher += chr(ord(text[pos]) ^\
                ord(self._password[pos % len(self._password)]))
        return cipher
            
    def _writeHeader(self, jumpBack=True):
        band, position = self._band, self._position
        self._reset()
        header = ''
        header += chr(self._size >> 24 & 0xff) + chr(self._size >> 16 & 0xff)
        header += chr(self._size >> 8  & 0xff) + chr(self._size >> 0  & 0xff)
        self.update(header, True)
        # HACK: possibilty to override payload
        if jumpBack:
            self._reset(position, band)
        else:
            self._size = 0
        
    def save(self, filename):
        self._writeHeader()
        if not filename.lower().endswith('.png'):
            filename += '.png'
        self._image.putdata(tuple(self._data))
        self._image.save(filename)
        
        
if __name__ == '__main__':    
    teststr = ["ABCDEFabc 0123456789 ÖÄÜß", "124", "blub"]
    password = "secret"
    image_name = 'Android.png'
    
    # test without password but with mutiple continuations
    print "multiple continuations test: ",
    filename1 = 'image_Steganos.png'
    test = Steganos(image_name)
    for string in teststr:
        test.update(string)
    test.save(filename1)
    print "success" if Steganos(filename1).extract() == "".join(teststr) else "fail"
