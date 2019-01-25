# -*- coding: utf-8 -*-
"""
Manager
=======

This file defines `ObjectManager`.
"""

from collections import OrderedDict
import numpy as np
import zipfile
import os

import tempfile

from app import app_utils


from app import log
from classes.base.generic_manager import GripyManager

import copy


try:
    import cPickle as pickle
except ImportError:
    import pickle




class ObjectManager(GripyManager):
    """
    The Object Manager.
    
    The ObjectManager is responsible for managing objects throughout the
    program execution. For instance, it is responsible for creating new objects
    and deleting them when they are no longer needed.
    
    The ObjectManager is a "Borg", i.e. all the instances of the class share
    (almost) the same state. This way, when access to a managed object is
    needed an "instance" of ObjectManager must be created in order to access
    the data.
    
    Parameters
    ----------
    owner
        The object that is instantiating a new ObjectManager.
    """
    
    # Types 
    _types = OrderedDict()
    _currentobjectids = {}
    _parenttidmap = {}
    # Data
    _data = OrderedDict()
    _parentuidmap = {}
    _childrenuidmap = {}
    
    # Other
    _NPZIDENTIFIER = "__NPZ;;"
    _changed = False
    _on_load = False
  
    
    def __init__(self):
        #super().__init__()
        self._types = ObjectManager._types
        self._currentobjectids = ObjectManager._currentobjectids
        self._parenttidmap = ObjectManager._parenttidmap   
        
#        print ('\nObjectManager is initing...')
#        print ('ObjectManager._data:', ObjectManager._data)
        self._data = ObjectManager._data
        self._parentuidmap = ObjectManager._parentuidmap
        self._childrenuidmap = ObjectManager._childrenuidmap
