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
        self._ownerref = None
    
    def is_loading_state(self):
        return self.__class__._LOADING_STATE 

    def get_publisher_name(self):
        return self.__class__.__name__
       
    def do_query(self, tid, parent_uid=None, *args, **kwargs):
        try:
            objects = self.list(tid, parent_uid)
            if not objects: return None  
            comparators = self._create_comparators(*args)  
            ret_list = []
            for obj in objects:
                ok = True
                for (key, operator, value) in comparators:
                    ok = False
                   
                    attr = obj._ATTRIBUTES.get(key)
                    # TODO: acertar isso, pois a linha de cima deve servir de atalho
                    # para obj.model de forma transparente
                    obj_model = False
                    if attr is None:
                        attr = obj.model._ATTRIBUTES.get(key)
                        obj_model = True

                    type_ = attr.get('type')
                    value = type_(value)

                    if obj_model:
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
                        
                    else:
                        if operator == '>=':
                            ok = obj[key] >= value
                        elif operator == '<=':
                            ok = obj[key] <= value                  
                        elif operator == '>':
                            ok = obj[key] > value
                        elif operator == '<':
                            ok = obj[key] < value     
                        elif operator == '!=':
                            ok = obj[key] != value
                        elif operator == '=':
                            ok = obj[key] == value
                            
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
        except Exception as e:
            print ('\nERROR in {}.do_query({}, {}, {}, {})'.format( \
                   self.__class__.__name__,tid, parent_uid, args, kwargs)
            )
            raise
            
            
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
        
    
    
    
