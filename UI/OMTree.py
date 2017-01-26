# -*- coding: utf-8 -*-

from OM.Manager import ObjectManager
import wx


ID_EXCLUDE_OBJECT = wx.NewId()

class Tree(wx.TreeCtrl):  # TODO: tirar isso daqui
    _PSEUDOROOTUID = "__ROOT__"

    def __init__(self, *args, **kwargs):
        super(Tree, self).__init__(*args, **kwargs)

        self._OM = ObjectManager(self)
        
        self._rootid = self.AddRoot(u"ObjectManager")

        self._mapobjects = {}
        self._maptypes = {}

        self.SetPyData(self._rootid, (self._PSEUDOROOTUID, None))
        self._mapobjects[self._PSEUDOROOTUID] = self._rootid
        self._maptypes[self._PSEUDOROOTUID] = {}

        self._OM.addcallback('add', self.om_add_cb)
        self._OM.addcallback('post-remove', self.om_remove_cb)
        
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_rightclick)
        self.Bind(wx.EVT_TREE_SEL_CHANGED, self.on_selchanged)
        #self.Bind(wx.EVT_TREE_ITEM_ACTIVATED, self.on_activated)

        self.selectedWelluid = None        
        self.selectedCoreuid = None
        self.main_window = None
        
        
        #self.popupmenu = wx.Menu()            
        #item = self.popupmenu.Append(-1, menu_option_str)
        #self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        #self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)  
        
        
    # TODO: Alterar este armengue feito para permitir que controller chame
    #       o LogPlot passando main_window como parent. 
    # Essa bagaça deve ser alterada o quanto antes.    
    def set_main_window(self, main_window):
        self.main_window = main_window       
        
        
    def om_add_cb(self, objuid):
        obj = self._OM.get(objuid)
        parentuid = self._OM._getparentuid(objuid)
        if not parentuid:
            parentuid = self._PSEUDOROOTUID
        treeparentid = self._maptypes[parentuid].get(obj.tid)
        if not treeparentid:
            treeparentid = self.AppendItem(self._mapobjects[parentuid], obj.tid)
            self.SetPyData(treeparentid, (parentuid, obj.tid))
            self._maptypes[parentuid][obj.tid] = treeparentid
        newtreeid = self.AppendItem(treeparentid, obj.name)
        self.SetPyData(newtreeid, (obj.uid, None))
        self._mapobjects[obj.uid] = newtreeid
        self._maptypes[obj.uid] = {}

    def om_remove_cb(self, objuid):
        treeid = self._mapobjects[objuid]
        treeparentid = self.GetItemParent(treeid)
        parentuid, tid = self.GetPyData(treeparentid)

        if self.GetChildrenCount(treeid):
            return False
        del self._maptypes[objuid]
        del self._mapobjects[objuid]
        
        self.Delete(treeid)
        
        if not self.GetChildrenCount(treeparentid):
            del self._maptypes[parentuid][objuid[0]]
            self.Delete(treeparentid)

        return True
    
    
    def refresh(self):
        for uid, treeid in self._mapobjects.items():
            if uid == self._PSEUDOROOTUID:
                continue
            self.SetItemText(treeid, self._OM.get(uid).name)
  
  
    def on_selchanged(self, event):
        treeid = event.GetItem()
        uid, tid = self.GetPyData(treeid)
        if uid != self._PSEUDOROOTUID:   
            tid, oid = uid
            if tid == 'well':
                    self.selectedWelluid = uid
            elif tid == 'core':
                    self.selectedCoreuid = uid
            else:        
                parentuid = self._OM._getparentuid(uid)
                tid, oid = parentuid
                if tid == 'well':
                    self.selectedWelluid = parentuid
                else:    
                    self.selectedWelluid = None    
        else:
            self.selectedWelluid = None   
        return 
        
    
    def on_rightclick(self, event):
        treeid = event.GetItem()
        uid, tree_tid = self.GetPyData(treeid)
        if uid == self._PSEUDOROOTUID and tree_tid is None:
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
            menu_option_str = menu_option_str + str(self._OM.get(uid).name) + u']'
        self.popup_obj = (uid, tree_tid)
        self.popupmenu = wx.Menu()            
        item = self.popupmenu.Append(ID_EXCLUDE_OBJECT, menu_option_str)
        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        pos = event.GetPoint()
        self.PopupMenu(self.popupmenu, pos)


    def OnPopupItemSelected(self, event):
        uid, tree_tid = self.popup_obj
        if tree_tid is None:
            self._OM.remove(uid)
        else:
            if tree_tid == 'well':
                items = self._OM.list(tree_tid)
            else:    
                items = self._OM.list(tree_tid, uid)
            for item in items:
                self._OM.remove(item.uid)



 
                