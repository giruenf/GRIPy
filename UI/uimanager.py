# -*- coding: utf-8 -*-

import gc
import wx
import types
from collections import OrderedDict
import App.app_utils
from App import log
from App.pubsub import PublisherMixin
from App.gripy_manager import Manager
from OM.Manager import ObjectManager


###############################################################################
###############################################################################

class UI_MODEL_ATTR_CLASS(App.app_utils.GripyEnum):     
    APPLICATION = 1
    USER = 2

###############################################################################
###############################################################################

class UIBase(object):
    tid = None
    
    def __init__(self):
        self.check_creator()
        self.oid = None
      
    def PostInit(self):
        """To be overrriden"""
        pass

    def PreDelete(self):
        """To be overrriden"""
        pass

    @property
    def uid(self):
        return self.tid, self.oid
    
    @property
    def name(self): 
        return '{}.{}'.format(*self.uid)
   
    @name.setter
    def name(self, value):
        msg = "Cannot set UIBase object name."
        raise TypeError(msg)
    
    @name.deleter
    def name(self):
        msg = "Cannot delete UIBase object name."
        raise TypeError(msg)  
    
    def check_creator(self):
        # Only UIManager can create objects. Checking it!
        #print 'ZZZ'
        caller_info = App.app_utils.get_caller_info()
        #print 'ZZZ2:', caller_info
        #print
        ok = False
        for idx, ci in enumerate(caller_info):
            module_name = None
            module = ci[0]
            if module:
                module_name = module.__name__
            func_name = ci[2]
            if module_name and func_name:
                if module_name == 'UI.uimanager' and func_name == 'create':
                    ok = True
                    break     
        if not ok:
            msg = '{} objects must be created only by UIManager.'.format(self.__class__.__name__)
            log.exception(msg)
            raise Exception(msg)    

###############################################################################
###############################################################################
                                 

class UIControllerBase(UIBase, PublisherMixin):
    tid = None
    # TODO: verificar se vale a pena manter esses singletons
    _singleton = False
    _singleton_per_parent = False
       
    def __init__(self):
        super(UIControllerBase, self).__init__()  
        UIM = UIManager()
        self.oid = UIM._getnewobjectid(self.tid)
          

    def _create_model_view(self, **base_state): 
        UIM = UIManager()           
        model_class, view_class = UIM.get_model_view_classes(self.tid)
        if model_class is not None:
            try:
                self.model = model_class(self.uid, **base_state)
            except Exception, e:
                msg = '' #ERROR on creating MVC model {} object: {}'.format(model_class.__name__, e.message)
                log.exception(msg)
                print '\n', msg
                raise e
        else:
            self.model = None
        if view_class is not None:     
            try:
                self.view = view_class(self.uid)
            except Exception, e:
                msg = 'ERROR on creating MVC view {} object: {}'.format(view_class.__name__, e.message)
                log.exception(msg)
                print '\n', msg, view_class
                raise e             
        else:
            self.view = None  

        
    def _PostInit(self):
        try:
            if self.model:
                self.model.PostInit()
        except Exception, e:
            msg = 'ERROR in {}.PostInit: {}'.format(self.model.__class__.__name__, e.message)
            log.exception(msg)
            print '\n', msg
            raise
        try:    
            if self.view:        
                self.view.PostInit()
        except Exception, e:
            msg = 'ERROR in {}.PostInit: {}'.format(self.view.__class__.__name__, e.message)
            log.exception(msg)
            print '\n', msg
            raise
        try:                
            self.PostInit()    
        except Exception, e:
            msg = 'ERROR in {}.PostInit: {}'.format(self.__class__.__name__, e.message)
            log.exception(msg)
            print '\n', msg
            raise
        

    def _call_self_remove(self):
        UIM = UIManager()
        wx.CallAfter(UIM.remove, self.uid)
  
    
    def attach(self, OM_objuid):
        #print 'attach:', OM_objuid
        OM = ObjectManager(self)
        obj = OM.get(OM_objuid)
        try:
            # TODO: REVER ISSO
            obj.subscribe(self._call_self_remove, 'remove')
        except:
            pass
           
    def detach(self, OM_objuid):
        #print 'detach:', OM_objuid
        OM = ObjectManager(self)
        obj = OM.get(OM_objuid)
        try:
            # TODO: REVER ISSO
            obj.unsubscribe(self._call_self_remove, 'remove')        
        except:
            pass
        
        
    def get_state(self):
        if not self.model:
            return None 
        state = self.model._getstate()
        UIM = UIManager()
        children = UIM.list(parentuidfilter=self.uid)
        if children:
            state['children'] = []
            for child in children:
                state['children'].append(child.get_state())
        return self.tid, state
  
      
    # TODO: ver se deve-se manter o tid na chamada abaixo (@staticmethod)
    @staticmethod    
    def load_state(state, tid, parentuid=None):
        children = state.pop('children', None)
        UIM = UIManager()
        obj = UIM.create(tid, parentuid, **state)
        if children:
            for child_tid, child_state in children:
                UIControllerBase.load_state(child_state, child_tid, obj.uid)
        return obj
        

           
            
