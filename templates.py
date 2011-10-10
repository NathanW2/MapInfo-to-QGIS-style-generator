# This file contains all the qml style templates for MapInfo->QGIS
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

simpleLineStyleQML = '''<symbol outputUnit="MM" alpha="1" type="line" name="$name">
<layer pass="0" class="SimpleLine" locked="0">
  <prop k="capstyle" v="square"/>
  <prop k="color" v="$color"/>
  <prop k="customdash" v="5;2"/>
  <prop k="joinstyle" v="bevel"/>
  <prop k="offset" v="0"/>
  <prop k="penstyle" v="solid"/>
  <prop k="use_custom_dash" v="0"/>
  <prop k="width" v="$width"/>
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
                    "simpleLineStyle":Template(simpleLineStyleQML),
                    "baseBlock":Template(stylebaseQML)
}
