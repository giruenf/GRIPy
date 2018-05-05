# -*- coding: utf-8 -*-
#
# GRIPy Unit of Measure (UOM) 
# Classes for units of measure and it's conversion
# Universidade Estadual do Norte Fluminense - UENF
# Laboratório de Engenharia de Petróleo - LENEP
# Grupo de Inferência em Reservatório - GIR
# Adriano Paulo Laes de Santana
# March 25th, 2017
#
# The following code is based on Energistics Unit of Measure Dictionary (UOM) V1.0
# Energistics UOM data is distributed under the Energistics License Agreement at http://www.energistics.org. 
# Copyright (c) 2014 Energistics. 

import math        
import xml.etree.ElementTree as ElementTree


UOM_FILENAME = 'basic\\uom\\Energistics_Unit_of_Measure_Dictionary_V1.0.xml'
NAMESPACE_KEY = 'uom'
NAMESPACE_VALUE = 'http://www.energistics.org/energyml/data/uomv1'

UNIT_DIMENSION_SET_KEY = 'unitDimensionSet'
QUANTITY_CLASS_SET_KEY = 'quantityClassSet'
UNIT_SET_KEY = 'unitSet'
REFERENCE_SET_KEY = 'referenceSet'
PREFIX_SET_KEY = 'prefixSet'

TAG_UNIT_DIMENSION_SET = NAMESPACE_KEY + ':' + UNIT_DIMENSION_SET_KEY
TAG_QUANTITY_CLASS_SET = NAMESPACE_KEY + ':' + QUANTITY_CLASS_SET_KEY
TAG_UNIT_SET = NAMESPACE_KEY + ':' + UNIT_SET_KEY
TAG_REFERENCE_SET = NAMESPACE_KEY + ':' + REFERENCE_SET_KEY
TAG_PREFIX_SET = NAMESPACE_KEY + ':' + PREFIX_SET_KEY

namespace = {NAMESPACE_KEY: NAMESPACE_VALUE}


class UOM(object):
    _instance = None
    
    def __init__(self, filename=None):
        if self.__class__._instance:
            raise Exception('Cannot create another UOM instance.')
        self._unit_dimensions = {}
        self._quantity_classes = {}
        self._units = {}
        self._references = {}
        self._prefixes = {}
        if filename:
            self._load_XML(filename)
        self.__class__._instance = self
    
    @classmethod    
    def get(cls):
        if not cls._instance:
            UOM()
        return cls._instance

    def convert(self, value, from_unit_symbol, to_unit_symbol):
        unit_from = self.get_unit(from_unit_symbol)
        if unit_from is None:
            raise Exception('Invalid unit from')
        unit_to = self.get_unit(to_unit_symbol)
        if unit_to is None:
            raise Exception('Invalid unit to')        
        if unit_from.dimension != unit_to.dimension:
            raise Exception('Cannot convert between diferent dimensions.')       
        units_dimension = self.get_unit_dimension(unit_from.dimension)
        #
        if units_dimension.baseForConversion == unit_from.symbol: 
            base_value = value
        else:    
            base_value = (unit_from.A + unit_from.B * value) / (unit_from.C + unit_from.D * value) 
        if units_dimension.baseForConversion == unit_to.symbol:
            return base_value
        return (unit_to.A - unit_to.C * base_value) / (unit_to.D * base_value - unit_to.B)

    def get_unit_dimension(self, dimension):
        return self._unit_dimensions.get(dimension)
    
    def get_quantity_class(self, name):
        return self._quantity_classes.get(name)    
    
    def get_unit(self, symbol):
        return self._units.get(symbol)
    
    def get_reference(self, ID):
        return self._references.get(ID)
    
    def get_prefix(self, symbol):
        return self._prefixes.get(symbol)

    def is_valid_unit(self, unit_symbol, quantity_name=None):
        unit = self.get_unit(unit_symbol)
        if not unit:
            return False
        elif quantity_name is None:
            return True
        quantity = self.get_quantity_class(quantity_name)
        if quantity is None:
            return False
        return unit_symbol in quantity.memberUnit
            
        
    def _load_XML(self, filename):
        tree = ElementTree.parse(filename)
        uds = tree.findall(TAG_UNIT_DIMENSION_SET, namespace)[0]
        qcs = tree.findall(TAG_QUANTITY_CLASS_SET, namespace)[0]
        us = tree.findall(TAG_UNIT_SET, namespace)[0]
        rs = tree.findall(TAG_REFERENCE_SET, namespace)[0]
        ps = tree.findall(TAG_PREFIX_SET, namespace)[0]
        for ud in uds:
            kv = {}
            for attr in ud:
                key = attr.tag.split('}')[1]
                if attr.text:
                    #kv[key] = attr.text.translate(None, '\t\n')
                    kv[key] = attr.text.translate('\t\n')
            self._unit_dimensions[kv['dimension']] = UnitDimension(**kv) 
        for qc in qcs:
            kv = {}
            member_unit = []
            for attr in qc:
                key = attr.tag.split('}')[1]
                if attr.text:
                    if key == 'memberUnit':
                        member_unit.append(attr.text)
                    else:    
                        #kv[key] = attr.text.translate(None, '\t\n')
                        kv[key] = attr.text.translate('\t\n')
            qc = QuantityClass(**kv)
            qc.memberUnit = member_unit
            self._quantity_classes[kv['name']] = qc
        for ref in rs:
            kv = {}
            for attr in ref:
                key = attr.tag.split('}')[1]
                if attr.text:
                    #kv[key] = attr.text.translate(None, '\t\n')
                    kv[key] = attr.text.translate('\t\n')
            self._references[kv['ID']] = Reference(**kv)            
        for pref in ps:
            kv = {}
            for attr in pref:
                key = attr.tag.split('}')[1]
                if attr.text:
                    #kv[key] = attr.text.translate(None, '\t\n')
                    kv[key] = attr.text.translate('\t\n')
            self._prefixes[kv['symbol']] = Prefix(**kv)   
        for unit in us:
            kv = {}
            for attr in unit:
                key = attr.tag.split('}')[1]
                if attr.text:
                    #kv[key] = attr.text.translate(None, '\t\n')
                    kv[key] = attr.text.translate('\t\n')
            self._units[kv['symbol']] = Unit(**kv)    

        

