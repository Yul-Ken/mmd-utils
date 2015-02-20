#!/usr/bin/env python
# -*- coding: utf-8 -*-
###############################################################################
# The MIT License (MIT)
#
# Copyright (c) <year> <copyright holders>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
###############################################################################
from __future__ import unicode_literals
from __future__ import division

import os
import sys

import StringIO

from pandac.PandaModules import *

# need to be before the Direct Start Import
loadPrcFileData("", "window-title MMD PMX/PMX Model Viewer")
loadPrcFileData("", "icon-filename viewpmx.ico")
loadPrcFileData("", "win-size 800 800")
loadPrcFileData("", "window-type none")
loadPrcFileData('', 'text-encoding utf8')
loadPrcFileData('', 'textures-power-2 none')

from panda3d.core import ConfigVariableString
from panda3d.core import Shader
from panda3d.core import Filename
from panda3d.core import Material
from panda3d.core import VBase4


from direct.filter.CommonFilters import CommonFilters
from direct.showbase.ShowBase import ShowBase

import direct.directbase.DirectStart

from direct.gui.DirectGui import *

from utils.DrawPlane import *
from utils.pmx import *

# Get the location of the 'py' file I'm running:
CWD = os.path.abspath(sys.path[0])

SHOW_LIGHT_POS = True
SHOW_LIGHT_POS = False

SHOW_SHADOW = True
SHOW_SHADOW = False

SHOW_AXIS = True
# SHOW_AXIS = False

lastModel = None

def setCamera(x=0, y=0, z=0, h=0, p=0, r=0, oobe=False):
  base.camLens.setNearFar(0.1, 550.0)
  base.camLens.setFov(45.0)
  base.camLens.setFocalLength(50)

  # base.trackball.node().setPos(0, 20, -20)
  base.trackball.node().setHpr(h, p, r)
  base.trackball.node().setPos(x, y, -z)

  # base.useDrive()
  if oobe:
    # base.oobe()
    base.oobeCull()
  pass

def resetCamera():
  if lastModel:
    min_point = LPoint3f()
    max_point = LPoint3f()
    lastModel.calcTightBounds(min_point, max_point)

    node_size = LPoint3f(max_point.x-min_point.x, max_point.y-min_point.y, max_point.z-min_point.z)
    setCamera(x=0, y=1.6*node_size.z, z=0.5*node_size.z, p=10, oobe=False)
  pass

