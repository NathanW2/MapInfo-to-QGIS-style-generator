from string import Template

class StyleGenerator:
    def generateQml(self, symbolBlocks, fieldBlock):
        """ Generates a full qml string ready for use with QGIS
        
        symbolBlocks -- List of a  qml symbol blocks generated from generateSymbol()
        fieldBlock -- qml string containing list of fields and symbol labels.  
        If fieldBlock is null and len(symbolBlocks) == 0 then a single singleSymbol renderer is used.
        
        Return A qml string ready to be writing to file for qgis to use.
        """
        qml = Template('''<qgis>
        <renderer-v2 symbollevels="0" type="$rendertype">
        <symbols>
        $symbolblocks
        </symbols>
        </renderer-v2>
        </qgis> ''')
        
        renderType = "singleSymbol"
        if fieldBlock is None:
            renderType = "singleSymbol"
        
        symbols = ""
        if len(symbolBlocks) > 0:
            for symbol in symbolBlocks:
                symbols += symbol
        
        # Generate the final qml string.
        return qml.safe_substitute(rendertype=renderType,symbolblocks=symbols)
        
    def generateSymbol(self,mapbasicString, name):
        """ Generates the qml symbol block from a MapInfo symbol string.
        
        mapbasicString -- The mapbasic symbol string.
        name -- the name of the symbol for qgis, normally 1..n
        
        Return -- A xml string based for a qml based on closest match to 
        the givin Mapbasic string.
        """
        # We can tell the type of symbol from the size of the array.
        FONTSYMBOL = 6
        count = len(mapbasicString.split(','))
        if count == FONTSYMBOL:
            return self.generateFontSymbol(mapbasicString,name)
        else:
            pass
    
    def generateFontSymbol(self,mapbasicString, name):
        """ Generates the qml symbol block from a MapInfo font symbol string.
        
        mapbasicString -- The mapbasic symbol string.
        name -- the name of the symbol for qgis, normally 1..n
        
        Return -- A xml string based for a qml based on closest match to 
        the givin Mapbasic string.
        """
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