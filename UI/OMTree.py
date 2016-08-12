# -*- coding: utf-8 -*-

from OM.Manager import ObjectManager
import wx
import UI

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
        # TODO: Colocar pop-up menu com opções do que fazer com o objeto
        treeid = event.GetItem()
        uid, tid = self.GetPyData(treeid)
        #print('uid: {} - tid: {}'.format(uid, tid))
        if uid == self._PSEUDOROOTUID or tid is not None:
            event.Skip()
        #    print 'passou'
            return
        self._OM.remove(uid)
        """
        #menu = wx.Menu()
        tipo, _ = uid 
        menu_option_str = u'Excluir objeto [' + self._OM.get(uid).name + ']'
        #menu.Append(ID_EXCLUDE_OBJECT, menu_option_str)
        #self.Bind(wx.EVT_MENU, self.on_exclude, id=ID_EXCLUDE_OBJECT)
        #self.PopupMenu(menu, event.GetPoint())
        self.popupmenu = wx.Menu()            
        item = self.popupmenu.Append(-1, menu_option_str)
        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        self.Bind(wx.EVT_CONTEXT_MENU, self.OnShowPopup)  
        """

    def OnShowPopup(self, event):
        pos = event.GetPosition()
        pos = self.ScreenToClient(pos)
        self.PopupMenu(self.popupmenu, pos)
        self.popupmenu.Destroy()

    def OnPopupItemSelected(self, event):
        uid, tid = self.GetPyData(self.GetSelection())
        print('uid: {} - tid: {}'.format(uid, tid))
        self._OM.remove(uid)

 
 
    def on_exclude(self, event):
        treeid = event.GetItem()
        uid, tid = self.GetPyData(treeid)
        print('uid: {} - tid: {}'.format(uid, tid))        
        #self._OM.remove(uid)
        
    '''        
    def on_activated(self, event):
        treeid = event.GetItem()
        uid, treetid = self.GetPyData(treeid)
        if not uid == self._PSEUDOROOTUID:
            tid, oid = uid
            if tid == 'plotformat' and self.main_window:
                _, well_oid = self.selectedWelluid
                UI.UIManager.get().create_log_plot(well_oid, oid)
    '''            
                