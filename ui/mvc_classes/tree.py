# -*- coding: utf-8 -*-

import os
from collections import OrderedDict

import wx

import app
from basic.uom import uom
from classes.om import ObjectManager
from classes.ui import UIManager
from classes.ui import UIControllerObject 
from classes.ui import UIViewObject 
from app import log 

#
# Root
# Has no ItemData
#
# Object
# self.view.SetItemData(obj_tree_item, (ID_TYPE_OBJECT, obj_uid, None))
#
# Tid
# self.view.SetItemData(tid_tree_item, (ID_TYPE_TID, obj_tid, parent_uid))
#
# Attribute
# self.view.SetItemData(attr_tree_item, (ID_TYPE_ATTRIBUTE, obj_uid, attr_name))


ID_TYPE_OBJECT = 0
ID_TYPE_TID = 1
ID_TYPE_ATTRIBUTE = 2


class TreeController(UIControllerObject):
    tid = 'tree_controller'
    _DEFAULT_ROOT_NAME = u"GRIPy Project"
    
    
    def __init__(self): 
        super(TreeController, self).__init__()
        
    def PostInit(self):
        OM = ObjectManager()
        OM.subscribe(self._on_OM_object_added, 'add')
        OM.subscribe(self._on_OM_object_removed, 'post_remove')

    def PreDelete(self): 
        OM = ObjectManager()
        OM.unsubscribe(self._on_OM_object_added, 'add')
        OM.unsubscribe(self._on_OM_object_removed, 'post_remove')
        
          
        
    def _on_OM_object_added(self, objuid):  
        OM = ObjectManager()
        obj = OM.get(objuid)
        obj.subscribe(self.teste, 'change')
        self.create_object_node(objuid)


    def _on_OM_object_removed(self, objuid):  
        OM = ObjectManager()
        obj = OM.get(objuid)
        obj.unsubscribe(self.teste, 'change')
        self.remove_object_node(objuid)

    
    def teste(self, old_value, new_value, topic=app.pubsub.AUTO_TOPIC):
        key = topic.getName().split('.')[2]
        print ('\nTESTE:',topic.getName(), key, old_value, new_value)
        
        
        
        
    def create_object_node(self, objuid):
        OM = ObjectManager()
        obj = OM.get(objuid)

        
#        print ('\n\ncreate_object_node', objuid)
        ####
        #   VERIFICA SE O OBJETO DEVE SER INCLUIDO NA ÁRVORE (NAO EH O TID!)
        #   O TID EH VERIFICADO PELA FUNCAO _is_tree_tid_node_needed ABAIXO.
        #
        
        node_props = obj._get_tree_object_node_properties()
        if node_props is None:
            return
        
        #print ()
#        print ('node_props:', node_props)
 
        try:
            parentuid = OM._getparentuid(objuid)
            # Find location to create tid node
            
#            print ('\nparentuid:', parentuid)
            
            
            if obj._is_tree_tid_node_needed():
                
#                print ('\n\n1 - PROCURANDO TID:', objuid[0], 
#                                           'FILHO DE:', parentuid
#                )
                
                # Then, tid node will be object node parent
                obj_parent_node = self.get_object_tree_item(ID_TYPE_TID, 
                                                        objuid[0], parentuid
                ) 
                
#                print ('\n\n2 - obj_parent_node:', obj_parent_node, ID_TYPE_TID, 
#                                                        objuid[0], parentuid)
                
                
#                PAREI AQUI!!!!!!
                
                
                if obj_parent_node is None:
                    
#                    print ('\n\n2 - NÃO ACHOU O TID')
                    
                    # It's necessary to create tid node
                    if parentuid is None:
                        # Create tid node as a root child
                        tid_parent_node = self.view.GetRootItem()
                    else:
                        # Create tid node as another object child
#                        print('\n\n\nBUSCANDO PAI DO TID_NODE:', 
#                                                ID_TYPE_OBJECT, parentuid
#                        )
                        tid_parent_node = self.get_object_tree_item(
                                                ID_TYPE_OBJECT, parentuid
                        ) 
#                        print('\n\n\ntid_parent_node:', tid_parent_node)
                        
#                        print(self.view.GetItemData(tid_parent_node))
                        
                        
#                    print('objuid[0]:', objuid[0])    
                    # Create tid node    
                    class_ = OM._gettype(objuid[0])
                    
#                    print('class_:', class_)
                    
                    
                    tid_label = class_._get_tid_friendly_name()

#                    print('PRE')
#                    print(str(tid_label))
#                    print('    Tree 1 - ' +  str(tid_parent_node) + ' ' + tid_label)
                    obj_parent_node = self.view.AppendItem(tid_parent_node, 
                                                         tid_label)    
                    self.view.SetItemData(obj_parent_node, 
                                          (ID_TYPE_TID, objuid[0], parentuid))
                    