def setStudioLight(render):
  lightsStage = u'./stages/default_lights.bam'
  try:
    lights = loader.loadModel(lightsStage)
  except:
    lights = NodePath(PandaNode('StageLights'))

    alight = AmbientLight('alight')
    alight.setColor(VBase4(0.67, 0.67, 0.67, .8))
    # alight.setColor(VBase4(0.33, 0.33, 0.33, 0.67))
    alnp = render.attachNewNode(alight)
    alnp.reparentTo(lights)

    dlight_top = PointLight('top dlight')
    dlnp_top = render.attachNewNode(dlight_top)
    dlnp_top.setX(-5)
    dlnp_top.setZ(45)
    dlnp_top.setY(0)
    # dlnp_top.node().setAttenuation( Vec3( 0.001, 0.005, 0.001 ) )
    dlnp_top.node().setAttenuation( Vec3( 0.005, 0.005, 0.005 ) )
    dlnp_top.setHpr(0, -180, 0)
    if SHOW_LIGHT_POS:
      dlnp_top.node().showFrustum()
    dlnp_top.reparentTo(lights)

    dlight_back = PointLight('back dlight')
    dlnp_back = render.attachNewNode(dlight_back)
    dlnp_back.setX(0)
    dlnp_back.setZ(25)
    dlnp_back.setY(+55)
    # dlnp_back.node().setAttenuation( Vec3( 0.001, 0.005, 0.001 ) )
    dlnp_back.node().setAttenuation( Vec3( 0.001, 0.005, 0.001 ) )
    dlnp_back.setHpr(0, -168, 0)
    if SHOW_LIGHT_POS:
      dlnp_back.node().showFrustum()
    dlnp_back.reparentTo(lights)

    dlight_front = PointLight('front dlight')
    dlnp_front = render.attachNewNode(dlight_front)
    dlnp_front.setX(0)
    dlnp_front.setY(-36)
    dlnp_front.setZ(15)
    dlens = dlnp_front.node().getLens()
    dlens.setFilmSize(41, 21)
    # dlens.setNearFar(50, 75)
    dlnp_front.node().setAttenuation( Vec3( 0.001, 0.005, 0.001 ) )
    # dlnp_front.node().setAttenuation( Vec3( 0.005, 0.005, 0.005 ) )
    dlnp_front.setHpr(0, -10, 0)
    if SHOW_LIGHT_POS:
      dlnp_front.node().showFrustum()
    dlnp_front.reparentTo(lights)

    dlight_left = Spotlight('left dlight')
    dlnp_left = render.attachNewNode(dlight_left)
    dlnp_left.setX(-46)
    dlnp_left.setY(+36)
    dlnp_left.setZ(27)
    dlens = dlnp_left.node().getLens()
    dlens.setFilmSize(41, 21)
    # dlens.setNearFar(50, 75)
    dlnp_left.node().setAttenuation( Vec3( 0.001, 0.002, 0.001 ) )
    # dlnp_left.node().setAttenuation( Vec3( 0.011, 0.011, 0.011 ) )
    dlnp_left.setHpr(-130, -15, 0)
    if SHOW_LIGHT_POS:
      dlnp_left.node().showFrustum()
    dlnp_left.reparentTo(lights)

    dlight_right = Spotlight('right dlight')
    dlnp_right = render.attachNewNode(dlight_right)
    dlnp_right.setX(+50)
    dlnp_right.setY(+40)
    dlnp_right.setZ(30)
    dlens = dlnp_right.node().getLens()
    dlens.setFilmSize(41, 21)
    # dlens.setNearFar(50, 75)
    dlnp_right.node().setAttenuation( Vec3( 0.001, 0.002, 0.001 ) )
    # dlnp_right.node().setAttenuation( Vec3( 0.011, 0.011, 0.011 ) )
    dlnp_right.setHpr(130, -15, 0)
    if SHOW_LIGHT_POS:
      dlnp_right.node().showFrustum()
    dlnp_right.reparentTo(lights)

    if SHOW_SHADOW:
      lights.setShaderAuto()
      lights.setShadowCaster(True, 512, 512)

    # lights.writeBamFile(lightsStage)

  # lights.reparentTo(render)
  return(lights)
  pass

def lightAtNode(node, lights=None):
  if not lights:
      return
  if isinstance(node, NodePathCollection):
    for np in node:
      for light in lights.getChildren():
        np.setLight(light)
  elif isinstance(node, NodePath):
    for light in lights.getChildren():
      try:
        node.setLight(light)
      except:
        continue
  pass

def setAxis(render):
  axisStage = u'./stages/default_axis.bam'
  try:
    gridnodepath = loader.loadModel(axisStage)
  except:
    grid = ThreeAxisGrid(xy=True, yz=False, xz=False, z=False)
    gridnodepath = grid.create()
    grid.showPlane(XY=True)
    grid.showAxis(Z=False)
    gridnodepath.writeBamFile(axisStage)
  gridnodepath.reparentTo(render)
  pass