#        log.debug('ObjectManager new instance was solicitated by {}'.format(str(self._owner)))

        self._LOADING_STATE = ObjectManager._LOADING_STATE         
 
    
    #### Remover isso assim que possivel
    def print_info(self):
        print ('\nObjectManager.print_info:')
        #print (hex(id(ObjectManager)))
        print ('ObjectManager._data: ', str(ObjectManager._data))
        #print ('ObjectManager._types: ', ObjectManager._types)
        #print ('ObjectManager._currentobjectids: ', ObjectManager._currentobjectids)
        print ('ObjectManager._parentuidmap: ', ObjectManager._parentuidmap)
        print ('ObjectManager._childrenuidmap: ', ObjectManager._childrenuidmap)
        #print ('ObjectManager._parenttidmap: ', ObjectManager._parenttidmap)
        #print ('ObjectManager._MVC_CLASSES: ', ObjectManager._MVC_CLASSES)    
    ####


       
    def _reset(self):
        # TODO: Resolver DataFilter tid 'data_filter'
    
        temp_parentuidmap = copy.deepcopy(self._parentuidmap)
        
        for uid, parentuid in temp_parentuidmap.items():
            if parentuid is None and uid[0] != 'data_filter':
                try:
                    # TODO: rever isso, pois alguns uid estao dando problema
                    #       A ideia eh nao ter esse try
                    self.remove(uid)
                except Exception as e:
                    print ('OM._reset ERROR:', str(e))
                    pass
        #            
        for tid in self._currentobjectids.keys():
            self._currentobjectids[tid] = 0
            
            
        self._data = OrderedDict()
        self._parentuidmap = {}
        self._childrenuidmap = {} 
        ObjectManager._changed = False         
    

    
    def get_changed_flag(self):
        """
        Return a flag used by Application know if ObjectManager was changed
        since last saved state. 
        
        Returns
        -------
        bool
            Whether the ObjectManager was changed.
        """
        return ObjectManager._changed 
        
    def set_changed_flag(self):
        """
        Set True a flag used by Application as know if ObjectManager was 
        changed since last saved state. 
        """
        ObjectManager._changed = True   

    def _getnewobjectid(self, typeid):
        """
        Return a new object identifier for the desired type.
        
        Parameters
        ----------
        typeid : str
            The identifier for the type that a new object identifier is
            needed.
        
        Returns
        -------
        objectid : int
            A new unique object identifier for given type.
        """
        objectid = self._currentobjectids[typeid]
        self._currentobjectids[typeid] += 1
        return objectid


    def new(self, typeid, *args, **kwargs):
        """
        Create a new instance of the desired type.
        
        In this method `*args` and `**kwargs` will be passed on as arguments to
        the constructor of the new object.
        
        Parameters
        ----------
        typeid : str
            The type identificator of the new object.
        
        Returns
        -------
        obj : GenericObject
            The new object.
        
        Notes
        -----
        The new object is not automatically added to ObjectManager. The ``add``
        method must be called so that the new object can be managed.
        
        Examples
        --------
        >>> om = ObjectManager()
        >>> newobj = om.new('typeid', name='nameofthenewobject')
        >>> # name will be passed to the constructor
        """
        try:
            class_ = self._types[typeid]
    #        print ('\n\n{}'.format(class_))
    #        print (typeid, args, kwargs)
            obj = class_(*args, **kwargs)
    #        objectid = self._getnewobjectid(typeid)
    #        obj.oid = objectid
            return obj
        except Exception as e:
            msg = 'Error on creating object! [tid={}, args={}, kwargs={}, error={}]'.format(typeid, args, kwargs, e)
            raise Exception(msg)


    def add(self, obj, parentuid=None):
        """
        Add a new instance that from now on will be managed by ObjectManager.
        
        Parameters
        ----------
        obj : GenericObject
            The object to be managed by ObjectManager.
        parentuid : uid, optional
            The unique identificator of the added object's parent. If the
            object has no parent this argument must be ommited.
        
        Returns
        -------
        bool
            Whether the operation was successful.
        
        Examples
        --------
        >>> om = ObjectManager()
        >>> parentobj = om.new('parenttypeid')
        >>> om.add(parentobj)
        True
        >>> childobj = om.new('childtypeid')
        >>> om.add(childobj)
        False
        >>> om.add(childobj, parentobj.uid)
        True
        """
        
        try:
            if not self._isvalidparent(obj.uid, parentuid):
                return False
            self._parentuidmap[obj.uid] = parentuid
            self._childrenuidmap[obj.uid] = []
            self._data[obj.uid] = obj

            if parentuid:
                self._childrenuidmap[parentuid].append(obj.uid)  
        
        except Exception as e:
            print ('ERROR in adding object [ObjectManager.add]:', obj.uid, e, type(e))
            raise
            
        # Sending message  
        try:
            self.send_message('add', objuid=obj.uid)
        except Exception as e:
            print ('ERROR in dealing with object creation [ObjectManager.add]:', obj.uid, e)
            return False

        # TODO: Rever isso: UI.mvc_classes.track_object@DataFilter 
        try:
            nsc = obj._NO_SAVE_CLASS
        except:
            nsc = False
        
        if not ObjectManager._on_load and not nsc:
            ObjectManager._changed  = True       
        return True



    def get(self, uid):  # TODO: colocar "Raises" na docstring
        """
        Return the object which `uid` was provided.
        
        This method is the main access point for the objects that are being
        managed by ObjectManager.
        
        Parameters
        ----------
        uid : uid
            The unique identificator of the desired object.
        
        Returns
        -------
        GenericObject
            The desired object.
        
        Examples
        --------
        >>> om = ObjectManager()
        >>> obj = om.new('typeid')
        >>> om.add(obj)
        True
        >>> obj2 = om.get(obj.uid)
        >>> obj2 == obj
        True
        """
#        print ('\n\nOM.get:', uid, type(uid))
        if isinstance(uid, str):
            uid = app_utils.parse_string_to_uid(uid)
        try:    