###############################################################################
###############################################################################    
    

class UIModelBase(UIBase):
    """
    The base class for all Model classes (MVC software architectural pattern).
        
    """
    tid = None
    # Special keys bypasses the checking made in __setattr__ or __setitem__
    _SPECIALS_KEYS = ['oid', 
                      '_controller_uid', 
                      '_UIModelBase__initialised',
                      '_processing_value_from_event',
                      '_redirects_to'
    ]

    def __init__(self, controller_uid, **state):
        # TODO: REVER NECESSIDADE DE 'attr_class' e DE 'base_attr'
        try:
            super(UIModelBase, self).__init__()
            self._controller_uid = controller_uid
            self.__initialised = False       
            self._processing_value_from_event = False
            UIM = UIManager()
            self.oid = UIM._getnewobjectid(self.tid) 
            # We are considering that only Controller class objects 
            # can create Model class objects. Then, we must verify it
            model_class = UIM.get_model_view_classes(controller_uid[0])[0]
            if self.__class__ != model_class:
                msg = 'Error! Only the controller can create the model.'
                raise Exception(msg)    
            for attr_name, attr_props in self._ATTRIBUTES.items():
                #if attr_props.get('attr_class') not in UI_MODEL_ATTR_CLASS.__members__.values():
                #    msg = '{}.{} has not a valid ''attr_class'' value: {}. Valid values are UI.uimanager.UI_MODEL_ATTR_CLASS members.'.format( \
                #        self.__class__.__name__, attr_name, 
                #        attr_props.get('attr_class')
                #    )
                #    print '\n', msg
                #if attr_props.get('attr_class') == UI_MODEL_ATTR_CLASS.APPLICATION \
                if state.has_key(attr_name):
                    self[attr_name] = state.get(attr_name)
                else:    
                    self[attr_name] = attr_props.get('default_value')                       
            self.__initialised = True
        except Exception as e:
            try:
                UIM = UIManager()
                UIM.remove(self._controller_uid)
            except:
                pass
            raise e
        
        
    def PostInit(self):
        pass

    def initialised(self):
        return self.__dict__.get('UIModelBase__initialised')

    def set_value_from_event(self, key, value):
        self._processing_value_from_event = True
        try:
            self._do_set(key, value)
        except: 
            raise
        finally:    
            self._processing_value_from_event = False

    def __getattr__(self, key):
        # http://docs.python.org/2/library/functions.html#getattr
        if self.__dict__.has_key('_redirects_to'):
            return self._redirects_to[key]
        raise AttributeError(key)

    def __setattr__(self, key, value):
        if key in self._SPECIALS_KEYS:
            self.__dict__[key] = value
            return
        self._do_set(key, value)

    def __getitem__(self, key):
        # http://docs.python.org/2/reference/datamodel.html#object.__getitem__
        try:
            return self.__dict__.get(key)
        except KeyError:
            raise AttributeError(key)

    def __setitem__(self, key, value):
        self._do_set(key, value)

    def _do_set(self, key, value):
        if (not self.initialised() and not self._ATTRIBUTES.has_key(key)) or \
                       (self.initialised() and not self.__dict__.has_key(key)):
            msg = '{} does not have attribute {}.'.format(\
                                             self.__class__.__name__, str(key))
            if self.__dict__.has_key('_redirects_to'):
                self._redirects_to._do_set(key, value)
                return
            log.warning(msg)
            print msg
            return
        '''
        base_attr = self._ATTRIBUTES.get(key).get('base_attr')    
        if self.__initialised and base_attr:
            msg = 'Base attributes are only loaded before initialization. {}.{} = {}'.format(\
                self.__class__.__name__, str(key), str(value))
            log.warning(msg)
            return
        '''   
        type_ = self._ATTRIBUTES.get(key).get('type')

        # Special treatment for functions
        if type_ == types.FunctionType:
            if isinstance(value, basestring):
                value = App.app_utils.get_function_from_string(value)
            if value is not None and not callable(value):
                msg = 'ERROR: Attributes signed as \"types.FunctionType\" can recieve only \"str\" or \"types.FunctionType\" values. '
                msg += 'Received: {} - Type: {}'.format(value, type(value))
                log.error(msg)
                raise AttributeError(msg)
        elif not isinstance(value, type_):
            try:
                if value is not None:    
                    value = type_(value)
            except Exception:
                raise 
        if not self.__initialised:
            self.__dict__[key] = value
        else:    
            if self.__dict__[key] == value:
                return      
            old_value = self[key]    
            self.__dict__[key] = value
            if not self._processing_value_from_event:
                UIM = UIManager()
                controller = UIM.get(self._controller_uid)
                topic = 'change.' + key
                controller.send_message(topic, 
                                  old_value=old_value, 
                                  new_value=value
                )
        k = key.encode('utf-8')            
        v = self[key]
        if isinstance(v, basestring):        
            v = self[key]
            v = v.encode('utf-8')
        else:
            v = str(v)
        msg = '    {} has setted attribute {} = {}'.format(self.uid, k, v)       
        log.debug(msg)

    
    # TODO: VERIFICAR ISSO TUDO 
    """
    def get_application_state(self):
        return self.get_state(UI_MODEL_ATTR_CLASS.APPLICATION)
        
    def get_user_state(self):
        return self.get_state(UI_MODEL_ATTR_CLASS.USER)    
    """
    
    def _getstate(self, state_type=None):
        try:
            if state_type is not None and state_type not in \
                                    UI_MODEL_ATTR_CLASS.__members__.values():
                return None
            state = OrderedDict()                
            for attr_name in self.__dict__.keys(): 
                if attr_name not in self._SPECIALS_KEYS:
                    if state_type is None:
                        state[attr_name] = self[attr_name]
                    elif self._ATTRIBUTES.get(attr_name).get('attr_class') == state_type:
                        state[attr_name] = self[attr_name]
            return state            
        except Exception as e:
            print e
            print e.message

 
    def _loadstate(self, **state):
        if not state:
            return
        log.debug('Loading {} state...'.format(self.__class__.__name__))
        for key, value in state.items():
            if key not in self._SPECIALS_KEYS:     
                try:
                    self[key] = value  
                except AttributeError:
                    msg = 'ERROR setting self[{}] = {}. Value type: {}'.format(str(key), \
                        str(value), str(type(value))
                    )
                    log.exception(msg)
            else:
                msg = u'    ' + unicode(key) + ' cannot be loaded. [key in _SPECIALS_KEYS]'
                log.error(msg)
        log.debug('{} state has loaded.'.format(self.__class__.__name__))
     
     # TODO: FIM - VERIFICAR ISSO TUDO