def setAppInfo(title, icon):
  # 'DtoolClassDict', 'DtoolGetSupperBase',
  # 'MAbsolute', 'MRelative', 'M_absolute', 'M_relative',
  # 'ZBottom', 'ZNormal', 'ZTop', 'Z_bottom', 'Z_normal', 'Z_top',
  # 'addProperties', 'add_properties',
  # 'assign', 'clear',
  # 'clearCursorFilename', 'clearCursorHidden', 'clearDefault', 'clearFixedSize',
  # 'clearForeground', 'clearFullscreen',
  #  'clearIconFilename', 'clearMinimized', 'clearMouseMode',
  #  'clearOpen', 'clearOrigin', 'clearParentWindow', 'clearRawMice', 'clearSize',
  #  'clearTitle', 'clearUndecorated',
  #  'clearZOrder', 'clear_cursor_filename', 'clear_cursor_hidden',
  #  'clear_default', 'clear_fixed_size', 'clear_foreground', 'clear_fullscreen', 'clear_icon_filename',
  #  'clear_minimized', 'clear_mouse_mode', 'clear_open', 'clear_origin', 'clear_parent_window', 'clear_raw_mice', 'clear_size',
  #  'clear_title', 'clear_undecorated', 'clear_z_order',
  #  'getConfigProperties', 'getCursorFilename', 'getCursorHidden', 'getDefault', 'getFixedSize', 'getForeground', 'getFullscreen',
  #  'getIconFilename', 'getMinimized', 'getMouseMode', 'getOpen', 'getParentWindow', 'getRawMice', 'getTitle', 'getUndecorated',
  #  'getXOrigin', 'getXSize', 'getYOrigin', 'getYSize', 'getZOrder',
  #  'get_config_properties', 'get_cursor_filename', 'get_cursor_hidden', 'get_default', 'get_fixed_size',
  #  'get_foreground', 'get_fullscreen', 'get_icon_filename', 'get_minimized', 'get_mouse_mode', 'get_open',
  #  'get_parent_window', 'get_raw_mice', 'get_title', 'get_undecorated',
  #  'get_x_origin', 'get_x_size', 'get_y_origin', 'get_y_size', 'get_z_order',
  #  'hasCursorFilename', 'hasCursorHidden', 'hasFixedSize', 'hasForeground', 'hasFullscreen', 'hasIconFilename', 'hasMinimized',
  #  'hasMouseMode', 'hasOpen', 'hasOrigin', 'hasParentWindow', 'hasRawMice', 'hasSize', 'hasTitle', 'hasUndecorated', 'hasZOrder',
  #  'has_cursor_filename', 'has_cursor_hidden', 'has_fixed_size', 'has_foreground', 'has_fullscreen', 'has_icon_filename',
  #  'has_minimized', 'has_mouse_mode', 'has_open', 'has_origin', 'has_parent_window', 'has_raw_mice', 'has_size', 'has_title',
  #  'has_undecorated', 'has_z_order', 'isAnySpecified', 'is_any_specified',
  #  'output',
  #  'setCursorFilename', 'setCursorHidden', 'setDefault', 'setFixedSize', 'setForeground', 'setFullscreen', 'setIconFilename',
  #  'setMinimized', 'setMouseMode', 'setOpen', 'setOrigin', 'setParentWindow', 'setRawMice', 'setSize', 'setTitle', 'setUndecorated',
  #  'setZOrder', 'set_cursor_filename', 'set_cursor_hidden', 'set_default', 'set_fixed_size', 'set_foreground', 'set_fullscreen',
  #  'set_icon_filename', 'set_minimized', 'set_mouse_mode', 'set_open', 'set_origin', 'set_parent_window', 'set_raw_mice', 'set_size',
  #  'set_title', 'set_undecorated', 'set_z_order', 'size', this', 'this_metatype'

  props = WindowProperties()
  props.setTitle(title)
  props.setIconFilename(Filename.fromOsSpecific(os.path.join(CWD, icon)))
  base.win.requestProperties(props)
  pass

def snapshot(snapfile='snap_00.png'):
  result = False
  if lastModel:
    GUI = render2d.find('**/aspect2d/*')
    GUI.hide()
    path = lastModel.node().getTag('path')
    fn = os.path.splitext(os.path.basename(path))
    folder = os.path.dirname(path)
    snapfile = os.path.join(folder, u'snap_%s.png' % (fn[0]))
    base.graphicsEngine.renderFrame()
    result = base.screenshot(namePrefix=snapfile, defaultFilename=0, source=None, imageComment=fn[0])
    GUI.show()
  return(result)
  pass