class Unit(object):
    
    def __init__(self, **kwargs):
        self.symbol = kwargs.get('symbol')
        self.name = kwargs.get('name')
        self.dimension = kwargs.get('dimension')
        self.isSI = self._value_parser(kwargs.get('isSI'))
        self.category = kwargs.get('category')
        self.baseUnit = kwargs.get('baseUnit')
        self.conversionRef = kwargs.get('conversionRef')
        self.isExact = self._value_parser(kwargs.get('isExact'))
        self.A = self._value_parser(kwargs.get('A'))
        self.B = self._value_parser(kwargs.get('B'))    
        self.C = self._value_parser(kwargs.get('C'))   
        self.D = self._value_parser(kwargs.get('D'))    
        if self.A is None:
            self.A = 0.0
        if self.B is None:
            self.B = 0.0
        if self.C is None:
            self.C = 0.0
        if self.D is None:
            self.D = 0.0
        self.underlyingDef = kwargs.get('underlyingDef')
        self.description = kwargs.get('description')
        self.isBase = self._value_parser(kwargs.get('isBase'))

    def _value_parser(self, value_str):
        if value_str is None:
            return None
        if value_str == 'true':
            return True
        if value_str == 'false':
            return False
        try:
            return float(value_str)
        except Exception:
            if value_str == 'PI':
                return math.pi
            elif value_str == '2*PI':
                return 2*math.pi
            elif value_str == '4*PI':
                return 4*math.pi
            raise            
        
    def getstate(self):
        state = {
            'symbol': self.symbol,
            'name': self.name,
            'dimension': self.dimension,
            'isSI': self.isSI,
            'category': self.category,
            'baseUnit': self.baseUnit,
            'conversionRef': self.conversionRef,
            'isExact': self.isExact,
            'A': self.A,
            'B': self.B,
            'C': self.C,
            'D': self.D,
            'underlyingDef': self.underlyingDef,
            'description': self.description,
            'isBase': self.isBase
        }
        return state        

        
class QuantityClass(object):
    
    def __init__(self, **kwargs):    
        self.name = kwargs.get('name')
        self.dimension = kwargs.get('dimension')
        self.baseForConversion = kwargs.get('baseForConversion')
        self.alternativeBase = kwargs.get('name')
        self.memberUnit = []
        self.description = kwargs.get('description')
        
    def getstate(self):
        state = {
                'name': self.name,
                'dimension': self.dimension,
                'baseForConversion': self.baseForConversion,
                'alternativeBase': self.alternativeBase,
                'memberUnit': self.memberUnit,
                'description': self.description
        }
        return state
    
    
class UnitDimension(object):
    
    def __init__(self, **kwargs):    
        self.name = kwargs.get('name')
        self.dimension = kwargs.get('dimension')
        self.baseForConversion = kwargs.get('baseForConversion')
        self.canonicalUnit = kwargs.get('canonicalUnit')
        self.description = kwargs.get('description')

        
    def getstate(self):
        state = {
                'name': self.name,
                'dimension': self.dimension,
                'baseForConversion': self.baseForConversion,
                'canonicalUnit': self.canonicalUnit,
                'description': self.description
        }
        return state
    
    
class Reference(object):
    
    def __init__(self, **kwargs):    
        self.ID = kwargs.get('ID')
        self.description = kwargs.get('description')

        
    def getstate(self):
        state = {
                'ID': self.ID,
                'description': self.description
        }
        return state    
    
    
class Prefix(object):
    
    def __init__(self, **kwargs):    
        self.symbol = kwargs.get('symbol')
        self.name = kwargs.get('name')
        self.multiplier = kwargs.get('multiplier')
        
    def getstate(self):
        state = {
                'symbol': self.symbol,
                'name': self.name,
                'multiplier': self.multiplier
        }
        return state        
    
    
uom = UOM(UOM_FILENAME)

"""
def print_(dict_):
    for key, value in dict_.items():
        print key, '-', value
    print    


if __name__ == '__main__':
    uom_ = UOM('D:\\repo\\GRIPy\\DT\\Energistics_Unit_of_Measure_Dictionary_V1.0.xml')
    #print uom_
    #
    unit = uom_.get_unit('km')
    print_(unit.getstate())
    #
    ud = uom_.get_unit_dimension('L')
    print_(ud.getstate())
    #
    qc = uom_.get_quantity_class('length')
    print_(qc.getstate())
    
    print uom_.is_valid_unit('ms', 'length') 
    #value = 1555
    #new_value = UOM_.convert(value, 'g/cm3', 'kg/m3')#, 'g/cm3')
    #print 'new_value:', new_value

"""
