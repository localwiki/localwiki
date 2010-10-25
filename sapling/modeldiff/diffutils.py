import difflib

from django.db import models
from django.template.loader import render_to_string
from django.utils.safestring import SafeString, mark_safe


class DiffUtilNotFound(Exception):
    '''
    No appropriate diff util registered for this object
    '''
    pass

class BaseFieldDiff():
    '''
    Simplest diff possible, used when no better option is available.
    Just shows two fields side-by-side, in the case of HTML output.
    '''
    template = None
    
    def __init__(self, field1, field2):
        self.field1 = field1
        self.field2 = field2
        
    def get_diff(self):
        if self.field1 == self.field2:
            return None
        return { 'deleted': self.field1, 'inserted': self.field2 }
    
    def as_dict(self):
        '''
        Returns the diff as a dictionary or array of dictionaries
        '''
        return self.get_diff()
    
    def as_html(self):
        '''
        Returns a string of the diff between field1 and field2.  These are normally
        one row of an HTML table, with two cells in a side-by-side diff.
        '''
        diff = self.as_dict()
        if self.template:
            return render_to_string(self.template, diff)
        
        if diff is None:
            return '<tr><td colspan="2">(No differences found)</td></tr>'
        return '<tr><td>%s</td><td>%s</td></tr>' % (self.field1, self.field2)
        
    def __str__(self):
        return self.as_html()
    
    def __unicode__(self):
        return mark_safe(unicode(self.__str__()))
    
class BaseModelDiff(object):
    fields = None
    template = None
    excludes = ()
    
    def __init__(self, model1, model2):
        self.model1 = model1
        self.model2 = model2
    
    def as_dict(self):
        diffs = {}
        for field, field_diff in self.get_diff().items():
            field_diff_dict = field_diff.as_dict()
            if field_diff_dict:
                diffs[field] = field_diff_dict
        if not diffs:
            return None
        return diffs
    
    def as_html(self):
        diffs = self.get_diff()
        diff_str = []
        if self.fields:
            display_order = self.fields
        else:
            display_order = diffs.keys()
        for name in display_order:
            if not isinstance(name, basestring):
                name = name[0]
            if diffs[name].get_diff():
                diff_str.append('<tr><td colspan="2">%s</td></tr>' % (name,))
                diff_str.append('%s' % (diffs[name],))
        if diff_str:
            return '\n'.join(diff_str)
        return '<tr><td colspan="2">No differences found</td></tr>'
            
    def get_diff(self):
        '''
        Returns a dictionary that contains all field diffs, indexed by field name.
        '''
        diff = {}
        diff_utils = {}
        
        if self.fields:
            diff_fields = self.fields
        else:
            diff_fields = self.model1._meta.get_all_field_names()
            
        for name in diff_fields:
            if isinstance(name, basestring):
                field = self.model1._meta.get_field(name)
                diff_class = registry.get_diff_util(field.__class__)
            else:
                field = self.model1._meta.get_field(name[0])
                diff_class = name[1]
            diff_utils[field] = diff_class
                
        for field, diff_class in diff_utils.items():
            if not (isinstance(field, (models.AutoField,
                                       ))
                    ):
                if field.name in self.excludes:
                    continue
                
                field_values = [getattr(o, field.name) for o in (self.model1, self.model2)]
                diff[field.name] = diff_class(field_values[0], field_values[1])
        return diff
        
    def __str__(self):
        return self.as_html()
    
    def __unicode__(self):
        '''
        For use in templates, returns a safe string.
        '''
        return mark_safe(unicode(self.__str__()))
    
class TextFieldDiff(BaseFieldDiff):
    def as_html(self):
        d = self.get_diff()
        if d is None:
            return '<tr><td colspan="2">(No differences found)</td></tr>'
        return render_to_string('modeldiff/text_diff.html', {'diff': d})
    
    def get_diff(self):
        return get_diff_operations(self.field1, self.field2)
    
class FileFieldDiff(BaseFieldDiff):
    
    def get_diff(self):
        '''
        Returns a dictionary of all the file attributes or None if it's the same file
        '''
        if self.field1 == self.field2:
            return None
        
        diff = {
                'name': { 'deleted': self.field1.name, 'inserted': self.field2.name },
                'url': { 'deleted': self.field1.url, 'inserted': self.field2.url },
               }
        return diff
    
    def as_html(self):
        d = self.get_diff()
        if d is None:
            return '<tr><td colspan="2">(No differences found)</td></tr>'
        return render_to_string('modeldiff/file_diff.html', {'diff': d})

class ImageFieldDiff(FileFieldDiff):
    def as_html(self):
        d = self.get_diff()
        if d is None:
            return '<tr><td colspan="2">(No differences found)</td></tr>'
        return render_to_string('modeldiff/image_diff.html', {'diff': d})
        
def get_diff_operations(a, b):
    if a == b:
        return None
    operations = []
    sequence_matcher = difflib.SequenceMatcher(None, a, b)
    for opcode in sequence_matcher.get_opcodes():

        operation, start_a, end_a, start_b, end_b = opcode

        deleted = ''.join(a[start_a:end_a])
        inserted = ''.join(b[start_b:end_b])
        if operation == 'equal':
            operations.append({ 'equal' : inserted })
        else:
            operations.append({ 'deleted': deleted,
                                'inserted': inserted })
    return operations
    
class Registry(object):
    
    def __init__(self):
        self._registry = {}
        
    def register(self, model_or_field, diff_util):
        self._registry[model_or_field] = diff_util
        
        
    def get_diff_util(self, model_or_field):
        if model_or_field in self._registry:
            return self._registry[model_or_field]
        
        if model_or_field is models.Model:
            return BaseModelDiff
        if model_or_field is models.Field:
            return BaseFieldDiff
        # unregistered, try the base class
        if model_or_field.__base__ is not object:
            return self.get_diff_util(model_or_field.__base__)
        
        raise DiffUtilNotFound
        
registry = Registry()

def register(model_or_field, diff_util):
    registry.register(model_or_field, diff_util)

def diff(object1, object2):
    diff_util = registry.get_diff_util(object1.__class__)
    return diff_util(object1, object2)

register(models.CharField, TextFieldDiff)
register(models.TextField, TextFieldDiff)
register(models.FileField, FileFieldDiff)
register(models.ImageField, ImageFieldDiff)
