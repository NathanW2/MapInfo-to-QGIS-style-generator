from mapinfoToQgis import StyleGenerator
import unittest
import difflib

class testStyleGenerator(unittest.TestCase):
    def setUp(self):
        self.gen = StyleGenerator()

    def testField_Map_Qml_With_Label_And_Value(self):
        fieldMap = [(0,"TestLabel2","TestValue"),(1,"TestLabel2","TestValue2")]
        output = self.gen.generateFieldMap(fieldMap)

        expected = '<categories> \n'
        expected += '<category symbol="0" value="TestLabel2" label="TestValue" />\n'
        expected += '<category symbol="1" value="TestLabel2" label="TestValue2" />\n'
        expected += '</categories>'
        self.assertEqual(output,expected)

    def testPoint_To_QGISSize(self):
        '''Conversion should be 3 points == 1mm'''
        expected = 1
        point = 3
        self.assertEqual(self.gen.pointTomm(point),expected)

    def testPenWidthToPoints(self):
        expected = 3
        penwdith = 40
        self.assertEqual(self.gen.penWidthToPoint(penwdith),expected)

    def testFont_Symbol_Generation(self):
        mapbasic = 'Symbol (101,10502399,9,"MapInfo Cartographic",1,0)'
        expected = '''<symbol outputUnit="MM" alpha="1" type="marker" name="0" >
<layer pass="0" class="FontMarker" locked="0" >
  <prop k="angle" v="0" />
  <prop k="chr" v="e" />
  <prop k="color" v="160,64,255" />
  <prop k="font" v="MapInfo Cartographic" />
  <prop k="offset" v="0,0" />
  <prop k="size" v="3.0" />
</layer>
</symbol>'''

        output = self.gen.generateSymbol(mapbasic,0)
        self.assertEqual(output,expected)

    def testColor_Value_To_CorrectRGB(self):
        # Expected values
        color = '16750323'
        red = 255
        green = 150
        blue = 243

        colors = self.gen.colorToRGB(color)
        self.assertEqual(colors[0],red,"Red failed")
        self.assertEqual(colors[1],green,"Green failed")
        self.assertEqual(colors[2],blue,"Blue failed")


if __name__ == '__main__':
    unittest.main()