#                    print ('Creating tid_node:',  (ID_TYPE_TID, objuid[0], parentuid))
                    
                    self.view.Expand(tid_parent_node)
            else:
#                print (3)
                #Create direct link to parent object
                obj_parent_node = self.get_object_tree_item(ID_TYPE_OBJECT, parentuid) 
            
            # Create object node itself
#            print ('node_props 2:', node_props)
            obj_repr = node_props.pop('name')
            #obj_repr, obj_props = node_props 
            obj_node = self.view.AppendItem(obj_parent_node, obj_repr)
            
            #
            # TODO: Consider create (ID_TYPE_OBJECT, objuid, ('ATTRIBUTE','name') vs
            #                       (ID_TYPE_OBJECT, objuid, ('FUNCTION', 'function_name')
            # For objects and attributes
            #
            
            self.view.SetItemData(obj_node, (ID_TYPE_OBJECT, objuid, 'name'))
#            print ('Creating obj_node:', (ID_TYPE_OBJECT, objuid, 'name'))
            self.view.Expand(obj_parent_node)

#            print ()
            # Create item object attributes
            for attr, attr_label in node_props.items():
#                print ('Creating attr_node:',  (ID_TYPE_ATTRIBUTE, objuid, attr)) 
                attr_node = self.view.AppendItem(obj_node, attr_label)
                self.view.SetItemData(attr_node, (ID_TYPE_ATTRIBUTE, objuid, attr))      
#                print ('Creating attr_node:',  (ID_TYPE_ATTRIBUTE, objuid, attr))   
            #
            
            self.view.Expand(obj_node)
        
        except Exception as e:
            print ('\nERRO ARVORE:', e)
            raise    



    def remove_object_node(self, objuid):
        try:
            treeitem = self.get_object_tree_item(ID_TYPE_OBJECT, objuid)
            if treeitem is None:
                raise Exception('Removing treeitem for an object not exists.')
            #        
            treeitem_parent = self.view.GetItemParent(treeitem)
            parent_node_type, _, _ = self.view.GetItemData(treeitem_parent)
            self.view.Delete(treeitem)
            #
            if (parent_node_type == ID_TYPE_TID) and not (self.view.GetChildrenCount(treeitem_parent)):
                # If parent node is a tid node and there is no other child, del it!
                self.view.Delete(treeitem_parent)
        except:
            raise   
            
            
    
    def get_object_tree_item(self, node_type, node_main_info, 
                                 node_extra_info=None, start_node_item=None):
        """Returns the wx.TreeItemId associated with Tree data given.
        """
#        print ('\nget_object_tree_item:', node_type, node_main_info, 
#                                           node_extra_info, start_node_item)
        
        try:
            if start_node_item is None:
                start_node_item = self.view.GetRootItem()
                
            start_node_data = self.view.GetItemData(start_node_item)
            
#            print ('111', start_node_item, start_node_data)

                
            if start_node_data is not None:
                    
                if node_type == ID_TYPE_OBJECT:
                    _, obj_uid, _ = start_node_data
                    if obj_uid == node_main_info:
                        # We found the TreeItem (Object)
                        return start_node_item
                    
                elif start_node_data == (node_type, node_main_info, node_extra_info):
                    # We found the TreeItem (Tid or Object attribute)
                    return start_node_item      
                
            # Let's search in children
            (child_item, cookie) = self.view.GetFirstChild(start_node_item)
            
            while child_item.IsOk():
                ret_child_val = self.get_object_tree_item(node_type, 
                                node_main_info, node_extra_info, child_item)
                if ret_child_val is not None:
                    return ret_child_val         
                (child_item, cookie) = self.view.GetNextChild(start_node_item,
                                                                        cookie)
            
#            print('RETORNOU NONE!!!!')
            
            return None       
        
        except Exception as e:
            print('\nERROR: get_object_tree_item:', e)
        #except:
            raise
                
            
    # TODO: Verificar isso        
    def set_project_name(self, name=wx.EmptyString):
        if name:
            _, name = os.path.split(name)      
        self.view._set_project_name(name)        



    def reload_object_node(self, objuid):
        try:
            self.remove_object_node(objuid)
        except:
            raise
        try:    
            self.create_object_node(objuid)
        except:
            raise
            
        """
        obj_node = self.get_object_tree_item(ID_TYPE_OBJECT, objuid)
        if not obj_node:
            raise Exception('Trying to reload an object not exists.')
        #self.view.DeleteChildren(treeitem)
        self.view.SetItemText(obj_node, self._get_object_label(objuid))
        #self._create_object_attributes(objuid)        
        """



        
        




     
              


