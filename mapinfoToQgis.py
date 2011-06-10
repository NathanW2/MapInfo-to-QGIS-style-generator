from string import Template
import re
import string
from PyQt4.QtCore import QChar
from optparse import OptionParser

class StyleGenerator:
    def generateQml(self, symbolQmlBlocks, fieldQmlBlock, attributeColumn):
        """ Generates a full qml string ready for use with QGIS

        symbolQmlBlocks -- List of a  qml symbol blocks generated from generateSymbol()
        fieldQmlBlock -- qml string containing list of fields and symbol labels.
        If fieldQmlBlock is null and len(symbolBlocks) == 0 then a single singleSymbol renderer is used.

        Return A qml string ready to be writing to file for qgis to use.
        """
        qml = Template('''<qgis>
        <renderer-v2 $attr symbollevels="0" type="$rendertype"> $categories
        <symbols>
        $symbolblocks
        </symbols>
        </renderer-v2>
        </qgis>''')

        # Handle for the case of a single symbol by default
        renderType = "singleSymbol"
        attribute = ""
        categories = ""
        # If we have information in the fieldQmlBlock then we use a different renderer.
        if not fieldQmlBlock is None and not attributeColumn is None:
            renderType = "categorizedSymbol"
            attribute = 'attr="' + attributeColumn + '"'
            categories = '\n' + fieldQmlBlock

        symbols = ""
        if len(symbolQmlBlocks) > 0:
            for symbol in symbolQmlBlocks:
                symbols += symbol

        # Generate the final qml string.
        return qml.safe_substitute(attr = attribute,
                                   categories = categories,
                                   rendertype = renderType,
                                   symbolblocks = symbols)


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

        Return -- A qml string based on closest match to
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
        </symbol>''')

        tokens = mapbasicString[mapbasicString.index('(') + 1 : mapbasicString.index(')')].split(',')
        rgb = self.colorToRGB(tokens[1])
        rgbString = "%s,%s,%s" % (rgb[0],rgb[1],rgb[2])
        values = dict(
            shapeIndex = QChar(int(tokens[0])).toAscii(),
            color = rgbString, # Color needs to be converted to RGB
            size = self.pointTomm(tokens[2]), # Mapasic size 3 points == 1 mm
            fontname = tokens[3].strip('"'),
            angle = int(tokens[5]) / 180, # MapInfo rotation is back to front.
            name = name)
        # Generate the xml for a font marker
        return fontTemplate.safe_substitute(values)

    def generateFieldMap(self, fieldValueMap):
        ''' Generates qml block with symbol number, value, label mapping

        fieldValueMap -- A list of tuples containing number, value, label maps.

        '''
        if fieldValueMap is None or len(fieldValueMap) == 0:
            return None

        catTemplate = Template('<category symbol="$number" value="$value" label="$label" />')

        categories = "<categories> \n"
        for cat in fieldValueMap:
            if len(cat) == 2:
                categories += catTemplate.safe_substitute(number = cat[0],value = cat[1], label = cat[1]) + "\n"
            else:
                categories += catTemplate.safe_substitute(number = cat[0],value = cat[1], label = cat[2]) + "\n"
        categories += "</categories>"
        return categories

    def createQmlFromFile(self, asciiFile,outName,columnName):
        styles = open(asciiFile)
        fields = []
        symbols = {}
        count = 0
        for line in styles:
            items = line.split('|')
            if len(items) == 2:
                # First column is value second is style
                fields.append((count,items[0]))
            else:
                # First column is value, second is label, third is style
                fields.append((count,items[0],items[0]))
            symbols[count] = items[-1]
            count += 1
        #Generate the qml file
        symbolsList = []
        for symbol in symbols:
            symbolsList.append(gen.generateFontSymbol(symbols[symbol],symbol))
        fields = gen.generateFieldMap(fields)
        qml = gen.generateQml(symbolsList,fields,columnName)

        outqml = open(outName,'w')
        outqml.write(qml)

        outqml.close()
        styles.close()

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

    def pointTomm(self,pointSize):
        return float(pointSize) / 3

if __name__ == '__main__':
    gen = StyleGenerator()
    usage = "usage: %prog  inputFile outQmlFile [options]"
    parser = OptionParser(usage)
    parser.add_option("-c", "--column", dest="columnName",
                      help="Name of the column the values are in")

    (options, args) = parser.parse_args()
    gen.createQmlFromFile(args[0],args[1],options.columnName or "")



