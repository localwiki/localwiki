import difflib

from django.db import models
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from django.conf import settings

import diff_match_patch
import daisydiff

class DiffUtilNotFound(Exception):
    """
    No appropriate diff util registered for this object.
    """
    pass

class BaseFieldDiff():
    """
    Simplest diff possible, used when no better option is available.
    Just shows two fields side-by-side, in the case of HTML output.
    To customize how two fields get compared, subclass BaseFieldDiff,
    implement (at minimum) get_diff() and as_html() and register your
    class either for a certain field type or for a specific field of a
    specific model.  See BaseModelDiff for details on the latter.
    
    Here's how you might create your own diff util and register it for
    a field type:
    
    class MyIntegerDiff(BaseFieldDiff):
        def get_diff(self):
            if self.field1 == self.field2:
                return None
            return {'difference': (self.field2 - self.field1)}
        
        def as_html(self):
            d = self.get_diff()
            if d is None:
                return 'Values are the same'
            if d['difference'] > 0:
                return 'New value is larger'
            return 'New value is smaller'
            Unchanged
            
    diff.register(models.IntegerField, MyIntegerDiff)
    """
    template = None
    
    def __init__(self, field1, field2):
        self.field1 = field1
        self.field2 = field2
        
    def get_diff(self):
        """
        Compares the two field values (field1 and field2) and returns a dictionary
        that contains the diffs.  This dictionary can then be used by as_html() for
        rendering HTML.  Returns None if the fields values are equal.
        """
        if self.field1 == self.field2:
            return None
        return { 'deleted': self.field1, 'inserted': self.field2 }
    
    def as_dict(self):
        """
        Returns the diff as a dictionary or array of dictionaries.
        """
        return self.get_diff()
    
    def as_html(self):
        """
        Returns a string of the diff between field1 and field2.  These are normally
        one row of an HTML table, with two cells in a side-by-side diff.
        """
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
    """
    Diff util used for comparing two model instances.  By default, it will compare
    the instances on all of their fields, except AutoFields.
    To customize which fields to compare, subclass BaseModelDiff, setting the
    'fields' or 'excludes' attributes like this:
    
    class MyModelDiff(diff.BaseModelDiff):
        fields =   ('name', 
                    'contents')
                    
    and then register it with your model like this:
    
    diff.register(MyModel, MyModelDiff)
    
    You can also customize how each field is compared by using a tuple
    ('field_name', FieldDiff) instead of just the field names, like this:
    
    class MyModelDiff(diff.BaseModelDiff):
        fields =   ( ('name', diff.TextFieldDiff),
                     ('contents', diff.HtmlFieldDiff),
                   )
    """
    fields = None
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
        """
        Renders the diffs between the model instances as a table, returning an
        HTML string. Only those fields that are different will be rendered as
        rows in the table. Fields that are not different will just be skipped.
        """
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
        """
        Returns a dictionary that contains all field diffs, indexed by field name.
        """
        diff = {}
        diff_utils = {}
        
        if self.fields:
            diff_fields = self.fields
        else:
            diff_fields = [ f.name for f in self.model1._meta.fields ]

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
                
                diff[field.name] = diff_class(
                    getattr(self.model1, field.name),
                    getattr(self.model2, field.name)
                )

        return diff
        
    def __str__(self):
        return self.as_html()
    
    def __unicode__(self):
        """
        For use in templates, returns a safe string.
        """
        return mark_safe(unicode(self.__str__()))
    
class TextFieldDiff(BaseFieldDiff):
    """
    Compares the fields as text and renders the diff in an easy to read format.
    """
    def as_html(self):
        d = self.get_diff()
        if d is None:
            return '<tr><td colspan="2">(No differences found)</td></tr>'
        return render_to_string('diff/text_diff.html', {'diff': d})
    
    def get_diff(self):
        return get_diff_operations_clean(self.field1, self.field2)
    
class HtmlFieldDiff(BaseFieldDiff):
    """
    Compares the fields as HTML and renders them side-by-side, with the
    deleted, inserted, and changed text and elements highlighted.
    To use for a field type, first register in your code like this:
    diff.register(MyHtmlField, diff.HtmlFieldDiff)
    """
    DAISYDIFF_URL = getattr(settings, 'DAISYDIFF_URL', 'http://localhost:8080')
    
    def as_html(self):
        d = self.get_diff()
        if d is None:
            return '<tr><td colspan="2">(No differences found)</td></tr>'
        try:
            return daisydiff.daisydiff(d['deleted'], d['inserted'],
                                       self.DAISYDIFF_URL)
        except:
            return TextFieldDiff(d['deleted'], d['inserted']).as_html()
    
    def get_diff(self):
        if self.field1 == self.field2:
            return None
        return {'deleted': self.field1, 'inserted': self.field2}
        
    
class FileFieldDiff(BaseFieldDiff):
    """
    Compares the fields as file paths and renders links to the files.
    """
    def get_diff(self):
        """
        Returns a dictionary of all the file attributes or None if it's the same file
        """
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
        return render_to_string('diff/file_diff.html', {'diff': d})

class ImageFieldDiff(FileFieldDiff):
    """
    Compares the fields as image file paths and renders the images.
    """
    def as_html(self):
        d = self.get_diff()
        if d is None:
            return '<tr><td colspan="2">(No differences found)</td></tr>'
        return render_to_string('diff/image_diff.html', {'diff': d})
        
def get_diff_operations(a, b):
    """
    Returns the minimal diff operations between two strings, using difflib. 
    """
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

def get_diff_operations_clean(a, b):
    """
    Returns a cleaned-up, more human-friendly set of diff operations between
    two strings.  Uses diff_match_patch.
    """
    if a == b:
        return None
    dmp = diff_match_patch.diff_match_patch()
    dmp.Diff_Timeout = 0.01
    dmp.Diff_EditCost = 4
    
    diff = dmp.diff_main(a, b, False)
    dmp.diff_cleanupSemantic(diff)
    op_map = { diff_match_patch.diff_match_patch.DIFF_DELETE: 'deleted',
               diff_match_patch.diff_match_patch.DIFF_EQUAL: 'equal',
               diff_match_patch.diff_match_patch.DIFF_INSERT: 'inserted'
              }
    return [ { op_map[op]: data } for op, data in diff ]

class Registry(object):
    """
    This tracks what diff util should be used for what model or field.
    """
    def __init__(self):
        self._registry = {}
        
    def register(self, model_or_field, diff_util):
        """
        Registers a diff util for a particular model or field type.
        @param model_or_field: type that will be compared (subclass of Model or Field)
        @param diff_util: class that will do the comparison (subclass of BaseModelDiff
        or BaseFieldDiff, respectively)
        """
        self._registry[model_or_field] = diff_util
        
    def get_diff_util(self, model_or_field):
        if model_or_field in self._registry:
            return self._registry[model_or_field]
        if model_or_field is models.ForeignKey:
            return BaseModelDiff
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
    """
    See Registry.register()
    """ 
    registry.register(model_or_field, diff_util)

def diff(object1, object2):
    """
    Compares two objects (such as model instances) and returns an object that can
    be used to render the differences between the two objects.
    """
    diff_util = registry.get_diff_util(object1.__class__)
    return diff_util(object1, object2)

"""
Built-in diff utils provided for some of the Django field types.
"""
register(models.CharField, TextFieldDiff)
register(models.TextField, TextFieldDiff)
register(models.FileField, FileFieldDiff)
register(models.ImageField, ImageFieldDiff)

