# -*- coding: utf-8 -*-

from app import pubsub
from classes.base.metaclasses import GripyManagerMeta
from app import log


class GripyManager(pubsub.PublisherMixin, metaclass=GripyManagerMeta):
    """
    The parent class for a Manager.
    
    A Manager is responsible for managing objects throughout the
    program execution. For instance, it is responsible for creating new objects
    and deleting them when they are no longer needed.
    
    Managers are design under "Borg pattern", i.e. all the instances of the 
    class share the same state . This way, when access to a managed object is
    needed an instance of its respective Manager must be created in order to access
    the data.
    """
    _LOADING_STATE = False

    def __init__(self):
        pass
        # self._ownerref = None

    def _get_pubsub_uid(self):
        return self.__class__.__name__

    def is_loading_state(self):
        return self.__class__._LOADING_STATE

    def set_loading_state(self):
        self.__class__._LOADING_STATE = True

    def unset_loading_state(self):
        self.__class__._LOADING_STATE = False

        # Criado por Adriano em 08-11-2018

    def get_children_uids(self, parent_uid=None, recursively=False):
        """
        Given a parent object unique identificator (uid), returns children 
        uids.
        
        Parameters
        ----------
        parent_uid : uid, optional
            The uid for the parent object whose children uids is needed.
        recursively : bool, optional
            Indicates a recursively list of children.
            
        Returns
        -------
        children_uids: list
            A list of uids of a given parent uid. If parent uid is None, all 
            uids are returned. By the way, a recursively search on a parent 
            uid includes its children, 'children of children', etc. 
            If the parent uid given has not children returns a empty list.
        """
        if parent_uid is None:
            return self._data.keys()
        children_uids = self._childrenuidmap[parent_uid]
        if not recursively:
            return children_uids
        else:
            ret_list = []
            ret_list += children_uids
            for child_uid in children_uids:
                ret_list += self.get_children_uids(child_uid, True)
            return ret_list

            # Migrado para a SuperClasse em 10-11-2018

    # TODO: Add recursively to docs.
    def list(self, tid=None, parent_uid=None, recursively=False):
        """
        Return a list of objects being managed by `Manager`.
        
        Parameters
        ----------
        tid : str, optional
            Only objects which type identificator is equal to `tidfilter` will
            be returned.
        parentuidfilter : uid, optional
            Only objects which parent has unique identificator equal to
            `parentuidfilter` will be returned.
        recursively : bool, optional
            Indicates a recursively list of children objects.            
            
        Returns
        -------
        list
            A list of objects that satisfy the given filters.
        
        Examples
        --------
        >>> om = ObjectManager()
        >>> parentobj = om.new('parenttypeid')
        >>> om.add(parentobj)
        True
        >>> childobj = om.new('childtypeid')
        >>> om.add(childobj, parentobj.uid)
        True
        >>> om.list()
        [parentobj, childobj]
        >>> om.list(parentuidfilter=parentobj.uid)
        [childobj]
        >>> om.list(tidfilter='parenttypeid')
        [parentobj]
        >>> om.list(parentuidfilter=parentobj.uid, tidfilter='parenttypeid')
        []
        """
        '''
    		if not recursively:
    			if parentuidfilter is None:
    				children_uids = self._data.keys()
                else:
                    children_uids = self.get_children(parentuidfilter)
    		else:
    			children_uids = self.get_children_uids(parentuidfilter, True)
		'''
        children_uids = self.get_children_uids(parent_uid, True)
        if tid is None:
            return [self.get(child_uid) for child_uid in children_uids]
        return [self.get(child_uid) \
                for child_uid in children_uids \
                if child_uid[0] == tid
                ]

    def exec_query(self, tid, parent_uid=None, *args, **kwargs):
        """
        Execute queries for searching managed objects.
        
        """
        try:
            recursively = kwargs.pop('recursively', False)
            objects = self.list(tid, parent_uid, recursively)
            if not objects: return None
            comparators = self._create_query_comparators(*args)
            ret_list = []
            for obj in objects:
                ok = True
                for (key, operator, value) in comparators:
                    ok = False
                    attr = obj.find_attribute(key)
                    if attr is None:
                        raise Exception('Attribute {} was not found.'.format( \
                            key)
                        )
                    type_ = attr.get('type')
                    value = type_(value)
                    attr_value = obj[key]

                    if operator == '>=':
                        ok = attr_value >= value
                    elif operator == '<=':
                        ok = attr_value <= value
                    elif operator == '>':
                        ok = attr_value > value
                    elif operator == '<':
                        ok = attr_value < value
                    elif operator == '!=':
                        ok = attr_value != value
                    elif operator == '=':
                        ok = attr_value == value

                    if not ok:
                        break
                if ok:
                    ret_list.append(obj)
            # if kwargs:
            orderby = kwargs.get('orderby')
            if orderby and len(ret_list) >= 2:
                aux_list = []
                while len(ret_list) > 0:
                    minor_idx = 0
                    for idx, obj in enumerate(ret_list):
                        if obj[orderby] < ret_list[minor_idx][orderby]:
                            minor_idx = idx
                    aux_list.append(ret_list[minor_idx])
                    del ret_list[minor_idx]
                ret_list = aux_list
            reverse = kwargs.get('reverse')
            if reverse:
                ret_list.reverse()
            return ret_list
        except Exception as e:
            msg = 'ERROR in {}.exec_query({}, {}, {}, {})'.format( \
                self.__class__.__name__, tid, parent_uid, args, kwargs)
            print('\n' + msg)
            raise

    def _create_query_comparators(self, *args):
        """
        Create the comparators used by `.exec_query`.
        
        """
        operators = ['>=', '<=', '>', '<', '!=', '=']
        ret_list = []
        for arg in args:
            operator = None
            for oper in operators:
                if oper in arg:
                    operator = oper
                    break
            if not operator:
                raise ValueError('Operator not found. Valid operators are: {}' \
                                 .format(operators)
                                 )
            ret_list.append((arg.split(operator)[0], operator,
                             arg.split(operator)[1])
                            )
        return ret_list
