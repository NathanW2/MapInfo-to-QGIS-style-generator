from string import Template

class StyleGenerator:
    def GenerateSymbol(self,mapbasicString, name):
        """ Generates the xml symbol block for qgis styling.
        
        mapbasicString -- The mapbasic symbol string.
        name -- the name of the symbol for qgis, normally 1..n
        
        Return A xml string based for a qml based on closest match to 
        the givin Mapbasic string.
        """
        # Just assume that we only have to deal with font symbols for now.
        # MAPBASIC Font Symbol syntax: 
        # Symbol ( shape, color, size, fontname, fontstyle, rotation )
        
        fontTemplate = Template('''
        <symbol outputUnit="MM" alpha="1" type="marker" name="$name" >
        <layer pass="0" class="FontMarker" locked="0" >
          <prop k="angle" v="$angle" />
          <prop k="chr" v="$shapeIndex" />
          <prop k="color" v="$color" />
          <prop k="font" v="$fontname" />
          <prop k="offset" v="0,0" />
          <prop k="size" v="$size" />
        </layer>
        </symbol>
        ''') 
        
        tokens = mapbasicString[mapbasicString.index('(') + 1 : mapbasicString.index(')')].split(',')
        rgb = self.colorToRGB(tokens[1])
        rgbString = "%s,%s,%s" % (rgb[0],rgb[1],rgb[2])
        values = dict(
            shapeIndex = int(tokens[0]),
            color = rgbString, # Color needs to be converted to RGB
            size = float(tokens[2]),
            fontname = tokens[3].strip('"'),
            angle = int(tokens[5]) / 180, # MapInfo rotation is back to front.
            name = name)
        # Generate the xml for a font marker
        return fontTemplate.safe_substitute(values)
    
    def colorToRGB(self, colorValue):
        ''' Returns a RGB tuple from a Mapbasic color value
        Formula: 
        R = RGB \ 65536
        G =  (RGB - R*65536) \ 256
        B = RGB - R*65536 - G*256
        '''
        color = int(colorValue)
        red = color / 65536
        green = (color - red * 65536) / 256
        blue = color - red * 65536 - green * 256
        return red,green,blue