#            print ('OM.get [2]:', uid, type(uid))
#            print (self._data)
            obj = self._data[uid]
            return obj
        except Exception as e:
#            print ('ERROR OM.get:', uid, e)
            raise
        


    def remove(self, uid):
        """
        Remove the object which `uid` was provided.
        
        Parameters
        ----------
        uid : uid
            The unique identificator of the object to remove.
        
        Returns
        -------
        bool
            Whether the remove operation was successful.
        
        Examples
        --------
        >>> om = ObjectManager()
        >>> obj = om.new('typeid')
        >>> om.add(obj)
        True
        >>> om.remove(obj.uid)
        True
        >>> om.get(obj.uid)
        KeyError: obj.uid
        """
        
        print ('\nOM Removing', uid)
        
        obj = self._data.pop(uid)
        #
        # TODO: Ver se deve permanecer da forma abaixo
        # foi deixado assim por causa do UIControllerObject.attach
        #obj.send_message('pre_remove')
        
        self.send_message('pre_remove', objuid=uid)
        print ('\nReturning to OM.revove...')
        #
        for childuid in self._childrenuidmap[uid][::-1]:
            self.remove(childuid) 
        parentuid = self._parentuidmap[uid]
        del self._parentuidmap[uid]
        if parentuid:      
            self._childrenuidmap[parentuid].remove(uid)    
        
        del self._childrenuidmap[uid]
        del obj
        self.send_message('post_remove', objuid=uid)
        ObjectManager._changed  = True   
        #
        return True





    @classmethod
    def register_class(cls, obj_type_class, parent_type_class=None):
        # TODO: Editar isso
        """
        Register a type which instances are now able to be managed.
        
        Parameters
        ----------
        type_ : type
            The new type that will be registered within `ObjectManager`.
        parenttype : type, optional
            The parent type of `type_`
        
        Returns
        -------
        bool
            Whether the remove operation was successful.
        
        Examples
        --------
        >>> om = ObjectManager()
        >>> obj = om.new('unregisteredtypeid', name='nameofobj')
        KeyError: 'unregisteredtypeid'
        >>> ObjectManager.registertype(UnregeristeredType)
        True
        >>> obj = om.new('unregisteredtypeid', name='nameofobj')
        >>> om.add(obj)
        True
        """
        tid = None
        parent_tid = None
        # obj_type_class validation 
        try:    
            tid = obj_type_class.tid
        except AttributeError:
            msg = "Type indentifier (tid) not found for class: {}.".format(obj_type_class)
            log.exception(msg)
            return False
        if not tid:
            msg = "Wrong tid for class: {}.".format(obj_type_class)
            log.error(msg)  
            return False
        if parent_type_class:
            try:    
                parent_tid = parent_type_class.tid
            except AttributeError:
                msg = "Type indentifier (tid) not found for parent type class: {}.".format(obj_type_class)
                log.exception(msg)
                return False
            if not parent_tid:
                msg = "Wrong tid for parent type class: {}.".format(parent_type_class)
                log.error(msg)  
                return False
        # parent_type_class validation 
        if parent_tid:
            if parent_tid not in cls._types.keys():
                msg = "Parent type Class {} must be registered before accept children types.".format(\
                             obj_type_class.__name__, parent_type_class.__name__
                )
                log.error(msg)   
                return False
            if cls._parenttidmap.get(tid) and parent_tid in cls._parenttidmap.get(tid):
                msg = "Class {} was registered previously for parent type class {}.".format(\
                             obj_type_class.__name__, parent_type_class.__name__)
                log.error(msg) 
                return False
        # Actual registering...
        if tid not in cls._types.keys():
            cls._types[tid] = obj_type_class
            cls._currentobjectids[tid] = 0
            cls._parenttidmap[tid] = [parent_tid]
        else:                
            cls._parenttidmap.get(tid).append(parent_tid)
        # Logging for successful operation       
        class_full_name = str(obj_type_class.__module__) + '.' + str(obj_type_class.__name__)
        if parent_type_class:
            parent_full_name = str(parent_type_class.__module__) + '.' + str(parent_type_class.__name__)
            log.info('ObjectManager registered class {} for parent class {} successfully.'.format(class_full_name, parent_full_name))
        else:    
            log.info('ObjectManager registered class {} successfully.'.format(class_full_name))
        return True        


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
        return parenttid in self._parenttidmap[objtid]


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
        return self._parentuidmap[uid]



            
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
        return self._types[tid]
    
    
    
    def save(self, archivepath):
        """
        Save the current `ObjectManager` state to a file.
        
        Parameters
        ----------
        archivepath : str
            The path (i.e. the filename) of the file in which the state will
            be saved.
        
        Returns
        -------
        bool
            Whether the operation was successful.
        
        Notes
        -----
            Callbacks are not saved.
        """
        
        dirname, filename = os.path.split(archivepath)
        basefilename = filename.rsplit('.', 1)[0]
        picklefilename =  basefilename + ".pkl"
        npzfilename = basefilename + ".npz"
        
        pickledata = OrderedDict()
        npzdata = OrderedDict()
        
        for uid, obj in self._data.items():
            objdict = {} #OrderedDict()
            
            for key, value in obj._getstate().items():
                if isinstance(value, np.ndarray):
                    npzname = "{}_{}_{}".format(uid[0], uid[1], key)
                    npzdata[npzname] = value
                    objdict[key] = self._NPZIDENTIFIER + npzname
                else:
                    objdict[key] = value
            
