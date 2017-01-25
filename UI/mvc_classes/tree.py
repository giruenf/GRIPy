# -*- coding: utf-8 -*-

import wx
import logging

from OM.Manager import ObjectManager
from UI.uimanager import UIManager
from UI.uimanager import UIControllerBase 
from UI.uimanager import UIViewBase 
import DT
 
      
class TreeController(UIControllerBase):
    tid = 'tree_controller'
    _singleton_per_parent = True
    _PSEUDOROOTUID = "__ROOT__"
    
    
    def __init__(self): 
        super(TreeController, self).__init__()


    def PostInit(self):
        self._mapobjects = {}
        self._maptypes = {}
        self._mapobjects[self._PSEUDOROOTUID] = self.view._rootid
        self._maptypes[self._PSEUDOROOTUID] = {} 
        self._OM = ObjectManager(self)
        self._OM.addcallback('add', self.om_add_cb)
        self._OM.addcallback('post-remove', self.om_remove_cb)
        #self._UIM = UIManager()
        #self.model.attributes['hidden'] = OrderedDict()   
 

    def set_project_name(self, name=wx.EmptyString):
        if name == wx.EmptyString:
            self.view._root_name = self.view._default_root_name    
        else:            
            self.view._root_name = self.view._default_root_name + ' [' + name + ']'
        self.view.SetItemText(self.view._rootid, self.view._root_name)              
        
        
    def om_add_cb(self, objuid):
        obj = self._OM.get(objuid)
        parentuid = self._OM._getparentuid(objuid)
        if not parentuid:
            parentuid = self._PSEUDOROOTUID
        treeparentid = self._maptypes[parentuid].get(obj.tid)  
        if not treeparentid:
            if obj._OM_TREE_PARENT_LABEL: 
                treeparentid = self.view.AppendItem(self._mapobjects[parentuid], obj._OM_TREE_PARENT_LABEL)
            else:  
                treeparentid = self.view.AppendItem(self._mapobjects[parentuid], obj.tid)
            self.view.SetPyData(treeparentid, (parentuid, obj.tid))
            self._maptypes[parentuid][obj.tid] = treeparentid
        if isinstance(obj, DT.DataTypes.DataTypeUnitMixin):    
            try:    
                obj_str = obj.name + ' (' + obj.unit + ')'    
            except AttributeError:
                obj_str = obj.name + ' (unitless)'
        else:
            obj_str = obj.name
        newtreeid = self.view.AppendItem(treeparentid, obj_str)
        self.view.SetPyData(newtreeid, (obj.uid, None))
        try:
            #attr_str = 'Object Id: ' + str(obj.oid)
            #attrtreeid = self.view.AppendItem(newtreeid, attr_str)
            #self.view.SetPyData(attrtreeid, (None, None))    
            for attr, attr_label in obj._OM_TREE_ATTR_SHOWN:
                attr_str = attr_label + ': ' + str(obj.attributes.get(attr, 'None'))
                attrtreeid = self.view.AppendItem(newtreeid, attr_str)
                self.view.SetPyData(attrtreeid, (None, None))
        except AttributeError:    
            pass
        self._mapobjects[obj.uid] = newtreeid
        self._maptypes[obj.uid] = {}
        #self.view.ExpandAll()
      

    def om_remove_cb(self, objuid):
        treeid = self._mapobjects[objuid]
        treeparentid = self.view.GetItemParent(treeid)
        parentuid, tid = self.view.GetPyData(treeparentid)
        if self.view.GetChildrenCount(treeid):
            return False
        del self._maptypes[objuid]
        del self._mapobjects[objuid]
        self.view.Delete(treeid)
        if not self.view.GetChildrenCount(treeparentid):
            del self._maptypes[parentuid][objuid[0]]
            self.view.Delete(treeparentid)
        #self.view.Expand(treeparentid)    
        return True        


        
    
    
