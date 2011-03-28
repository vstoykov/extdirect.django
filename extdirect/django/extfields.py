#
# ExtJs Field models
#

#
# MISSING : 
#

#'CommaSeparatedIntegerField'    : {'type':'string'}
#'FileField'                     : {'type':'string'}
#'FilePathField'                 : {'type':'string'} 
#'ImageField'                    : {'type':'string'}
#'IPAddressField'                : {'type':'string'}
#'NullBooleanField'              : {'type':'boolean'}
#'PositiveIntegerField'          : {'type':'int'}
#'PositiveSmallIntegerField'     : {'type':'int'}
#'SmallIntegerField'             : {'type':'int'}
#'TextField'                     : {'type':'string'}
 
 
import datetime

from django.core.urlresolvers import reverse

class Field(object):
    WIDTH = None
    def __init__(self, field):
        self.field = field  # django field
    
    def getEditor(self, initialValue = False):
        label = self.field.name
        if self.field.verbose_name:
            label = self.field.verbose_name
        if not self.field.blank:
            label += '*'
        conf = {
            'xtype':'textfield'
            ,'fieldLabel':label
            ,'allowBlank':self.field.blank
            ,'name':self.field.name 
            
            }
        
        if initialValue:
            conf['value'] = self.getValue(initialValue)
        if getattr(self.field, 'max_length', None):
            pixels = self.field.max_length*5
            if pixels<40:
                pixels=40
            if pixels>300:
                pixels=300
            conf['width'] = pixels
        if self.WIDTH:  
            conf['width'] = self.WIDTH
        # disable some fields : eg: autofields and auto datetimefields
        if not self.field.editable or self.field.__class__.__name__ == 'AutoField':
            conf = {
                'xtype':'hidden'
                ,'disabled':True
                ,'editable':False
                ,'name':self.field.name
                }
            
        #if self.field.name in  .in _get_validation_exclusions
        return conf
        
    def getReaderConfig(self):
        conf = {
                'name': self.field.name
                ,'allowBlank': self.field.blank
                }
        return conf
        
        
    def getColumnConfig(self):
        conf = {
            'header': self.field.verbose_name, 
            'width': 40, 
            'sortable': True, 
            'dataIndex': self.field.name,
            'editor':self.getEditor()
        }
        if self.WIDTH:  
            conf['width'] = self.WIDTH
        return conf

    def parseValue(self, value):
        # called by the handler
        # transform input data to fit field format
        return value
    
    def getValue(self, value):
        # format data for ExtJs emitter
        return value
        
class AutoField(Field):
    WIDTH=40
    def getEditor(self, initialValue = False):
        conf = super(AutoField, self).getEditor(initialValue = initialValue)
        conf.update( {'xtype':'hidden', 'editable':False} )
        return conf
        
    def getColumnConfig(self):
        conf = super(AutoField, self).getColumnConfig()
        conf['hidden'] = True
        return conf
        
class EmailField(Field):
    WIDTH=70
    def getEditor(self, initialValue = False):
        conf = super(EmailField, self).getEditor(initialValue = initialValue)
        conf.update( {'xtype':'textfield', 'vtype':'email'} )
        return conf
        
class URLField(Field):
    WIDTH=70
    def getEditor(self, initialValue = False):
        conf = super(URLField, self).getEditor(initialValue = initialValue)
        conf.update( {'xtype':'textfield', 'vtype':'url'} )
        return conf

class CharField(Field):
    def getEditor(self, initialValue = False):
        conf = super(CharField, self).getEditor(initialValue = initialValue)
        if getattr(self.field, 'choices', None):
            choices =  {
                'xtype':'combo'
                ,'displayField':'value'
                ,'valueField':'id'
                ,'mode':'local'
                ,'triggerAction':'all'
                ,'editable':False
                ,'forceSelection': True
                ,'store':{
                    'xtype':'simplestore'
                    ,'fields':['id','value']
                    ,'data':self.field.choices
                }
            }
            conf.update( choices )
        return conf

        return {'xtype':'textfield'}
        
 
 
            
class DecimalField(Field):
    FORMAT_RENDERER = '0.00'
    TYPE = 'float'
    def getEditor(self, initialValue = False):
        conf = super(DecimalField, self).getEditor(initialValue = initialValue)
        conf.update( {'xtype':'numberfield', 'style':'text-align:right', 'width':50} )
        return conf

    def getReaderConfig(self):
        conf = super(DecimalField, self).getReaderConfig()
        conf['type'] = self.TYPE
        return conf
        
    def getColumnConfig(self):
        conf = super(DecimalField, self).getColumnConfig()
        conf['xtype'] = 'numbercolumn'
        conf['align'] = 'right'
        conf['format'] = self.FORMAT_RENDERER
        conf['width'] = 50
        return conf
        
    def parseValue(self, value):
        if value:
            value = str(value)
        return value

