from mapinfoToQgis import StyleGenerator
import unittest
import difflib

class testStyleGenerator(unittest.TestCase):
    def setUp(self):
        self.gen = StyleGenerator()
        
    def testQmlOutputWithOneSymbolBlock(self):
        symbolblock = '''<symbol outputUnit="MM" alpha="1" type="marker" name="0" >
        <layer pass="0" class="FontMarker" locked="0" >
          <prop k="angle" v="0" />
          <prop k="chr" v="101" />
          <prop k="color" v="160,64,255" />
          <prop k="font" v="MapInfo Cartographic" />
          <prop k="offset" v="0,0" />
          <prop k="size" v="9.0" />
        </layer>
        </symbol> '''
        
        expected = '''<qgis>
        <renderer-v2 symbollevels="0" type="singleSymbol">
        <symbols>
        <symbol outputUnit="MM" alpha="1" type="marker" name="0" >
        <layer pass="0" class="FontMarker" locked="0" >
          <prop k="angle" v="0" />
          <prop k="chr" v="101" />
          <prop k="color" v="160,64,255" />
          <prop k="font" v="MapInfo Cartographic" />
          <prop k="offset" v="0,0" />
          <prop k="size" v="9.0" />
        </layer>
        </symbol>
        </symbols>
        </renderer-v2>
        </qgis>'''
        output = self.gen.generateQml([symbolblock],None)
        print output
        print ''.join(difflib.ndiff(expected.splitlines(1),output.splitlines(1)))
        self.assertEqual(output,expected)
    
    def testFontSymbolGeneration(self):
        mapbasic = 'Symbol (101,10502399,9,"MapInfo Cartographic",1,0)'
        expected = '''
        <symbol outputUnit="MM" alpha="1" type="marker" name="0" >
        <layer pass="0" class="FontMarker" locked="0" >
          <prop k="angle" v="0" />
          <prop k="chr" v="101" />
          <prop k="color" v="160,64,255" />
          <prop k="font" v="MapInfo Cartographic" />
          <prop k="offset" v="0,0" />
          <prop k="size" v="9.0" />
        </layer>
        </symbol>
        '''
        output = self.gen.generateSymbol(mapbasic,0)
        print expected
        print output
        self.assertEqual(output,expected)
    
    def testColorValueToCorrectRGB(self):
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