def menuItemSel(arg):
  if arg in [u'X轴线', u'Y轴线', u'Z轴线', u'XY平面', u'YZ平面', u'XZ平面']:
    if   arg == u'X轴线':
      axis = render.find('**/AXISLINE/X*')
    elif arg == u'Y轴线':
      axis = render.find('**/AXISLINE/Y*')
    elif arg == u'Z轴线':
      axis = render.find('**/AXISLINE/Z*')
    elif arg == u'XY平面':
      axis = render.find('**/PLANEGRID/XY*')
    elif arg == u'YZ平面':
      axis = render.find('**/PLANEGRID/YZ*')
    elif arg == u'XZ平面':
      axis = render.find('**/PLANEGRID/XZ*')

    if axis.isHidden():
      axis.show()
    else:
      axis.hide()
  else:
    pass

  # menuAxisSelect = render2d.find('**/menuAxisSelect*')
  # if menuAxisSelect:
  #   print(menuAxisSelect.ls())
  #   menuAxisSelect.node().setup(u'坐标系  ')
  pass

def processVertexData(vdata_src, vdata_dst, morph=True, strength=1.0):
  print('morph ------> ', morph)
  vertex_src = GeomVertexWriter(vdata_src, 'vertex')

  vertex_dst = GeomVertexReader(vdata_dst, 'vertex')
  vindex_dst = GeomVertexReader(vdata_dst, 'vindex')
  vmorph_dst = GeomVertexReader(vdata_dst, 'vmorph')

  vertex_dst.setForce(True)
  vindex_dst.setForce(True)
  vmorph_dst.setForce(True)
  while not vertex_dst.isAtEnd():
    v_dst = vertex_dst.getData3f()
    i_dst = vindex_dst.getData1i()
    m_dst = vmorph_dst.getData3f()
    vertex_src.setRow(i_dst)
    if morph:
      vertex_src.setData3f(v_dst.getX()+m_dst.getX(), v_dst.getY()+m_dst.getY(), v_dst.getZ()+m_dst.getZ())
    else:
      vertex_src.setData3f(v_dst.getX(), v_dst.getY(), v_dst.getZ())

def processGeom(geom, vertices, morph=True, strength=1.0):
  vdata_src = geom.modifyVertexData()
  vdata_dst = vertices.getVertexData()
  return(processVertexData(vdata_src, vdata_dst, morph))

def processGeomNode(geomNode, morphNode, morph=True, strength=1.0):
  morphgeom = morphNode.getGeom(0)
  geom = geomNode.modifyGeom(0)
  state = geomNode.getGeomState(0)
  result = processGeom(geom, morphgeom, morph)

def setVertex(nodepath, morphnodepath, morph=True, strength=1.0):
  morphNode = morphnodepath.node()
  geomNodeCollection = nodepath.findAllMatches('**/Body/+GeomNode')
  for nodePath in geomNodeCollection:
    print(u'%s' % nodePath.getName().replace(u'\u30fb', u'.'))
    geomNode = nodePath.node()
    processGeomNode(geomNode, morphNode, morph)
  pass

def setExpression(model, expression, morph=True, strength=1.0):
  morph = model.find('**/Morphs*')
  for item in morph.getChildren():
    if item.getName() == expression:
      print(u'===================\n%s\n===================' % expression)
      lastExpression = model.getPythonTag('lastExpression')
      if lastExpression:
        setVertex(model, lastExpression, morph=False)
      setVertex(model, item, morph=True, strength=1.0)
      model.setPythonTag('lastExpression', item)
      break
    pass
  pass

def menuMorphSel(arg):
  setExpression(lastModel, arg)

