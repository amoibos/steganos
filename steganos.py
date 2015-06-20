#!/usr/bin/env python
#encoding:UTF-8

# Copyright 2012, Daniel Oelschlegel <amoibos@gmail.com>
# License: 2-clause BSD
from __future__ import division
from PIL import Image

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
    
    def _header_size(self):
        return Steganos.MAX_TEXT_SIZE
    
    def _reset(self, position=0, band=0):
        self._position = position
        self._band = band
    
    def current_size(self):
        return self._size
        
    def current_password(self):
        return self._password
    
    def max_data_size(self):
        width, height = self._image.size
        calc = min(width * height * len(self._image.getbands()) // 8 \
            - self._header_size(), Steganos.INFINITY)
        return calc

    def free_data_size(self):
        return max(self.max_data_size() - len(self._image.getbands()) *\
            (self._position + 1), 0)

    def update(self, text, header=False):
        if not header and self.free_data_size() < len(text):
            return
        if not header:
            if self._password != '':
                text = self._encrypt(text)
            if self._size + len(text) + self._header_size() > self.max_data_size():
                return
            self._size += len(text)
        color = list(self._data[self._position]) 
        band_number = len(self._image.getbands())       
        for char in text:
            for bit in range(8):  
                if (ord(char) & Steganos.SELECT[bit]) != 0:
                    color[self._band] |= 1
                else:
                    color[self._band] &= ~1
                self._data[self._position] = tuple(color)
                self._band += 1
                if self._band == band_number:
                    self._band = 0
                    self._position += 1
                    color = list(self._data[self._position])  
        
    def extract(self):
        self._reset()
        text = ''
        bit = code = char_cnt = 0
        self._size = Steganos.INFINITY
        for self._position in range(Steganos.INFINITY):
            data = self._data[self._position]
            for self._band, _ in enumerate(data):
                if (data[self._band] & 1) != 0:
                    code += Steganos.SELECT[bit]
                bit += 1
                if bit == 8:
                    text += chr(code)
                    bit = code = 0
                    char_cnt += 1
                    if self._size == Steganos.INFINITY and \
                        len(text) == self._header_size():
                        # retrieve payload size from header
                        self._size = (ord(text[0]) << 24) + (ord(text[1]) << 16)
                        self._size += (ord(text[2]) << 8) + ord(text[3])
                        text = ''
                        char_cnt = 0
                    elif char_cnt == self._size:
                        break
            # for continuation after extracting          
            if char_cnt == self._size:
                if self._band + 1 == len(data):
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
        for pos,_ in enumerate(text):
            cipher += chr(ord(text[pos]) ^\
                ord(key[pos % len(self._password)]))
        return cipher
        
    def _decrypt(self, text):
        cipher = ''
        for pos, _ in enumerate(text):
            cipher += chr(ord(text[pos]) ^\
                ord(self._password[pos % len(self._password)]))
        return cipher
            
    def _write_header(self, jumpBack=True):
        band, position = self._band, self._position
        self._reset()
        header = ''
        header += chr(self._size >> 24 & 0xff) + chr(self._size >> 16 & 0xff)
        header += chr(self._size >> 8  & 0xff) + chr(self._size >> 0  & 0xff)
        self.update(header, True)
        # make it possibile to override payload
        if jumpBack:
            self._reset(position, band)
        else:
            self._size = 0
        
    def save(self, filename):
        self._write_header()
        if not filename.lower().endswith('.png'):
            filename = "".join([filename, '.png'])
        self._image.putdata(tuple(self._data))
        self._image.save(filename)
        
        
if __name__ == '__main__':    
    teststrings = ["ABCDEFabc 0123456789 ÖÄÜß", "124", "blub"]
    password = "secret"
    image_name = 'Android.png'
    
    # test without password but with mutiple continuations
    file_name = 'image_Steganos.png'
    test = Steganos(image_name)
    for string in teststrings:
        test.update(string)
    test.save(fileName)
    assert Steganos(fileName).extract() == "".join(testStrings)
