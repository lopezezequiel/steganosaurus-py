from PIL import Image
import os

class StegosaurusImageLSB:
    """Class to inject and extract data on an image. Image must be RGB and 
    lossless format like png. if you use jpg data will be corrupted
    """

    def _set_bit(self, byte, offset, value=True):
        """Returns an integer with the bit at offset set to 1 if value is
        True or 0 if value is False
        @param byte: byte to set 
        @type byte: int 
        @param offset: int from 0 to 7. 0 is LSB and 7 MSB.
        @type offset: int
        @param value: new value for the bit
        @type value: bool
        """

        return (1<<offset)|byte if value else ~(1<<offset)&byte


    def _get_offset_length(self, image):
        """Returns bytes needed to save the maximum data size
        @type image: PIL.Image in RGB mode
        @return: bytes needed to save the maximum data size
        @rtype: int
        """
        return len(str(self._get_max_bytes(image)))

    
    def _get_max_bytes(self, image):
        """Returns the maximum data size thats fill in the image
        """
        return image.size[0] * image.size[1] * 3 / 8

    def _data_iterator(self, data):
        """Returns data bit by bit. Bits are booleans.
        @type data: str
        @return: generator that returns bools
        @rtype: generator
        """

        for byte in data:
            for bit in format(ord(byte), '#010b')[2:]:
                yield bool(int(bit))
                

    def _position_iterator(self, image):
        """A generator to cycle through the pixels 
        @type image: PIL.Image in RGB mode
        @return: generator that returns tuples as (xy, z). z is 1, 2 or 3. 
        Used to access to rgb components of pixels
        @rtype: generator
        """
        for x in range(image.size[0]):
            for y in range(image.size[1]):
                for z in range(3):
                    yield ((x, y), z)



    def _extract_iterator(self, image):
        """Returns the data injected into image bit by bit
        @type image: PIL.Image in RGB mode
        @return: generator of bits
        @rtype: generator of bool
        """

        for xy, z in self._position_iterator(image):
            yield bool((image.getpixel(xy)[z])&1)


    def _set_image(self, image, bit, xy, z):
        """Sets the LSB of a component of an RGB pixel
        @param image: image to set
        @type image: PIL.Image
        @param bit: value of bit
        @type bit: bool
        @param xy: (x, y) coordinates
        @type xy: tuple of int
        @param z: 'r', 'g', 'b' represented as 0, 1, 2
        @type z: int
        """

        rgb = list(image.getpixel(xy))
        rgb[z] = self._set_bit(rgb[z], 0, bit)
        image.putpixel(xy, tuple(rgb))


    def get_max_size(self, image):
        """Returns the maximum message length that fits in the image
        @type image: PIL.Image in RGB mode
        @return: the maximum message length that fits in the image
        @rtype: int
        """

        assert image.mode == 'RGB', 'Image must be in RGB mode'
        ol = self._get_offset_length(image)
        mb = self._get_max_bytes(image)
        return mb - ol


    def inject(self, image, data):
        """Returns an image with the data injected
        @type image: PIL.Image in RGB mode
        @return: image with the data injected
        @rtype: PIL.Image
        """

        if len(data) > self.get_max_size(image):
            raise Exception('The data size exceeds the maximum that fits in the image')

        image = image.copy()    
        p = self._position_iterator(image)
        index = str(len(data)).zfill(self._get_offset_length(image))
        data = index + data

        for bit in self._data_iterator(data):
            xy, z = p.next()
            self._set_image(image, bit, xy, z)

        return image


    def extract(self, image):
        """Returns data injected into image passed as parameter
        @param image: image to set
        @type image: PIL.Image
        @return: data 
        @rtype: str 
        """

        c = 7
        data = ''
        byte = 0

        for bit in self._extract_iterator(image):
            byte = self._set_bit(byte, c, bit)
            if c == 0:
                data += chr(byte)
                byte = 0
                c = 7
            else:
                c -= 1
        
        il = self._get_offset_length(image)
        index = int(data[:il])

        return data[il:il+index]


    def inject_file(self, image, pathfile):
        """Returns an image with the file injected
        @type image: PIL.Image in RGB mode
        @param pathfile: path to file
        @type pathfile: str
        @return: image with the file injected
        @rtype: PIL.Image
        """

        filename = os.path.basename(pathfile)
        content = open(pathfile, 'rb').read()
        data = filename + '\x00' + content
        return self.inject(image, data)


    def extract_file(self, image, directory=None):
        """Extract file from image
        @type image: PIL.Image in RGB mode
        @param directory: path to extract
        @type directory: str
        """
        
        data = self.extract(image)
        offset = data.find('\x00')
        filename = data[:offset] 
        data = data[offset+1:]
        
        if directory == None:
            directory = os.path.dirname(os.path.abspath(__file__))
            
        filepath = os.path.join(directory, filename)

        f = open(filepath, 'wb')
        f.write(data)
        f.close()
