# -*- coding: utf-8 -*-

from OM import ObjectManager
import wx

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
    
    def on_rightclick(self, event):
        return  # TODO: Colocar pop-up menu com opções do que fazer com o objeto
        treeid = event.GetItem()
        uid, tid = self.GetPyData(treeid)
        self._OM.remove(uid)
        