class IntegerField(DecimalField):
    FORMAT_RENDERER = '0'
    TYPE = 'int'
  
FloatField = DecimalField
                    
                    
                    
                    
class DateTimeField(Field):
    FORMAT = 'Y-m-d H:i:s'
    FORMAT_RENDERER = 'Y-m-d H:i'
    EDITOR_XTYPE = 'datefield'
    FORMAT_PARSE = '%Y-%m-%dT%H:%M:%S'
    WIDTH = 50
    def getEditor(self, initialValue = False):
        conf = super(DateTimeField, self).getEditor(initialValue = initialValue)
        conf.update( {'xtype':self.EDITOR_XTYPE, 'format':self.FORMAT} )
        return conf

    def getReaderConfig(self):
        conf = super(DateTimeField, self).getReaderConfig()
        conf['dateFormat'] = self.FORMAT
        conf['type'] = 'date'
        return conf
        
    def getColumnConfig(self):
        conf = super(DateTimeField, self).getColumnConfig()
        conf['xtype'] = 'datecolumn'
        conf['align'] = 'center'
        conf['width'] = self.WIDTH
        conf['format'] = self.FORMAT_RENDERER
        return conf
     
    def parseValue(self, value):
        if value:
            value = datetime.datetime.strptime(value, self.FORMAT_PARSE)
        return value
     
class DateField(DateTimeField):
    FORMAT = 'Y-m-d'
    FORMAT_RENDERER = 'Y-m-d'
    FORMAT_PARSE = '%Y-%m-%d'
    WIDTH = 30
    def parseValue(self, value):
        if value:
            if value.find('T')>0:
                value = value.split('T')[0]
            value = datetime.datetime.strptime(value, self.FORMAT_PARSE).date()
        return value
    
class TimeField(DateTimeField):
    FORMAT = 'H:i:s'
    FORMAT_RENDERER = 'H:i'
    EDITOR_XTYPE = 'timefield'
    FORMAT_PARSE = '%H:%M:%S'
    WIDTH = 30
    def parseValue(self, value):
        if value:
            if value.find('T')>0:
                value = value.split('T')[1]
            value = datetime.datetime.strptime(value, self.FORMAT_PARSE).time()
        return value
     

     
     
     
     
     
class BooleanField(Field):

    WIDTH=30
    
    def getEditor(self, initialValue = False):
        conf = super(BooleanField, self).getEditor(initialValue = initialValue)
        conf.update( {'xtype':'checkbox'} )
        if initialValue == True:
            conf.update( {'checked':True} )
        return conf
        
    def getColumnConfig(self):
        conf = super(BooleanField, self).getColumnConfig()
        conf['xtype'] = 'checkcolumn'
        return conf
    def getReaderConfig(self):
        conf = super(BooleanField, self).getReaderConfig()
        conf['type'] = 'bool'
        return conf


class ForeignKey(Field):
    MANYTOMANY = False
    RENDERER = 'Ext.django.FKRenderer'
    def getEditor(self, initialValue = False):
        conf = super(ForeignKey, self).getEditor(initialValue = initialValue)
        #REST_index_url = reverse('modelIndex', args=(self.field.related.parent_model._meta.app_label,  self.field.related.parent_model._meta.object_name))
        REST_index_url='/fake'
        conf.update( {'xtype':'djangocombo', 'enableMultiSelect':self.MANYTOMANY, 'model':'%s.%s' % (self.field.related.parent_model._meta.app_label,  self.field.related.parent_model._meta.object_name)} )
        return conf
        
    def getColumnConfig(self):
        conf = super(ForeignKey, self).getColumnConfig()
        conf['related'] = True
        conf['renderer'] = {'fn':self.RENDERER, 'scope':'this'}
        return conf
        
    def getReaderConfig(self):
        conf = super(ForeignKey, self).getReaderConfig()
        conf['defaultValue'] = ''
        return conf
        
    def parseValue(self, value):
        if value:
            value = self.parseFK(self.field.rel.to, value)[0]
        if not value:
            value = None
        return value
 
    def parseFK( self, cls, value ):
        """ translates FK or M2M values to instance list """
        relateds = []
        if isinstance(value, list):
            for id in value:
                if isinstance(id, dict) and id.has_key('id'):
                    item = cls.objects.get(pk = id['id'])
                else:
                    item = cls.objects.get(pk = id)
                relateds.append( item )
        elif isinstance(value, dict) and value.has_key('id'):
            relateds.append( cls.objects.get(pk = value['id']) )
        else:
            relateds.append( cls.objects.get(pk = value) )
        return relateds
        
class ManyToManyField(ForeignKey):
    MANYTOMANY = True
    RENDERER = 'Ext.django.M2MRenderer'
    
    def parseValue(self, value):
        if value:
            value = self.parseFK(self.field.rel.to, value)
        return value
 
 