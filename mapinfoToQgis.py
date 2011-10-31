from string import Template
import re
import string
from PyQt4.QtCore import QChar
from PyQt4.QtGui import QApplication,QPaintDevice, QPainter
from optparse import OptionParser
from templates import templateLookup

class STYLE:
    """ Type of MapInfo style clause"""
    POINT = "symbol"
    LINE = "pen"

class StyleGenerator:
    def generateQml(self, symbolQmlBlocks, fieldQmlBlock, attributeColumn):
        """ Generates a full qml string ready for use with QGIS

        symbolQmlBlocks -- List of a  qml symbol blocks generated from generateSymbol()
        fieldQmlBlock -- qml string containing list of fields and symbol labels.
        If fieldQmlBlock is null and len(symbolBlocks) == 0 then a single singleSymbol renderer is used.

        Return A qml string ready to be writing to file for qgis to use.
        """
        qml = templateLookup['baseBlock']

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

        count = len(mapbasicString.split(','))
        stylString = mapbasicString.lower()

        if (STYLE.LINE in stylString):
            # Do stuff with lines only if we have the correct amount of tokens
            if count == 3:
                return self.generateLineFromPen(mapbasicString, name)
            pass
        elif (STYLE.POINT in stylString):
            # We can tell the type of symbol from the size of the array.
            FONTSYMBOL = 6
            SIMPLESYMBOL = 3
            if count == FONTSYMBOL:
                return self.generateFontSymbol(mapbasicString,name)
            elif count == SIMPLESYMBOL:
                # Translate the simple font string into a font one.
                fontString = self.translateSimpleSymbol(mapbasicString)
                return self.generateFontSymbol(fontString,name)
            else:
                pass

    def translateSimpleSymbol(self,mapbasicString):
        """ Translates a Mapbasic 3.0 Symbol into a new font MapInfo Symbol """

        # MAPBASIC Font Symbol syntax:
        # Symbol ( shape, color, size )

        fontSymbol = Template('Symbol ($id,$color,$size,"MapInfo Symbols",0,0)')
        tokens = mapbasicString[mapbasicString.index('(') + 1 : mapbasicString.index(')')].split(',')
        # Font shape ID is +1 ID from string.
        correctId = int(tokens[0]) + 1
        color = tokens[1]
        size = tokens[2]
        # We can't handle custom symbols people have added.  Just
        # use the default MapInfo one.
        if correctId > 68:
            correctId = 33
        return fontSymbol.safe_substitute(id=correctId,size=size,color=color)

    def generateFontSymbol(self,mapbasicString, name):
        """ Generates the qml symbol block from a MapInfo font symbol string.

        mapbasicString -- The mapbasic symbol string.
        name -- the name of the symbol for qgis, normally 1..n

        Return -- A qml string based on closest match to
        the givin Mapbasic string.
        """
        # MAPBASIC Font Symbol syntax:
        # Symbol ( shape, color, size, fontname, fontstyle, rotation )

        fontTemplate = templateLookup['symbolFont']

        tokens = mapbasicString[mapbasicString.index('(') + 1 : mapbasicString.index(')')].split(',')
        rgb = self.colorToRGB(tokens[1])
        rgbString = "%s,%s,%s" % (rgb[0],rgb[1],rgb[2])
        shape = QChar(int(tokens[0])).toAscii()
        # Handle escaping special XML tokens.
        if shape == '<':
            shape = '&lt;'
        elif shape == '&':
            shape = '&amp;'
        elif shape == '"':
            shape = '&quot;'
        values = dict(
            shapeIndex = shape,
            color = rgbString, # Color needs to be converted to RGB
            size = self.pointTomm(tokens[2]), # Mapasic size 3 points == 1 mm
            fontname = tokens[3].strip('"'),
            angle = int(tokens[5]) / 180, # MapInfo rotation is back to front.
            name = name)

        # Generate the xml for a font marker
        return fontTemplate.safe_substitute(values)

    def generateLineFromPen(self, mapbasicString, name):
        # MAPBASIC Font Symbol syntax:
        # Pen ( width, pattern, color )
        # NOTE Currently we only generate simple line types.

        # TODO Refactor mapbasicString into it's own object so it can handle all this mess.
        lineTemplate = templateLookup['simpleLineStyle']
        tokens = mapbasicString[mapbasicString.index('(') + 1 : mapbasicString.index(')')].split(',')
        rgb = self.colorToRGB(tokens[2])
        rgbString = "%s,%s,%s" % (rgb[0],rgb[1],rgb[2])
        values = dict(
            color = rgbString, # Color needs to be converted to RGB
            width = self.penWidthTomm(tokens[0]),
            name = name)

        return lineTemplate.safe_substitute(values)

    def generateFieldMap(self, fieldValueMap):
        """ Generates qml block with symbol number, value, label mapping

        fieldValueMap -- A list of tuples containing number, value, label maps.

        """
        if fieldValueMap is None or len(fieldValueMap) == 0:
            return None

        catTemplate = templateLookup['categoriesBlock']

        categories = "<categories> \n"
        for cat in fieldValueMap:
            if len(cat) == 2:
                categories += catTemplate.safe_substitute(number = cat[0],
                                                        value = cat[1].strip('"'),
                                                         label = cat[1].strip('"')) + "\n"
            else:
                categories += catTemplate.safe_substitute(number = cat[0],
                                                        value = cat[1].strip('"'),
                                                        label = cat[2].strip('"')) + "\n"
        categories += "</categories>"
        return categories

    def createQmlFromFile(self, asciiFile,outName,columnName):
        """ Writes a qml file from a | delimited file
        Syntax of input file:
            {value} | {label} | {font style}
        or
            {value} | {font style}

        asciiFile -- Name of the input file in the supported format
        outName -- Name of the output qml file
        columnName -- Name of the column that contains the values.
        """

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
                fields.append((count,items[0],items[1]))
            #The last column is always the style string.
            symbols[count] = items[-1]
            count += 1
        styles.close()

        #Generate the qml file
        print "Generating QGIS styles for:"
        symbolsList = []
        for symbolNo in symbols:
            print "No. %s : %s " % (symbolNo, symbols[symbolNo])
            symbolqml = gen.generateSymbol(symbols[symbolNo],symbolNo)
            if not symbolqml is None:
                symbolsList.append(symbolqml)
            else:
                continue
        fields = gen.generateFieldMap(fields)
        qml = gen.generateQml(symbolsList,fields,columnName)

        outqml = open(outName,'w')
        outqml.write(qml)
        outqml.close()

    def createQMLFromMapInfoTable(self,mapinfoTable, outName, columnName):
        """ Opens MapInfo and generates a qml file from the supplied table.
        mapinfoTable -- Name of the input tab file.
        outName -- Name of the output qml file
        columnName -- Name of the column that contains the values.

        WARNING: Very little error handling here.
        """

        import tempfile, os
        from win32com.client import Dispatch
        openTable = 'Open Table "%s" as tempMapInfoToQGIS' % mapinfoTable
        groupBySQL = 'Select %s, Str$(ObjectInfo(obj,2)) from tempMapInfoToQGIS Group By %s Into outputTable' % (columnName, columnName)
        tempoutput = tempfile.gettempdir() + "\mapinfoToQGISTemp.txt"
        try:
            os.remove(tempoutput)
        except WindowsError:
            #Do nothing here as MapInfo will create the file.
            pass
        exportString = 'Export "outputTable" Into "%s" Type "ASCII" Delimiter "|" CharSet "WindowsLatin1"' % tempoutput

        print "Opening MapInfo..."
        mapinfo = Dispatch("MapInfo.Application")
        mapinfo.do(openTable)
        mapinfo.do(groupBySQL)
        print "Exporting style table..."
        mapinfo.do(exportString)

        mapinfo.do("End MapInfo")
        mapinfo = None

        self.createQmlFromFile(tempoutput,outName,columnName)

    def colorToRGB(self, colorValue):
        """ Returns a RGB tuple from a Mapbasic color value
        Formula:
        R = RGB \ 65536
        G =  (RGB - R*65536) \ 256
        B = RGB - R*65536 - G*256
        """
        color = int(colorValue)
        red = color / 65536
        green = (color - red * 65536) / 256
        blue = color - red * 65536 - green * 256
        return red,green,blue

    def pointTomm(self,pointSize):
        return float(pointSize) / 3

    def penWidthTomm(self, pensize):
        # Pen width info from http://www.gissky.com/download/Download/DataFormat/Mapinfo_Mif.pdf
        # Width is a number from 1 to 7. 1-7 is the width in screen pixels. 11-2047 are values that will be
        # converted to points:
        # penwidth = (number of points * 10) + 10
        pensize = float( pensize )
        if ( pensize >= 11 ):
            pointsize = (float(pensize) - 10) / 10
            return pointsize / 3
        else:
            # This isn't really right as pixel size depends on the moniter settings but
            # working it out is a real pain so using this method will work for now.
            return pensize / 3


if __name__ == '__main__':
    gen = StyleGenerator()
    usage = '''usage: %prog  inputFile outQmlFile [options]

inputFile must contain a list of values and styles in the following format
Supported formats:
        {value} | {label} | {font style}
    or
        {value} | {font style}
    '''
    parser = OptionParser(usage)
    parser.add_option("-c", "--column", dest="columnName",
                      help="Name of the column the values are in")
    parser.add_option("-m", "--UseMapInfo", action="store_true", dest="useMapInfo",
                      default=False, help="If used MapInfo will be invoked to handle to needed query for \
                      the correct input.  inputFile must be the path a MapInfo table. \
                      Column name must be supplied using -c \
                      Only point object tables are currently supported. \
                      MapInfo must be installed. ")

    (options, args) = parser.parse_args()
    columnName = options.columnName

    if options.useMapInfo:
        gen.createQMLFromMapInfoTable(args[0],args[1],columnName)
    elif (not options.useMapInfo):
        gen.createQmlFromFile(args[0],args[1],columnName or "")
    else:
        parser.error("incorrect number of arguments")



