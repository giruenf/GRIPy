# -*- coding: utf-8 -*-
import sys
import gc
import pprint
import Queue
import wx
import weakref
import types
from collections import OrderedDict
from FileIO.utils import AsciiFile
import App.utils
from App import log


class UIBase(object):

    tid = None
    
    def __init__(self):
        self.check_creator()
        self.oid = None
      
    #def __del__(self):
    #    print 'deleting ', self.uid

    def PostInit(self):
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
        # Only UIManager can create objects. Let's check it!
        caller_info = App.utils.get_caller_info()
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

                             
        
class UIControllerBase(UIBase):
    tid = None
    # TODO: verificar se vale a pena manter esses singletons
    _singleton = False
    _singleton_per_parent = False
    
    
    def __init__(self):
        super(UIControllerBase, self).__init__()  
        _UIM = UIManager()
        self.oid = _UIM._getnewobjectid(self.tid)
          

    def _create_model_view(self, **base_state): 
        _UIM = UIManager()           
        model_class, view_class = _UIM.get_model_view_classes(self.tid)
        if model_class is not None:
            try:
                self.model = model_class(self.uid, **base_state)
            except Exception:
                msg = 'ERROR on creating MVC model {} object'.format(model_class.__name__)
                log.exception(msg)
                raise 
        else:
            self.model = None
        if view_class is not None:     
            try:
                self.view = view_class(self.uid)
            except Exception, e:
                msg = 'Error on creating MVC view {} object'.format(view_class.__name__)
                log.exception(msg)
                raise e             
        else:
            self.view = None  


    def PreRemove(self):
        pass

            
    def _PostInit(self):
        try:
            if self.model:
                self.model.PostInit()
            if self.view:        
                self.view.PostInit()
            self.PostInit()    
        except Exception:
            msg = 'ERROR in {}._PostInit'.format(self.__class__.__name__)
            log.exception(msg)
            raise
        

    def get_root_controller(self):
        """
        TODO: Traduzir e melhorar isso
    
        Em vez de retornar self._UIM.list('main_window_controller')[0], 
        retorna o controller raiz da qual self se encontra. E provavel que 
        quase sempre (ou sempre) seja retornado self._UIM.list('main_window_controller')[0],
        porem a ideia eh nao restringir isso facilitando futuras implementacoes.
                
        """    
        _UIM = UIManager()
        parent_uid = self.uid
        while parent_uid:
            obj_uid = parent_uid
            parent_uid = _UIM._getparentuid(obj_uid)  
        return _UIM.get(obj_uid)    
        

    def _getstate(self):
        if self.model:
            return self.model._getstate()
        return None    
             
             
    def _loadstate(self, **state):
        if self.model:
            return self.model._loadstate(**state)
            
            
###############################################################################
###############################################################################
        
        

class UIModelBase(UIBase):
    """
    The base class for all Model classes (MVC software architectural pattern).
        
    """
    
    tid = None
    # Special keys bypasses the checking made in __setattr__ or __setitem__
    _SPECIALS_KEYS = ['oid', '_controller_uid', '_UIModelBase__initialised']


    def __init__(self, controller_uid, **base_state):
        super(UIModelBase, self).__init__()
        self.__initialised = False        
        self._controller_uid = controller_uid
        _UIM = UIManager()
        self.oid = _UIM._getnewobjectid(self.tid)   
        # We are considering that only Controller class objects 
        # can create Model class objects. Then, we must verify it
        model_class = _UIM.get_model_view_classes(controller_uid[0])[0]
        if self.__class__ != model_class:
            msg = 'Error! Only the controller can create the model.'
            raise Exception(msg)    
        for key, value in self._ATTRIBUTES.items():
            if base_state.has_key(key):
                self[key] = base_state.get(key)
            else:    
                self[key] = value.get('default_value')   
        self.__initialised = True


    def PostInit(self):
        pass


    def __getattr__(self, key):
        raise AttributeError(key)


    def __setattr__(self, key, value):
        if key in self._SPECIALS_KEYS:
            self.__dict__[key] = value
            return
        self._do_set(key, value)


    def __getitem__(self, key):
        try:
            return self.__dict__.get(key)
        except KeyError:
            raise AttributeError(key)


    def __setitem__(self, key, value):
        self._do_set(key, value)


    def _do_set(self, key, value):
        if (not self.__dict__['_UIModelBase__initialised'] and not self._ATTRIBUTES.has_key(key)) or \
                        (self.__dict__['_UIModelBase__initialised'] and not self.__dict__.has_key(key)):
            msg = '{} does not have attribute {}.'.format(\
                self.__class__.__name__, str(key))
            log.warning(msg)
            return
        base_attr = self._ATTRIBUTES.get(key).get('base_attr')    
        if self.__initialised and base_attr:
            msg = 'Base attributes are only loaded before initialization. {}.{} = {}'.format(\
                self.__class__.__name__, str(key), str(value))
            log.warning(msg)
            return
        type_ = self._ATTRIBUTES.get(key).get('type')
        # Special treatment for functions
        if type_ == types.FunctionType:
            if isinstance(value, basestring):
                value = App.utils.get_function_from_string(value)
            if value is not None and not callable(value):
                msg = 'ERROR: Attributes signed as \"types.FunctionType\" can recieve only \"str\" or \"types.FunctionType\" values. '
                msg += 'Received: {} - Type: {}'.format(value, type(value))
                log.error(msg)
                raise AttributeError(msg)
        elif not isinstance(value, type_):
            try:
                value = type_(value)
            except Exception:
                ok = False
                if isinstance(value, basestring):
                    if value.startswith('wx.Point'):
                        value = value.lstrip('wx.Point(')
                        value = value.rstrip(')')
                        x = value.split(',')[0].strip()
                        y = value.split(',')[1].strip()
                        value = wx.Point(int(x), int(y))
                        ok = True
                    elif value.startswith('wx.Size'):
                        value = value.lstrip('wx.Size(')
                        value = value.rstrip(')')
                        x = value.split(',')[0].strip()
                        y = value.split(',')[1].strip()
                        value = wx.Size(int(x), int(y))
                        ok = True    
                if not ok:        
                    msg = 'ERROR in parsing value {} to type {}'.format(str(value), str(type_))
                    log.exception(msg)
                    raise
        if not self.__initialised:
            self.__dict__[key] = value
        else:    
            if self.__dict__[key] == value:
                return      
            old_value = self[key]    
            self.__dict__[key] = value
            on_change = self._ATTRIBUTES.get(key).get('on_change')
            if on_change:
                _UIM = UIManager()
                controller = _UIM.get(self._controller_uid)
                on_change(controller, key=key, old_value=old_value, new_value=value)
        k = key.encode('utf-8')            
        v = self[key]
        if isinstance(v, basestring):        
            v = self[key]
            v = v.encode('utf-8')
        else:
            v = str(v)
        msg = '    {} has setted attribute {} = {}'.format(self.uid, k, v)       
        log.debug(msg)



    def _getstate(self):
        state = OrderedDict()
        for key in self.__dict__.keys(): 
            if key not in self._SPECIALS_KEYS:
                state[key] = self[key]
        return state
             
             
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
     