#            for key in obj._READ_ONLY:
#                objdict[key] = obj[key]

                        
            objdict ['__children'] = self._childrenuidmap[uid]
            pickledata[uid] = objdict  
        
        print ('\nsave')
        print ()
        print ('pickledata:', pickledata)
        print ()
#        print ('parentuidmap:', self._parentuidmap)
#        print () 
        print ('npzdata:', npzdata)
        print ()
        

        picklefile = open(os.path.join(tempfile.gettempdir(), picklefilename), 'wb')
#        pickle.dump(dict(data=pickledata, parentmap=self._parentuidmap), picklefile, protocol=2)
        pickle.dump(pickledata, picklefile, protocol=2)
        picklefile.close()

        npzfile = open(os.path.join(tempfile.gettempdir(), npzfilename), 'wb')
        with zipfile.ZipFile(npzfile, mode='w', 
                                 compression=zipfile.ZIP_DEFLATED) as npz_zip:        
            for key, val in npzdata.items():
                print (key + '.npy')
                with npz_zip.open(key + '.npy', 'w') as buf:
                    np.lib.npyio.format.write_array(buf, np.asanyarray(val), 
                                                    allow_pickle=False)
        
        npzfile.close()
        
        with zipfile.ZipFile(archivepath, mode='w', 
                                 compression=zipfile.ZIP_DEFLATED) as pgg_zip:
            pgg_zip.write(os.path.join(tempfile.gettempdir(), picklefilename), arcname=picklefilename)
            pgg_zip.write(os.path.join(tempfile.gettempdir(), npzfilename), arcname=npzfilename) 
                                              
        os.remove(os.path.join(tempfile.gettempdir(), picklefilename))
        os.remove(os.path.join(tempfile.gettempdir(), npzfilename))    
        


    def load(self, archivepath):
        """
        Load the state of `ObjectManager` from a previously saved file.
        
        Parameters
        ----------
        archivepath : str
            The path (i.e. the filename) of the file to load the state from.
        
        Returns
        -------
        bool
            Whether the operation was successful.
        """
        
        self._LOADING_STATE = True
        
        dirname, filename = os.path.split(archivepath)
        picklefilename = filename.rsplit('.', 1)[0] + ".pkl"
        npzfilename = filename.rsplit('.', 1)[0] + ".npz"

        # Unzip and get 2 inner files
        archivefile = zipfile.ZipFile(archivepath, mode='r')
        archivefile.extract(picklefilename, path=tempfile.gettempdir())
        archivefile.extract(npzfilename, path=tempfile.gettempdir())
        archivefile.close()
        
        # Load pickle dict
        picklefile = open(os.path.join(tempfile.gettempdir(), picklefilename), 'rb')