def setUI(render):
  UI = NodePath('GUI')

  # btnReset = DirectButton(pos=(480,480), text=u'RESET', text_pos=(10,10), frameSize=(460, 460, 80, 80))
  btnSnapshot = DirectButton(text=u'截屏', scale=.05, pos=(-0.935, -10, 0.938), command=snapshot)
  btnSnapshot.setName('btnSnapShot')
  btnSnapshot.reparentTo(UI)

  btnAxisReset = DirectButton(text=u'复位', scale=.05, pos=(-0.935, -10, 0.852), command=resetCamera)
  btnAxisReset.setName('btnAxisReset')
  btnAxisReset.reparentTo(UI)

  menuAxisSelect = DirectOptionMenu(text="网格", scale=0.05, pos=(-0.985, -10, -0.980),
    items=[u'Z轴线', u'X轴线', u'Y轴线', u'XY平面', u'YZ平面', u'XZ平面'],
    initialitem=0, highlightColor=(0.65,0.65,0.65,1), command=menuItemSel, textMayChange=0)
  menuAxisSelect.setName('menuAxisSelect')
  menuAxisSelect.reparentTo(UI)

  morphItems = []
  morph = render.find('**/Morphs*')
  if morph:
    for item in morph.getChildren():
      morphItems.append(item.getName())
  if len(morphItems)>0:
    menuMorphs = DirectOptionMenu(text="表情", scale=0.05, pos=(0.850, -10, -0.980),
      items=morphItems,
      initialitem=0, highlightColor=(0.65,0.65,0.65,1), command=menuMorphSel)

    menuMorphs.setName('menuMorphSelect')
    menuMorphs.reparentTo(UI)

  UI.reparentTo(aspect2d)
  return(UI)
  pass

class Viewer(ShowBase):
  def __init__(self, gw):
    self.gw = gw
    self.active_points = {}
    self.touch_images = {}
    self.touch_text = {}

    ShowBase.__init__(self)
    self.build()

  def build(self):
    pass

  pass

if __name__ == '__main__':
  # title = 'PMX/PMX file Viewer'
  # icon = 'viewpmx.ico'
  # setAppInfo(title, icon)

  base.openMainWindow(type = 'onscreen')

  mmdFile = u'./models/apimiku/Miku long hair.pmx'
  mmdFile = u'./models/cupidmiku/Cupid Miku.pmx'
  mmdFile = u'./models/meiko/meiko.pmx'

  if len(sys.argv) > 1:
    if len(sys.argv[1]) > 0:
      mmdFile = sys.argv[1]

  if SHOW_AXIS:
    setAxis(render)

  # pmodel = loader.loadModel('panda')
  # print(type(pmodel))

  ext = os.path.splitext(mmdFile)[1].lower()
  if ext in ['.pmd']:
    mmdModel = pmdLoad(mmdFile)
    if mmdModel:
      p3dnode = pmd2p3d(mmdModel)
  elif ext in ['.pmx']:
    mmdModel = pmxLoad(mmdFile)
    if mmdModel:
      p3dnode = pmx2p3d(mmdModel)
      morphs = loadPmxMorph(mmdModel)
      morphs.reparentTo(p3dnode)

  p3dnode.reparentTo(render)
  lastModel = p3dnode

  if morphs:
    morph = morphs.find('*')
    print(u'%s' % morph.getName().replace(u'\u30fb', u'.'))

  if DEBUG:
    p3dnode.showTightBounds()

  lights = setStudioLight(render)
  lightAtNode(p3dnode, lights=lights)

  resetCamera()
  # base.screenshot(namePrefix='snap_', defaultFilename=p3dnode.getName())

  # render.setAntialias(AntialiasAttrib.MMultisample, 8)
  render.setAntialias(AntialiasAttrib.MAuto)

  # Shader.load(Shader.SLGLSL, './shader_v.sha', './shader_f.sha' )
  # render.setShader(Shader.load("inkGen.sha"))
  # render.setShaderAuto()

  # filters = CommonFilters(base.win, base.cam)
  # filters.setBloom()
  # filters.setCartoonInk()

  setUI(render)

  run()
