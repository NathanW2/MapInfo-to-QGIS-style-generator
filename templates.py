# This file contains all the qml style templates for QGIS->MapInfo
from string import Template

fontStyleQML = '''<symbol outputUnit="MM" alpha="1" type="marker" name="$name" >
<layer pass="0" class="FontMarker" locked="0" >
  <prop k="angle" v="$angle" />
  <prop k="chr" v="$shapeIndex" />
  <prop k="color" v="$color" />
  <prop k="font" v="$fontname" />
  <prop k="offset" v="0,0" />
  <prop k="size" v="$size" />
</layer>
</symbol>'''

categoriesQML = '<category symbol="$number" value="$value" label="$label" />'

stylebaseQML = '''<qgis>
<renderer-v2 $attr symbollevels="0" type="$rendertype"> $categories
<symbols>
$symbolblocks
</symbols>
</renderer-v2>
</qgis>'''

templateLookup = {
                    "symbolFont":Template(fontStyleQML),
                    "categoriesBlock":Template(categoriesQML),
                    "baseBlock":Template(stylebaseQML)
}

print stylebaseQML