#        pickledict = pickle.load(picklefile)
        pickledata = pickle.load(picklefile)
        picklefile.close()
        
        # Load NumPy's NpzFile object
        npzfile = open(os.path.join(tempfile.gettempdir(), npzfilename), 'rb')
        npzdata = np.lib.npyio.NpzFile(npzfile, allow_pickle=False)
        npzfile.close()
        
#        pickledata = pickledict['data']
#        parentuidmap = pickledict['parentmap']

        print ('\n\n\nload')
        print ()
        print ('pickledata:', pickledata)
        print ()
#        print ('parentuidmap:', parentuidmap)
#        print () 
        print ('npzdata:', npzdata)
        print ()


        self._load_object(pickledata)
        
        """
#        newuidsmap = {}
        for uid, objdict in pickledata.items():
            
            print ('\n{}: {}'.format(uid, objdict))
            
            tid = uid[0]
            for key, value in objdict.items():
                if isinstance(value, str) and value.startswith(self._NPZIDENTIFIER):
                    objdict[key] = npzdata[value.lstrip(self._NPZIDENTIFIER)]
                    
            print ()
            print (tid, objdict)
            
            try:
                obj = self.new(tid, oid=uid[1], **objdict)
#                newuidsmap[olduid] = obj.uid
#                self.add(obj, newuidsmap.get(parentuidmap[olduid]))
            except Exception as e:
                print (e)
                raise 
        """    
        
