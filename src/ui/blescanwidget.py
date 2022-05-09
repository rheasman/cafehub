from typing import Any
import kivy
kivy.require('1.9.1')  # type: ignore

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.treeview import TreeView, TreeViewNode, TreeViewLabel
from kivy.uix.label import Label
from kivy.logger import Logger

from ble.blescanresult import BLEScanResult

class BLEScanNode(BoxLayout, TreeViewNode):
  def __init__(self, item: BLEScanResult, **kwargs : Any):
    super(BLEScanNode, self).__init__(**kwargs)
    self.orientation = 'horizontal'
    self.is_open = True

    # Add a horizontal row of MAC, Name, Connect button
    self.add_widget(Label(text = item.MAC, font_size='18sp'))
    name = item.name
    if name == None:
      name = 'No name'

    self.add_widget(Label(text = name, font_size='18sp'))
    #self.bind(on_touch_down = self.cb_on_press)

  def on_touch_down(self, touch):
    Logger.info("UI: BLEScanNode.on_touch_down(%s)" % touch)
    if self.collide_point(*touch.pos):
      Logger.info("UI: Pressed")
      return True # Tell Kivy to stop processing this touch event
    return super(BLEScanNode, self).on_touch_down(touch)

class BLEScanWidget(BoxLayout):
  def __init__(self, **kwargs):
    super(BLEScanWidget, self).__init__(**kwargs)
    self.init()
    self.NodeItems = {}


  def init(self):
    self.TreeViewRoot = TreeView(root_options={
      'text': 'BLE Devices',
      'font_size': '18sp'
      })
    self.DE1sNode  = self.TreeViewRoot.add_node(TreeViewLabel(text='DE1s', font_size='18sp', is_open=True))
    self.OtherNode = self.TreeViewRoot.add_node(TreeViewLabel(text='Other', font_size='18sp', is_open=True))
    self.add_widget(self.TreeViewRoot)

  def addDE1Node(self, item):
    self.NodeItems[item.MAC] = item
    tvr = self.TreeViewRoot

    tvr.add_node(BLEScanNode(item), self.DE1sNode)

  def addOtherNode(self, item):
    self.NodeItems[item.MAC] = item
    tvr = self.TreeViewRoot

    tvr.add_node(BLEScanNode(item), self.OtherNode)