# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 20:45:36 2018

@author: Adriano
"""

import gc
from collections import OrderedDict

import wx

import app
from app import log
from classes.base import GripyManager

from classes.ui import UIControllerObject


class UIManager(GripyManager):
    # tid = 'ui_manager'
    _data = OrderedDict()
    _types = OrderedDict()
    _currentobjectids = {}
    _parentuidmap = {}
    _childrenuidmap = {}
    _parenttidmap = {}
    _MVC_CLASSES = {}
    _wx_ID = 2000  # for a shortcut do wx.NewId. See self.new_wx_id  

    #    _PUB_NAME = 'UIManager'
    # _VALID_PUBSUB_TOPICS = ['uim', 'uim.object_removed']

    def __init__(self):
        super().__init__()
        self._data = UIManager._data
        self._types = UIManager._types
        self._currentobjectids = UIManager._currentobjectids
        self._parentuidmap = UIManager._parentuidmap
        self._childrenuidmap = UIManager._childrenuidmap
        self._parenttidmap = UIManager._parenttidmap
        self._MVC_CLASSES = UIManager._MVC_CLASSES

    #    def get_root_controller(self):
    #        main_ctrl_view = wx.App.Get().GetTopWindow()
    #        controller_uid = main_ctrl_view._controller_uid
    #        return self.get(controller_uid)

    #### Remover isso assim que possivel
    def print_info(self):
        print('\nUIManager.print_info:')
        print('UIManager._data: ', UIManager._data)
        # print ('UIManager._types: ', UIManager._types)
        # print ('UIManager._currentobjectids: ', UIManager._currentobjectids)
        print('UIManager._parentuidmap: ', UIManager._parentuidmap)
        print('UIManager._childrenuidmap: ', UIManager._childrenuidmap)
        print('UIManager._parenttidmap: ', UIManager._parenttidmap)
        # print ('UIManager._MVC_CLASSES: ', UIManager._MVC_CLASSES)

    ####

    @classmethod
    def register_class(cls, controller_class, view_class,
                       controller_parent_class=None):
        #
        if controller_class is None:
            msg = "Controller class cannot be None"
            log.exception(msg)
            raise TypeError(msg)
        #    
        if not issubclass(controller_class, UIControllerObject):
            msg = "Controller class must inherit from UIControllerObject."
            log.exception(msg)
            raise TypeError(msg)
            #
        cls._types[controller_class.tid] = controller_class
        cls._currentobjectids[controller_class.tid] = 0
        #
        if view_class is not None:
            view_class_tid = view_class.tid
            if view_class_tid not in cls._types.keys():
                cls._types[view_class_tid] = view_class
                cls._currentobjectids[view_class_tid] = 0
        else:
            view_class_tid = None
        #    
        if controller_class.tid not in cls._MVC_CLASSES.keys():
            cls._MVC_CLASSES[controller_class.tid] = view_class_tid
        else:
            if view_class_tid != cls._MVC_CLASSES.get(controller_class.tid):
                msg = 'Cannot register another view for controller {}'.format(controller_class.tid)
                log.exception(msg)
                raise Exception(msg)
        #        
        if controller_parent_class:
            try:
                if controller_parent_class.tid is None:
                    msg = "Controller parent class tid cannot be None."
                    log.exception(msg)
                    raise TypeError(msg)
                if controller_parent_class.tid not in cls._MVC_CLASSES.keys():
                    msg = "Type {} is not registered".format(controller_parent_class.tid)
                    log.exception(msg)
                    raise TypeError(msg)
                parent_class = cls._types.get(controller_parent_class.tid)
                if not issubclass(parent_class, UIControllerObject):
                    msg = "Type {} is not instance of UIControllerObject.".format(controller_parent_class)
                    log.exception(msg)
                    raise TypeError(msg)
            except Exception:
                raise
            controller_parent_class_tid = controller_parent_class.tid
        else:
            controller_parent_class_tid = None
            #
        if controller_class.tid not in cls._parenttidmap.keys():
            cls._parenttidmap[controller_class.tid] = [controller_parent_class_tid]
        else:
            cls._parenttidmap.get(controller_class.tid).append(controller_parent_class_tid)
        #    
        class_full_name = str(controller_class.__module__) + '.' + \
                          str(controller_class.__name__)
        if controller_parent_class:
            parent_full_name = str(controller_parent_class.__module__) + '.' + \
                               str(controller_parent_class.__name__)
            log.info('UIManager registered class {} for parent class {} successfully.'.format(class_full_name,
                                                                                              parent_full_name))
        else:
            log.info('UIManager registered class {} successfully.'.format(class_full_name))
        return True

    def get(self, uid):
        if isinstance(uid, str):
            uid = app.app_utils.parse_string_to_uid(uid)
        return self._data.get(uid)
        # return self._data[uid]

    # Something like a mix between new and add in ObjectManager
    # Object Factory        
    def create(self, controller_tid,
               parent_uid=None, **base_state):
        try:
            class_ = self._check_controller_tid(controller_tid)
        except Exception as e:
            log.exception('Error during calling UIManager.create({}, {})'.format(controller_tid, parent_uid))
            raise e
        if parent_uid is None:
            parent_obj = parent_tid = None
        else:
            parent_obj = self.get(parent_uid)
            parent_tid = parent_obj.tid
        if parent_tid not in self._parenttidmap.get(controller_tid):
            msg = "Parent object given ({}) is not a instance of {} parent class.".format(parent_tid, controller_tid)
            raise TypeError(msg)
        if class_._singleton:
            objs = self.list(controller_tid)
            if len(objs) > 0:
                msg = 'Cannot create more than one object stated as Singleton.'
                raise Exception(msg)
        if class_._singleton_per_parent:
            objs = self.list(controller_tid, parent_uid)
            if len(objs) > 0:
                msg = 'Cannot create more than one per parent object stated as Singleton per parent.'
                raise Exception(msg)
        try:
            obj = class_(**base_state)
        except Exception:
            msg = 'ERROR found in Controller {} creation.'.format(class_.__name__)
            log.exception(msg)
            raise
        self._data[obj.uid] = obj
        self._parentuidmap[obj.uid] = parent_uid
        self._childrenuidmap[obj.uid] = []
        if parent_uid:
            self._childrenuidmap[parent_uid].append(obj.uid)
        try:
            obj._create_view()
        except Exception as e:
            print(e)
            msg = 'ERROR found in View creation for class {}.'.format(class_.__name__)
            log.exception(msg)
            raise
        try:
            obj._PostInit()
        except Exception:
            msg = 'Error found in {}._PostInit(). Object was not created.'.format(obj.__class__.__name__)
            log.exception(msg)

        self.send_message('create', objuid=obj.uid, parentuid=parent_uid)
        return obj

    def new_wx_id(self):
        """
        TODO: Traduzir e melhorar isso
        
        Um metodo atalho para wx.NewID(), porém mantendo a sequencia dos Ids 
        dentro do UI Manager.
        
        P.S.: A sequencia dos Ids no wx.NewId() é perdida quando se chama de diversos modulos.
        """
        ret_val = self.__class__._wx_ID
        self.__class__._wx_ID += 1

        return ret_val

    def _isvalidparent(self, objuid, parentuid):
        """
        Verify if a given parent is suited for an object using their `uid`s.
        
        The verification is done by checking if the object type has the parent
        object type as its parent type.
        
        Parameters
        ----------
        objuid : uid
            The unique identificator of the object to check if the given parent
            is valid.
        parentuid : uid
            The unique identificator of the parent object to check if it is a
            valid parent for the given object.
        
        Returns
        -------
        bool
            Whether the parent is valid for the object.
        """
        objtid = objuid[0]
        if parentuid is None:
            parenttid = None
        else:
            parenttid = parentuid[0]
        return self._parenttidmap[objtid] == parenttid

    def _getparentuid(self, uid):
        """
        Return the parent unique identificator.
        
        Parameters
        ----------
        uid : uid
            The unique identificator for the object whose parent unique
            identificator is needed.
        
        Returns
        -------
        uid
            The unique identificator of the object's parent.
        """
        return self._parentuidmap.get(uid)

    def _prepare_object_for_deletion(self, obj):
        """
        """
        try:
            # With detach, controller will not receiver messages of object 
            # deletion from ObjectManager. 
            obj.detach()

            # Unsubscribing listeners from controller, this implies controller
            # will not send messages anymore.
            obj.unsubAll()

            # PreDelete must close (delete) all references 
            # from controller's parent.    
            obj.PreDelete()
        except:
            raise

    # Before exit application
    def PreExit(self):
        #        print ('\nUIManager PreExit')
        for obj in self.list():
            self._prepare_object_for_deletion(obj)

            try:
                obj.view.unsubAll()
                obj.view.PreDelete()
            except AttributeError:
                pass
            except Exception as e:
                print('\n\nERROR with object {}: {} \n\n'.format(obj.uid, e))
                raise

    def remove(self, uid):
        msg = 'Removing object from UI Manager: {}.'.format(uid)
        log.debug(msg)
        #        print ('\n' + msg)

        self.send_message('pre_remove', objuid=uid)
        obj = self.get(uid)
        if not isinstance(obj, UIControllerObject):
            return False

        for childuid in self._childrenuidmap.get(uid)[::-1]:
            self.remove(childuid)

        self._prepare_object_for_deletion(obj)

        if obj.view:
            msg = 'Deleting UI view object {}.'.format(obj.view.uid)
            #            print (msg)
            log.debug(msg)

            #            try:
            obj.view.unsubAll()
            obj.view.PreDelete()

            # TODO: rever se este eh o melhor caminho....
            if isinstance(obj.view, wx.Window):
                obj.view.Destroy()
            else:
                del obj.view
        #            except Exception as e:
        #                print ('ERROR:', obj.uid, e)

        # Removing from _childrenuidmap    
        parent_uid = self._parentuidmap.get(uid)
        if parent_uid:
            self._childrenuidmap.get(parent_uid).remove(uid)
        del self._childrenuidmap[uid]
        # Removing from _parentuidmap
        del self._parentuidmap[uid]
        # And from _data
        del self._data[uid]
        msg = 'Deleting UI controller object {}.'.format(uid)
        # print msg
        log.debug(msg)
        # Finally, deletes the controller
        del obj
        gc.collect()
        self.send_message('post_remove', objuid=uid)
        msg = 'UI Manager removed sucessfully {}.'.format(uid)
        log.debug(msg)
        #        print (msg)
        return True

    def reparent(self, uid, new_parent_uid):
        print('UIM.reparent:', uid, new_parent_uid)
        if uid not in self._data:
            raise Exception('uid={} is not a UIManager object.'.format(uid))
        if new_parent_uid not in self._data:
            raise Exception('New parent uid={} is not a UIManager object.'.format(new_parent_uid))
        obj = self._data[uid]

        if new_parent_uid[0] not in self._parenttidmap.get(uid[0], None):
            raise Exception('New parent tid={} not registered as {} parent.'.format(new_parent_uid.tid,
                                                                                    obj.__class__.__name__)
                            )

        #
        old_parent_uid = self._parentuidmap[uid]
        self._parentuidmap[uid] = new_parent_uid
        #
        self._childrenuidmap[old_parent_uid].remove(uid)
        self._childrenuidmap[new_parent_uid].append(uid)
        # Make obj.view do the wx reparent
        obj.view.reparent(old_parent_uid, new_parent_uid)

    # TODO: escolher um melhor nome para este método
    def close(self):
        msg = 'UI Manager has received a close call.'
        log.info(msg)
        print(msg)
        # print
        # self.print_info()
        for top_level_uid in self._get_top_level_uids():
            print('Removing ' + str(top_level_uid))
            self.remove(top_level_uid)
        # msg = 'ENDS.'
        # log.info(msg)
        # print ('\n' + msg)
        # print
        #        self.print_info()
        msg = 'UI Manager has closed.'
        log.info(msg)
        print(msg + '\n')

    def _get_top_level_uids(self):
        return [uid for uid, puid in UIManager._parentuidmap.items() if puid is None]

    def _gettype(self, tid):
        """
        Return the type (i.e. the class) that has the given `tid`.
        
        Parameters
        ----------
        tid : str
            The type identificator for the desired type.
        
        Returns
        -------
        type
            The type that has `tid` as its identificator.
        """
        return self._types.get(tid)

    def get_view_class(self, controller_tid):
        try:
            self._check_controller_tid(controller_tid)
        except:
            raise
        view_tid = self._MVC_CLASSES.get(controller_tid)
        if view_tid is None:
            view_class = None
        else:
            view_class = self._gettype(view_tid)
        return view_class

    def _check_controller_tid(self, controller_tid):
        if controller_tid is None:
            msg = "Controller tid cannot be None."
            raise TypeError(msg)
        if controller_tid not in self._MVC_CLASSES.keys():
            msg = "Type {} is not registered".format(controller_tid)
            raise TypeError(msg)
        class_ = self._gettype(controller_tid)
        if not issubclass(class_, UIControllerObject):
            msg = "Type {} is not instance of UIControllerObject.".format(controller_tid)
            raise TypeError(msg)
        return class_

    def _getnewobjectid(self, object_tid):
        """
        Return a new object identifier for the desired tid.
        
        Parameters
        ----------
        object_tid : str
            The type identifier whose a new object identifier is needed.
        
        Returns
        -------
        idx : int
            A new unique object identifier for a given tid.
        """
        idx = self._currentobjectids[object_tid]
        self._currentobjectids[object_tid] += 1
        return idx

    # TODO:
    # DAQUI PARA BAIXO PRECISA SER REVISTO
    # 
    """
    def get_application_state(self, start_from_obj_uid=None):
        if start_from_obj_uid is None:
            obj_uid, obj = list(self._data.items())[0]
            objects = [obj]
        else:
            objects = [self.get(start_from_obj_uid)]          
        for obj in objects:

            obj_state = OrderedDict()
            else:
                obj_state = obj.get_application_state()
                if obj_state.has_key('children'):
                    msg = obj.__class__.__name__ + ' cannot have an attribute called ''children''.'
                    raise AttributeError(msg)
            obj_state['children'] = []
            for obj_child_uid in self.get_children_uids(obj.uid):
                obj_state.get('children').append(self.get_application_state(obj_child_uid))
        return {obj.tid: obj_state}
        
        
    def get_user_state(self, start_from_obj_uid=None):
        if not start_from_obj_uid:
            root_obj_uid, _ = list(self._data.items())[0]
            root_obj_tid, _ = root_obj_uid
            objects = self.list(root_obj_tid)
        else:
            objects = [self.get(start_from_obj_uid)]  
        
        states = []        
        for obj in objects:
            if not obj.model: 
                obj_state = OrderedDict()
            else:
                obj_state = obj.get_user_state()
            #    if obj_state.has_key('children'):
            #        msg = obj.__class__.__name__ + ' cannot have an attribute called ''children''.'
            #        raise AttributeError(msg)
            obj_state['children'] = []
            for obj_child_uid in self.get_children_uids(obj.uid):
                obj_state.get('children').append(self.get_user_state(obj_child_uid))
            states.append(obj_state)    
        return {obj.tid: states}
        
        
    def _load_application_state(self, state, parent_uid=None):  
        for obj_tid, obj_state in state.items():
            try:
                if obj_state:
                    children = obj_state.pop('children')
                    new_created_obj = self.create(obj_tid, parent_uid=parent_uid, **obj_state)
                    for child in children:
                        self._load_application_state(child, new_created_obj.uid)
                else:
                    self.create(obj_tid, parent_uid=parent_uid) 
            except Exception:
                msg = 'ERROR in loading UI state.'
                log.exception(msg)
                raise
              

    def _load_user_state(self, state):  
        #self.print_info()
        print ('\n_load_user_state')
        
        for obj_tid, objects_state in state.items():
            print
            print obj_tid
            print len(objects_state), objects_state
            objects = self.list(obj_tid)
            for i in range(len(objects_state)):
                obj = objects[i]
                obj_state = objects_state[i]
                for key, value in obj_state.items():
                    print ('\n', key, value, type(value))
                    obj.model[key] = value
                    
            '''
            try:
                if obj_state:
                    children = obj_state.pop('children')
                    new_created_obj = self.create(obj_tid, **obj_state)
                    for child in children:
                        self._load_application_state(child, new_created_obj.uid)
            except Exception:
                msg = 'ERROR in loading UI state.'
                log.exception(msg)
                raise
            '''        

    def load_application_state_from_file(self, fullfilename):
        msg = 'Loading Gripy application UI from file {}'.format(fullfilename)
        print msg
        log.debug(msg)
        _state = App.app_utils.read_json_file(fullfilename)
        self._load_application_state(_state)        
        msg = 'Gripy application UI loaded.'
        print msg
        log.debug(msg)
 
 
    def load_user_state_from_file(self, fullfilename):
        msg = 'Loading Gripy user UI session from file {}'.format(fullfilename)
        print msg
        log.debug(msg)
        _state = App.app_utils.read_json_file(fullfilename)
        self._load_user_state(_state)        
        msg = 'Gripy user UI session loaded.'
        print msg
        log.debug(msg)
 

      

    def save_application_state_to_file(self, fullfilename):
        try:
            state = self.get_application_state()
        except Exception:
            state = None
            msg = 'ERROR: UI Application State cannot be gotten from UI Manager.' 
            log.exception(msg)
        if state is not None: 
            try:
                App.app_utils.write_json_file(state, fullfilename)
                msg = 'Gripy interface state was saved to file ' + fullfilename 
                print msg
                log.info(msg)
            except Exception:
                raise
        
        
    def save_user_state_to_file(self, fullfilename):
        try:
            state = self.get_user_state()
        except Exception:
            state = None
            msg = 'ERROR: UI Application State cannot be gotten from UI Manager.' 
            log.exception(msg)
        if state is not None: 
            try:
                App.app_utils.write_json_file(state, fullfilename)
                msg = 'Gripy interface state was saved to file ' + fullfilename 
                print msg
                log.info(msg)
            except Exception:
                raise        
        
    """
