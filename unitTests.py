from mapinfoToQgis import StyleGenerator
import unittest

class testStyleGenerator(unittest.TestCase):
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
        gen = StyleGenerator()
        output = gen.GenerateSymbol(mapbasic,0)
        print expected
        print output
        self.assertEqual(output,expected)
    
    def testColorValueToCorrectRGB(self):
        # Expected values
        color = '16750323'
        red = 255
        green = 150
        blue = 243
        
        gen = StyleGenerator()
        colors = gen.colorToRGB(color)
        self.assertEqual(colors[0],red,"Red failed")
        self.assertEqual(colors[1],green,"Green failed")
        self.assertEqual(colors[2],blue,"Blue failed")
        
        
if __name__ == '__main__':
    unittest.main()