class TreeView(UIViewObject, wx.TreeCtrl):
    tid = 'tree'
    
    def __init__(self, controller_uid):
        UIViewObject.__init__(self, controller_uid)
        UIM = UIManager()
#        controller = UIM.get(self._controller_uid)
        parent_controller_uid = UIM._getparentuid(self._controller_uid)
        parent_controller =  UIM.get(parent_controller_uid)  
        
        wx.TreeCtrl.__init__(self, parent_controller.view, -1, wx.Point(0, 0), wx.Size(200, 250),
                           wx.TR_DEFAULT_STYLE | wx.NO_BORDER)
        
        
        self._rootid = self.AddRoot(wx.EmptyString)                  
        self._set_project_name() 
    
        #self.SetItemData(self._rootid, (controller._PSEUDOROOTUID, None))
        
        self.Bind(wx.EVT_TREE_ITEM_RIGHT_CLICK, self.on_rightclick)     
        
        '''
        imglist = wx.ImageList(16, 16, True, 2)
        imglist.Add(wx.ArtProvider_GetBitmap(wx.ART_FOLDER, wx.ART_OTHER, wx.Size(16,16)))
        tree.AssignImageList(imglist)
        items.append(tree.AppendItem(root, "Item 1", 0))
        '''
        parent_controller.view._mgr.AddPane(self, wx.aui.AuiPaneInfo().Name("tree").
                Caption("Object Manager").Left().Layer(1).Position(1).
                PinButton(True).MinimizeButton(True).
                CloseButton(False).MaximizeButton(True)
        )        
        parent_controller.view._mgr.Update()
        
        self.Bind(wx.EVT_TREE_BEGIN_DRAG, self._on_begin_drag) 



    def _set_project_name(self, name=wx.EmptyString):
        UIM = UIManager()
        controller = UIM.get(self._controller_uid)
        if name:          
            self._root_name = controller._DEFAULT_ROOT_NAME + ' [' + name + ']'
        else:
            self._root_name = controller._DEFAULT_ROOT_NAME
        self.SetItemText(self._rootid, self._root_name)   

              
        
    def _on_begin_drag(self, event):
        item = event.GetItem()
        #tree = event.GetEventObject()
        if item == self.GetRootItem():
            return   
        (node_type, node_main_info, node_extra_info) = self.GetItemData(item)
        
        if node_type != ID_TYPE_OBJECT: 
            return
        
        # Falta tratar Well
        def DoDragDrop():
            data_obj = wx.CustomDataObject('obj_uid')
            data_obj.SetData(str.encode(str(node_main_info)))
            drag_source = wx.DropSource(self)
            drag_source.SetData(data_obj)  
            drag_source.DoDragDrop()
            
        # TODO: Verificar se wx.CallAfter pode retornar
        # Motivo: wx.CallAfter não estava funcionando adequadamente em Gtk 
        # no DragAndDrop pois wx.DropSource.DoDragDrop retornava wx.DragNone
        # não permitia entrar no modo Dragging.
        # Essa foi a unica solução encontrada - Adriano - 22/3/2017
        if os.name == 'posix':
            DoDragDrop()
        else:    
            wx.CallAfter(DoDragDrop)



    def on_rightclick(self, event):
        tree_item = event.GetItem()
        if tree_item == self.GetRootItem():
            return
        item_data = self.GetItemData(tree_item)
        (node_type, node_main_info, node_extra_info) = item_data
        
        if node_type == ID_TYPE_ATTRIBUTE:    
            return
               
        self.popup_obj = (node_type, node_main_info, node_extra_info)
        self.popupmenu = wx.Menu()  
        
        OM = ObjectManager()
        
        if node_type == ID_TYPE_OBJECT:
            item = self.popupmenu.Append(wx.NewId(), 'Rename object')
            self.Bind(wx.EVT_MENU, self.OnRenameObject, item)
            self.popupmenu.AppendSeparator()
            if self._is_convertible(node_main_info):
                item = self.popupmenu.Append(wx.NewId(), 'Convert unit')
                self.Bind(wx.EVT_MENU, self.OnUnitConvert, item)
                self.popupmenu.AppendSeparator()
            # Exclude a specific object
            obj = OM.get(node_main_info)
            menu_option_str = 'Exclude object ['
            menu_option_str = menu_option_str + str(obj.name) + ']'    
            
        elif node_type == ID_TYPE_TID:  
            # Exclude all objects from a class
            menu_option_str = 'Exclude all objects [{}]'.format(node_main_info) 

        item = self.popupmenu.Append(wx.NewId(), menu_option_str)
        self.Bind(wx.EVT_MENU, self.OnPopupItemSelected, item)
        #
        pos = event.GetPoint()
        self.PopupMenu(self.popupmenu, pos)
     
        #elif node_type == ID_TYPE_ATTRIBUTE:    
        #    return

        

    def _is_convertible(self, uid):
        if uid[0] in ['log', 'data_index']:
            return True
        return False



    def OnPopupItemSelected(self, event):
        print ('OnPopupItemSelected', self.popup_obj)
        
        #tree_item = event.GetItem()
        #item_data = self.GetItemData(tree_item)
        
        
        (node_type, node_main_info, node_extra_info) = self.popup_obj
        OM = ObjectManager()
        
        if node_type == ID_TYPE_OBJECT:
            print ('ID_TYPE_OBJECT remove:', node_main_info)
            OM.remove(node_main_info)
            
        elif node_type == ID_TYPE_TID:  
            #if node_info == 'well':
            #    items = OM.list(node_main_info)
            #else:    
            items = OM.list(node_main_info, node_extra_info)
            for item in items:
                
                print ('ID_TYPE_TID remove:', item.uid)
                
                OM.remove(item.uid)
        print ('FIM OnPopupItemSelected')      


    def OnRenameObject(self, event):  
        (node_type, node_main_info, node_extra_info) = self.popup_obj
        OM = ObjectManager()       
        obj = OM.get(node_main_info)
        
        UIM = UIManager()
        dlg = UIM.create('dialog_controller', title='Rename object')        
        #
        try:        
            ctn_details = dlg.view.AddCreateContainer('StaticBox', label='Object details', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
            dlg.view.AddStaticText(ctn_details, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, label='Name: ' + obj.name)
            #
            dlg.view.AddStaticText(ctn_details, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, label='Type id: ' + obj.tid)
            dlg.view.AddStaticText(ctn_details, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, label='Object id: ' + str(obj.oid))
            #
            ctn_new_name = dlg.view.AddCreateContainer('StaticBox', label='New name', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)  
            dlg.view.AddTextCtrl(ctn_new_name, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='new_name', initial=obj.name)     
            #    
            dlg.view.SetSize((300, 330))
            answer = dlg.view.ShowModal()
            #
            if answer == wx.ID_OK:
                results = dlg.get_results()  
                new_name = results.get('new_name')
                obj.name = new_name
                UIM = UIManager()
                controller = UIM.get(self._controller_uid)
                controller.reload_object_node(obj.uid)                 
        except Exception as e:
            print ('\nERROR OnRenameObject:', e)
            raise
        finally:
            UIM.remove(dlg.uid)     


                          
    def OnUnitConvert(self, event):     
        (node_type, node_main_info, node_extra_info) = self.popup_obj
        OM = ObjectManager()       
        obj = OM.get(node_main_info)
        try:
            unit = uom.get_unit(obj.unit)
            dim = uom.get_unit_dimension(unit.dimension)
            qc = uom.get_quantity_class(dim.name)
            UNITS_OPTIONS = OrderedDict()
            for mu in qc.memberUnit:
                UNITS_OPTIONS[mu] = mu 
        except:    
            msg = 'Unit ' + obj.unit + ' cannot be converted.'
            wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_WARNING)
            return 
            #
        UIM = UIManager()
        dlg = UIM.create('dialog_controller', title='Unit conversion')        
        #
        try:
            ctn_details = dlg.view.AddCreateContainer('StaticBox', label='Object details', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)
            dlg.view.AddStaticText(ctn_details, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, label='Name: ' + obj.name)
            #
            dlg.view.AddStaticText(ctn_details, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, label='Type id: ' + obj.tid)
            dlg.view.AddStaticText(ctn_details, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, label='Object id: ' + str(obj.oid))
            dlg.view.AddStaticText(ctn_details, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, label='Current unit: ' + obj.unit)
            #
            ctn_new_unit = dlg.view.AddCreateContainer('StaticBox', label='New unit', orient=wx.VERTICAL, proportion=0, flag=wx.EXPAND|wx.TOP, border=5)  
            dlg.view.AddChoice(ctn_new_unit, proportion=0, flag=wx.EXPAND|wx.TOP, border=5, widget_name='new_unit', options=UNITS_OPTIONS)     
            #    
            dlg.view.SetSize((300, 330))
            answer = dlg.view.ShowModal()
            #
            if answer == wx.ID_OK:
                results = dlg.get_results()  
                new_unit_name = results.get('new_unit')
                new_data = uom.convert(obj.data, obj.unit, new_unit_name)
                obj._data = new_data
                obj.unit = new_unit_name            
#                UIM = UIManager()
#                controller = UIM.get(self._controller_uid)
#                controller.reload_object(obj.uid)                 
        except Exception:
            pass
        finally:
            UIM.remove(dlg.uid)        
            
        
        
        
        
        
        
        
        