###############################################################################
###############################################################################


class UIViewBase(UIBase):
    tid = None

    def __init__(self, controller_uid):
        UIBase.__init__(self)
        self._controller_uid = controller_uid
        _UIM = UIManager()  
        self.oid = _UIM._getnewobjectid(self.tid)
        # We are considering that only Controller class objects 
        # can create View class objects. Then, we must verify it       
        view_class = _UIM.get_model_view_classes(controller_uid[0])[1]
        if self.__class__ != view_class:
            msg = 'Error! Only the controller can create the view.'
            log.exception(msg)
            raise Exception(msg)       

    def PostInit(self):
        pass
        
        
###############################################################################
###############################################################################



class UIManager(object):#GenericObject):
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
    
    #_NPZIDENTIFIER = "__NPZ;;"
    #LOGPLOT_TITLEBG_COLOUR = '#B0C4DE' #LightSteelBlue
    


    def __init__(self):
        caller_info = App.utils.get_caller_info()
        #print 
        #print caller_info
        #print 
        owner = caller_info[0][1]
        # Armengue feito para as funcoes dos menus.. tentar corrigir isso
        if not owner:
            owner = wx.GetApp()
        try:
            owner_name = owner.uid
        except AttributeError:
            owner_name = owner.__class__.__name__
        msg = 'A new instance of UIManager was solicited by {}'.format(owner_name)
        log.debug(msg)        
        self._ownerref = weakref.ref(owner)
        self._data = UIManager._data
        self._types = UIManager._types
        self._currentobjectids = UIManager._currentobjectids
        self._parentuidmap = UIManager._parentuidmap
        self._childrenuidmap = UIManager._childrenuidmap
        self._parenttidmap = UIManager._parenttidmap
        self._MVC_CLASSES = UIManager._MVC_CLASSES
        

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


    # Analogue to OM.Manager.registertype
    @classmethod
    def register_class(cls, controller_class, model_class, view_class,
                           controller_parent_class=None):  
        if controller_class is None:
            msg = "Controller class cannot be None"
            log.exception(msg)
            raise TypeError(msg)
        cls._types[controller_class.tid] = controller_class 
        cls._currentobjectids[controller_class.tid] = 0    
        
        if model_class is not None:
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
            
        if controller_class.tid not in cls._MVC_CLASSES.keys():    
            cls._MVC_CLASSES[controller_class.tid] = (model_class_tid, view_class_tid)
        else:
            if (model_class_tid, view_class_tid) != cls._MVC_CLASSES.get(controller_class.tid):
                msg = 'Cannot register another model or another view for controller {}'.format(controller_class.tid)
                log.exception(msg)
                raise Exception(msg)
        if controller_parent_class:
            try:
                if controller_parent_class.tid is None:
                    msg = "Controller tid cannot be None."
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
                 
        if controller_class.tid not in cls._parenttidmap.keys():   
            cls._parenttidmap[controller_class.tid] = [controller_parent_class_tid]
        else:
            cls._parenttidmap.get(controller_class.tid).append(controller_parent_class_tid)

        class_full_name = str(controller_class.__module__) + '.' + str(controller_class.__name__)
        if controller_parent_class:
            parent_full_name = str(controller_parent_class.__module__) + '.' + str(controller_parent_class.__name__)
            log.info('UIManager registered class {} for parent class {} successfully.'.format(class_full_name, parent_full_name))
        else:    
            log.info('UIManager registered class {} successfully.'.format(class_full_name))                          
        return True
     
  

    def get(self, uid):
        return self._data.get(uid)
 
          
            
            
    # Something like a mix between new and add in ObjectManager
    # Object Factory        
    def create(self, controller_tid, parent_uid=None, **base_state):
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
            msg = "Parent object given is not a instance of {} parent class.".format(controller_tid)
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
        except Exception:
            msg = 'ERROR found in Model-View creation for class {}.'.format(class_.__name__)      
            log.exception(msg)
            raise         
        try:
            obj._PostInit()
        except Exception:
            msg = 'Error found in {}._PostInit(). Object was not created.'.format(obj.__class__.__name__)
            log.exception(msg)
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
        obj = self.get(uid)
        if not isinstance(obj, UIControllerBase):
            return False
        for childuid in self._childrenuidmap.get(uid)[::-1]:
            self.remove(childuid) 
        # PreRemove must close (delete) all references from object's parent.    
        obj.PreRemove()    
        if obj.model:
            msg = 'Deleting UI model object {}.'.format(obj.model.uid)
            log.debug(msg)
            del obj.model
        if obj.view:
            """
            view = obj.view
            obj.__dict__['view'] = None
            obj.view = None
            msg = 'Deleting UI view object {}.'.format(view.uid)
            log.debug(msg)
            del view
            """
            msg = 'Deleting UI view object {}.'.format(obj.view.uid)
            log.debug(msg)
            del obj.view
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
        log.debug(msg)
        # Finally, deletes the controller
        del obj
        gc.collect()
        msg = 'UI Manager removed sucessfully {}.'.format(uid) 
        log.debug(msg)    
        return True



    # TODO: escolher um melhor nome para este método
    def close(self):
        msg = 'UI Manager has received a close call.'
        log.info(msg)
        print '\n', msg
        print
        self.print_info()
        for top_level_uid in self._get_top_level_uids():
            self.remove(top_level_uid)
        msg = 'ENDS.'
        log.info(msg)
        print '\n', msg
        print
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



    def _getstate(self, start_from_obj_uid=None):
        if start_from_obj_uid is None:
            objects = self.list('main_window_controller')
        else:
            objects = [self.get(start_from_obj_uid)]          
        for obj in objects:
            if not obj.model: 
                obj_state = OrderedDict()
            else:
                obj_state = self._adjust_state_for_saving(obj.model._getstate())
                if obj_state.has_key('children'):
                    msg = obj.__class__.__name__ + ' cannot have an attribute called ''children''.'
                    raise AttributeError(msg)
            obj_state['children'] = []
            for obj_child_uid in self.get_children(obj.uid):
                obj_state.get('children').append(self._getstate(obj_child_uid))
        return {obj.tid: obj_state}
        
 

    def _adjust_state_for_saving(self, state):
        for key, value in state.items():
            if isinstance(value, wx.Point):       
                state[key] = 'wx.Point' + str(value)    
            elif isinstance(value, wx.Size):
                state[key] = 'wx.Size' + str(value)
            elif callable(value):
                state[key] = App.utils.get_string_from_function(value)
        return state
         
        
    def _loadstate(self, state, parent_uid=None):  
        for obj_tid, obj_state in state.items():
            try:
                if obj_state:
                    children = obj_state.pop('children')
                    new_created_obj = self.create(obj_tid, parent_uid=parent_uid, **obj_state)
                    #if not new_created_obj:
                    #    raise Exception()
                    for child in children:
                        self._loadstate(child, new_created_obj.uid)
                else:
                    self.create(obj_tid, parent_uid=parent_uid) 
            except Exception:
                msg = 'ERROR in loading UI state.'
                log.exception(msg)
                raise
              
  

    def _load_state_from_file(self, fullfilename):
        msg = 'Loading Gripy interface state from: {}'.format(fullfilename)
        print msg
        log.debug(msg)
        _state = AsciiFile.read_json_file(fullfilename)
        self._loadstate(_state)        
        msg = 'Gripy interface state loaded.'.format(fullfilename)
        print msg
        log.debug(msg)
        

    def _save_state_to_file(self, fullfilename):
        try:
            _state = self._getstate()
        except Exception:
            _state = None
            msg = 'ERROR: UI State cannot be gotten from UI Manager.' 
            log.exception(msg)
        if _state is not None: 
            try:
                AsciiFile.write_json_file(_state, fullfilename)
                msg = 'Gripy interface state was saved to file ' + fullfilename 
                print msg
                log.info(msg)
            except Exception:
                raise
        
        
        
        
        
        