class TreeView(UIViewBase, wx.TreeCtrl):
    tid = 'tree'
    _default_root_name = u"GRIPy Project"
    
    def __init__(self, controller_uid):
        UIViewBase.__init__(self, controller_uid)
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        parent_controller_uid = _UIM._getparentuid(self._controller_uid)
        parent_controller =  _UIM.get(parent_controller_uid)  
        
        wx.TreeCtrl.__init__(self, parent_controller.view, -1, wx.Point(0, 0), wx.Size(200, 250),
                           wx.TR_DEFAULT_STYLE | wx.NO_BORDER)

                         
                           
        self._root_name = self._default_root_name #+ ' (no wells)'                  
        self._rootid = self.AddRoot(self._root_name)
        self.SetPyData(self._rootid, (controller._PSEUDOROOTUID, None))
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_rightclick)        
        '''
        imglist = wx.ImageList(16, 16, True, 2)
        imglist.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16,16)))
        imglist.Add(wx.ArtProvider_GetBitmap(wx.ART_NORMAL_FILE, wx.ART_OTHER, wx.Size(16,16)))
        tree.AssignImageList(imglist)

        items.append(tree.AppendItem(root, "Item 1", 0))
        items.append(tree.AppendItem(root, "Item 2", 0))
        items.append(tree.AppendItem(root, "Item 3", 0))
        '''
        parent_controller.view._mgr.AddPane(self, wx.aui.AuiPaneInfo().Name("tree").
                Caption("Object Manager").Left().Layer(1).Position(1).
                PinButton(True).MinimizeButton(True).
                CloseButton(False).MaximizeButton(True)
        )        
        parent_controller.view._mgr.Update()
        
        
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self.on_begin_drag) 
        #self.Bind(wx.EVT_TREE_END_DRAG, self.on_end_drag)
      
      
    def on_begin_drag(self, event):
        item = event.GetItem()
        tree = event.GetEventObject()
        if item == tree.GetRootItem():
            return   
        uid, tree_tid = tree.GetPyData(item)
        print uid, tree_tid
        if tree_tid is not None:
            # Objects have tree_tid == None
            return
        if uid is None:
            # Object leaf properties
            return
        
        # Falta tratar Well
        
        def DoDragDrop():
            print 'start drag: ', uid, tree_tid            
            data_obj = wx.CustomDataObject('obj_uid')
            data_obj.SetData(str(uid))
            drag_source = wx.DropSource(tree)
            drag_source.SetData(data_obj)            
            drag_source.DoDragDrop()     
        wx.CallAfter(DoDragDrop)


  
    def on_rightclick(self, event):
        treeid = event.GetItem()
        uid, tree_tid = self.GetPyData(treeid)
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        if uid == controller._PSEUDOROOTUID and tree_tid is None:
            return    
        if tree_tid is not None:
            if tree_tid == 'well':
                menu_option_str = u'Excluir todos os poços' 
            elif tree_tid == 'log':
                menu_option_str = u'Excluir todas as curvas' 
            elif tree_tid == 'depth':
                menu_option_str = u'Excluir todos os depth'  
            elif tree_tid == 'partition':
                menu_option_str = u'Excluir todas as partições'      
            else:
                raise Exception('Curve type not recognized.')
        else:
            classid, oid = uid
            if classid == 'well':
                menu_option_str = u'Excluir poço [' 
            elif classid == 'log':
                menu_option_str = u'Excluir curva [' 
            elif classid == 'depth':
                menu_option_str = u'Excluir depth ['  
            elif classid == 'partition':
                menu_option_str = u'Excluir partição ['      
            else:
                raise Exception('Curve type not recognized.')
            menu_option_str = menu_option_str + str(controller._OM.get(uid).name) + u']'
        self.popup_obj = (uid, tree_tid)
        self.popupmenu = wx.Menu()            
        item = self.popupmenu.Append(wx.NewId(), menu_option_str)
        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        pos = event.GetPoint()
        self.PopupMenu(self.popupmenu, pos)


    def OnPopupItemSelected(self, event):
        uid, tree_tid = self.popup_obj
        _UIM = UIManager()
        controller = _UIM.get(self._controller_uid)
        if tree_tid is None:
            controller._OM.remove(uid)
        else:
            if tree_tid == 'well':
                items = controller._OM.list(tree_tid)
            else:    
                items = controller._OM.list(tree_tid, uid)
            for item in items:
                controller._OM.remove(item.uid)