###############################################################################
###############################################################################

class UIViewBase(UIBase):
    tid = None

    def __init__(self, controller_uid):
        UIBase.__init__(self)
        self._controller_uid = controller_uid
        UIM = UIManager()  
        self.oid = UIM._getnewobjectid(self.tid)
        # We are considering that only Controller class objects 
        # can create View class objects. Then, we must verify it       
        view_class = UIM.get_model_view_classes(controller_uid[0])[1]
        if self.__class__ != view_class:
            msg = 'Error! Only the controller can create the view.'
            log.exception(msg)
            raise Exception(msg)       

    def PostInit(self):
        pass
                
###############################################################################
###############################################################################


class UIManager(Manager):
    #tid = 'ui_manager'
    #__metaclass__ = Singleton

    _data = OrderedDict()
    _types = OrderedDict()
    _currentobjectids = {}
    _parentuidmap = {}
    _childrenuidmap = {}
    _parenttidmap = {}
    _MVC_CLASSES = {}
    _wx_ID = 2000  # for a shortcut do wx.NewId. See self.new_wx_id  
    _PUB_NAME = 'UIManager'
    #_VALID_PUBSUB_TOPICS = ['uim', 'uim.object_removed']

    def __init__(self):   
        super(UIManager, self).__init__()
        self._data = UIManager._data
        self._types = UIManager._types
        self._currentobjectids = UIManager._currentobjectids
        self._parentuidmap = UIManager._parentuidmap
        self._childrenuidmap = UIManager._childrenuidmap
        self._parenttidmap = UIManager._parenttidmap
        self._MVC_CLASSES = UIManager._MVC_CLASSES


    def get_root_controller(self):
        main_ctrl_view = wx.App.Get().GetTopWindow()
        controller_uid = main_ctrl_view._controller_uid
        return self.get(controller_uid)


    #### Remover isso assim que possivel
    def print_info(self):
        print '\nUIManager._data: ', UIManager._data
        print '\nUIManager._types: ', UIManager._types
        print '\nUIManager._currentobjectids: ', UIManager._currentobjectids
        print '\nUIManager._parentuidmap: ', UIManager._parentuidmap
        print '\nUIManager._childrenuidmap: ', UIManager._childrenuidmap
        print '\nUIManager._parenttidmap: ', UIManager._parenttidmap
        print '\nUIManager._MVC_CLASSES: ', UIManager._MVC_CLASSES    
    ####




    @classmethod
    def register_class(cls, controller_class, model_class, view_class,
                                               controller_parent_class=None):  
        #
        if controller_class is None:
            msg = "Controller class cannot be None"
            log.exception(msg)
            raise TypeError(msg)
        #    
        if not issubclass(controller_class, UIControllerBase):
            msg = "Controller class must inherit from UIControllerBase."
            log.exception(msg)
            raise TypeError(msg)           
        #    
        cls._types[controller_class.tid] = controller_class 
        cls._currentobjectids[controller_class.tid] = 0    
        #
        if model_class is not None:
            if not issubclass(model_class, UIModelBase):
                msg = "Model class must inherit from UIModelBase."
                log.exception(msg)
                raise TypeError(msg)     
            model_class_tid = model_class.tid
            if model_class_tid not in cls._types.keys():    
                cls._types[model_class_tid] = model_class
                cls._currentobjectids[model_class_tid] = 0     
        else:
            model_class_tid = None
        if view_class is not None:
            view_class_tid = view_class.tid
            if view_class_tid not in cls._types.keys():
                cls._types[view_class_tid] = view_class
                cls._currentobjectids[view_class_tid] = 0     
        else:
            view_class_tid = None
        #    
        if controller_class.tid not in cls._MVC_CLASSES.keys():    
            cls._MVC_CLASSES[controller_class.tid] = (model_class_tid, view_class_tid)
        else:
            if (model_class_tid, view_class_tid) != cls._MVC_CLASSES.get(controller_class.tid):
                msg = 'Cannot register another model or another view for controller {}'.format(controller_class.tid)
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
                if not issubclass(parent_class, UIControllerBase):
                    msg = "Type {} is not instance of UIControllerBase.".format(controller_parent_class)
                    log.exception(msg)                    
                    raise TypeError(msg)                  
            except Exception:
                raise
            controller_parent_class_tid = controller_parent_class.tid   
        else:
            controller_parent_class_tid  = None   
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
            log.info('UIManager registered class {} for parent class {} successfully.'.format(class_full_name, parent_full_name))
        else:    
            log.info('UIManager registered class {} successfully.'.format(class_full_name))                          
        return True
      
        

    def get(self, uid):
        if isinstance(uid, basestring):
            uid = App.app_utils.parse_string_to_uid(uid)
        return self._data.get(uid)


    # Something like a mix between new and add in ObjectManager
    # Object Factory        
    def create(self, controller_tid, 
                               parent_uid=None, **base_state):
        try:
            class_ = self._check_controller_tid(controller_tid)
        except Exception, e:
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
            obj = class_()
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
            obj._create_model_view(**base_state)
        except Exception as e:
            print e
            msg = 'ERROR found in Model-View creation for class {}.'.format(class_.__name__)      
            log.exception(msg)
            raise         
        try:
            obj._PostInit()
        except Exception:
            msg = 'Error found in {}._PostInit(). Object was not created.'.format(obj.__class__.__name__)
            log.exception(msg)
            
        self.send_message('create', objuid=obj.uid, parentuid=parent_uid)    
        return obj
 
    def get_children(self, parent_uid):
        return self._childrenuidmap.get(parent_uid)
 
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
               
    def remove(self, uid):
        msg = 'Removing object from UI Manager: {}.'.format(uid)
        log.debug(msg)
        #print '\n', msg
        self.send_message('pre_remove', objuid=uid)
        obj = self.get(uid)
        if not isinstance(obj, UIControllerBase):
            return False
        for childuid in self._childrenuidmap.get(uid)[::-1]:
            self.remove(childuid) 
        # Unsubscribing listeners from controller
        obj.unsubAll()    
        # PreDelete must close (delete) all references from object's parent.    
        obj.PreDelete()
        if obj.view:
            obj.view.PreDelete() 
            msg = 'Deleting UI view object {}.'.format(obj.view.uid)
            #print msg
            log.debug(msg)
            del obj.view
        if obj.model:
            #
            obj.model.PreDelete()  
            msg = 'Deleting UI model object {}.'.format(obj.model.uid)
            #print msg
            log.debug(msg)
            del obj.model    
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
        #print msg
        log.debug(msg)
        # Finally, deletes the controller
        del obj
        gc.collect()
        self.send_message('post_remove', objuid=uid)
        msg = 'UI Manager removed sucessfully {}.'.format(uid) 
        #print msg
        log.debug(msg)    
        return True

    # Before exit application
    def PreExit(self):
        for obj in self.list():
            try:
                obj.model.PreDelete() 
            except AttributeError:
                pass
            except:
                raise
            try:
                obj.view.PreDelete() 
            except AttributeError:
                pass
            except Exception as e:
                print '\n\n', obj.uid, e.args, e.message, '\n\n'
                raise                
            obj.PreDelete()    

    # TODO: escolher um melhor nome para este método
    def close(self):
        msg = 'UI Manager has received a close call.'
        log.info(msg)
        #print '\n', msg
        #print
        self.print_info()
        for top_level_uid in self._get_top_level_uids():
            self.remove(top_level_uid)
        msg = 'ENDS.'
        log.info(msg)
        #print '\n', msg
        #print
        self.print_info()    
        log.info('UI Manager has closed.')

    def list(self, tidfilter=None, parentuidfilter=None):
        if parentuidfilter is None:
            objs = self._data.values()
        else:
            parent = self.get(parentuidfilter)
            objs = [self._data.get(uid) for uid in self.get_children(parent.uid)]
        if tidfilter:
            return [obj for obj in objs if obj.tid == tidfilter]
        else:
            return objs            
            
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

    def get_model_view_classes(self, controller_tid):
        try:
            self._check_controller_tid(controller_tid)
        except:
            raise
        model_tid, view_tid = self._MVC_CLASSES.get(controller_tid)
        if model_tid is None:
            model_class = None
        else:    
            model_class = self._gettype(model_tid)
        if view_tid is None:
            view_class = None
        else:      
            view_class = self._gettype(view_tid)
        return model_class, view_class

    def _check_controller_tid(self, controller_tid):
        if controller_tid is None:
            msg = "Controller tid cannot be None."
            raise TypeError(msg)
        if controller_tid not in self._MVC_CLASSES.keys():
            msg = "Type {} is not registered".format(controller_tid)
            raise TypeError(msg)
        class_ = self._gettype(controller_tid)  
        if not issubclass(class_, UIControllerBase):
            msg = "Type {} is not instance of UIControllerBase.".format(controller_tid)
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

    def do_query(self, tid, parent_uid=None, *args, **kwargs):
        objects = self.list(tid, parent_uid)
        if not objects: return None  
        comparators = self._create_comparators(*args)  
        ret_list = []
        for obj in objects:
            ok = True
            for (key, operator, value) in comparators:
                ok = False
                type_ = obj.model._ATTRIBUTES.get(key).get('type')
                value = type_(value)
                if operator == '>=':
                    ok = obj.model[key] >= value
                elif operator == '<=':
                    ok = obj.model[key] <= value                  
                elif operator == '>':
                    ok = obj.model[key] > value
                elif operator == '<':
                    ok = obj.model[key] < value     
                elif operator == '!=':
                    ok = obj.model[key] != value
                elif operator == '=':
                    ok = obj.model[key] == value
                if not ok:
                    break
            if ok:
                ret_list.append(obj)
        if kwargs:
            orderby = kwargs.get('orderby')
            if orderby and len(ret_list) >= 2:
                aux_list = []
                while len(ret_list) > 0:
                    minor_idx = 0
                    for idx, obj in enumerate(ret_list):
                        if obj.model[orderby] < ret_list[minor_idx].model[orderby]:
                            minor_idx = idx
                    aux_list.append(ret_list[minor_idx])
                    del ret_list[minor_idx]
                ret_list = aux_list
            reverse = kwargs.get('reverse')
            if reverse:
                ret_list.reverse()                     
        return ret_list
        
    def _create_comparators(self, *args):
        operators = ['>=', '<=', '>', '<', '!=', '=']
        ret_list = []
        for arg in args:
            operator = None
            for oper in operators:
                if oper in arg:
                    operator = oper
                    break
            if not operator:
                raise ValueError('Operator not found. Valid operators are: {}'\
                                 .format(operators)
                )
            ret_list.append((arg.split(operator)[0], operator, 
                             arg.split(operator)[1])
            )
        return ret_list       


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
            if not obj.model: 
                obj_state = OrderedDict()
            else:
                obj_state = obj.model.get_application_state()
                if obj_state.has_key('children'):
                    msg = obj.__class__.__name__ + ' cannot have an attribute called ''children''.'
                    raise AttributeError(msg)
            obj_state['children'] = []
            for obj_child_uid in self.get_children(obj.uid):
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
                obj_state = obj.model.get_user_state()
            #    if obj_state.has_key('children'):
            #        msg = obj.__class__.__name__ + ' cannot have an attribute called ''children''.'
            #        raise AttributeError(msg)
            obj_state['children'] = []
            for obj_child_uid in self.get_children(obj.uid):
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
        print '\n_load_user_state'
        
        for obj_tid, objects_state in state.items():
            print
            print obj_tid
            print len(objects_state), objects_state
            objects = self.list(obj_tid)
            for i in range(len(objects_state)):
                obj = objects[i]
                obj_state = objects_state[i]
                for key, value in obj_state.items():
                    print '\n', key, value, type(value)
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


                