#        os.remove(os.path.join(tempfile.gettempdir(), picklefilename))
#        os.remove(os.path.join(tempfile.gettempdir(), npzfilename))  
        
        self._LOADING_STATE = False
        
        return True        
        
    
    # for recursion
    def _load_object(self, pickledata, **kwargs):
        if not pickledata:
            return
        
        parent_uid = kwargs.get('parent_uid', None)
        starts_with_uid = kwargs.get('starts_with_uid', None)
        
        if starts_with_uid is None:
            starts_with_uid = next(iter(pickledata))
            parent_uid = None
        
        
        objattr = pickledata.pop(starts_with_uid)
        objchildrenuid = objattr.pop('__children')
        
        print ()
        print ('_load_object:')
        print (starts_with_uid, parent_uid)
        print (objattr, objchildrenuid)
        
        try:
            obj = self.new(starts_with_uid[0], oid=starts_with_uid[1], **objattr)
            self.add(obj, parent_uid)
        except Exception as e:
            print (e)
            raise         
        
        for objchilduid in objchildrenuid:
            self._load_object(pickledata, starts_with_uid=objchilduid, parent_uid=obj.uid)
        
        
        
        """
                for uid, objdict in pickledata.items():
            
            print ('\n{}: {}'.format(uid, objdict))
            
            tid = uid[0]
            for key, value in objdict.items():
                if isinstance(value, str) and value.startswith(self._NPZIDENTIFIER):
                    objdict[key] = npzdata[value.lstrip(self._NPZIDENTIFIER)]
                    
            print ()
            print (tid, objdict)
            
            try:
                obj = self.new(tid, oid=uid[1], **objdict)
#                newuidsmap[olduid] = obj.uid
#                self.add(obj, newuidsmap.get(parentuidmap[olduid]))
            except Exception as e:
                print (e)
                raise 
        """        
    
    
        """
        try:
            
            print ('\n\nObjectManager.load')
            
            try:
                ObjectManager._on_load = True
                dirname, filename = os.path.split(archivepath)
                picklefilename = filename.rsplit('.', 1)[0] + ".pkl"
                npzfilename = filename.rsplit('.', 1)[0] + ".npz"
                
                try:
                    archivefile = zipfile.ZipFile(archivepath, mode='r')
                    print ('A')
                    archivefile.extract(picklefilename, path=dirname)
                    print ('B')
                    archivefile.extract(npzfilename, path=dirname)
                    print ('C')
                except Exception as e:    
                    print ('Error 000:', e)  
                    raise
                finally:
                    archivefile.close()
                print ('D')
                picklefile = open(os.path.join(dirname, picklefilename), 'rb')
                pickledict = pickle.load(picklefile)
                picklefile.close()
                
                print ('E')
                npzfile = open(os.path.join(dirname, npzfilename), 'rb')
                print ('G')
                npzdata = np.load(npzfile)
                print ('h')
                pickledata = pickledict['data']
                parentuidmap = pickledict['parentmap']
                
                newuidsmap = {}
                
                print ('parte 001 OK')   
                
            except Exception as e:
                print ('Error 001:', e)   
                raise
            
            print ()
            
            for olduid, objdict in pickledata.items():
                try:
                    tid = olduid[0]
                    # Obtendo o state dict do objeto
                    for key, value in objdict.items():
                        if isinstance(value, str) and value.startswith(self._NPZIDENTIFIER):
                            objdict[key] = npzdata[value.lstrip(self._NPZIDENTIFIER)]    
                    # TODO: melhorar isso abaixo
                    # A ideia e que a segunda opcao (except) venha a substituir a primeira
                    print ('\ntentando criar:', tid, objdict)
                    obj = self.new(tid, **objdict)
                    print ('Ok')
                except Exception as e:
                    print ('Error', e)
                    try:
                        print ('tentando de novo',)
                        obj = self.create_object_from_state(tid, **objdict)
                        print ('Ok')
                    except:
                        print ('Error')
                        print ('ERROR [ObjectManager.load]: Could not create object for tid={} with given state: {}'.format(tid, objdict))
                        continue
                #try:
                    #print 'A:', olduid, obj.uid
                newuidsmap[olduid] = obj.uid
                #print 'B:', parentuidmap[olduid]
                parent_uid = newuidsmap.get(parentuidmap[olduid])
                #print 'Trying to add object:', obj, 'to parent:', parent_uid
                self.add(obj, parent_uid)
                    #    print 'Added', obj.uid, 'for', parent_uid
                    #else:
                    #    print 'Nao foi added'
                #except Exception as e:
                #    print 'S-ERROR:', e
                #    pass
            npzfile.close()
            
            os.remove(os.path.join(dirname, picklefilename))
            os.remove(os.path.join(dirname, npzfilename))
            ObjectManager._on_load = False
            return True
        except Exception as e:
            print ('ERROR [ObjectManager.load]:', e)
            try:
                archivefile.close()
                picklefile.close()
                npzfile.close()
            
                os.remove(os.path.join(dirname, picklefilename))
                os.remove(os.path.join(dirname, npzfilename))
                ObjectManager._on_load = False 
                ObjectManager._set_empty()
                
            except:
                pass
            return False
        
        """
        
        
    def create_object_from_state(self, tid, **objdict):
        class_ = self._types.get(tid)
        if not class_:
            raise Exception('Error.')
        return class_._loadstate(**objdict)
            
    @classmethod
    def get_tid_friendly_name(cls, tid):
        class_ = cls._types.get(tid)
        if class_:
            try:
                return class_._TID_FRIENDLY_NAME
            except:
                pass
        return None

    @classmethod
    def get_tid(cls, tid_friendly_name):  
        for tid, class_ in cls._types.items():
            try:
                if class_._TID_FRIENDLY_NAME == tid_friendly_name:
                    return tid
            except AttributeError: # if class_ has no attribute '_TID_FRIENDLY_NAME' 
                continue
        return None
        
        
        
        