from django.test import TestCase
from django.db import models
from forms import MergeModelForm, PageForm
from pages.models import Page

class PageTest(TestCase):
    def test_merge_conflict(self):
        p = Page()
        p.content = '<p>old content</p>'
        p.name = 'Front Page'
        p.save()
        
        a = PageForm(instance=p)
        b = PageForm(instance=p)
        b_post = b.initial
        b_post['content'] = '<p>b content</p>'
        b = PageForm(b_post, instance=p)
        self.failUnless(b.is_valid())
        b.save()
        
        p = Page.objects.get(pk=p.pk)
        a_post = a.initial
        a_post['content'] = '<p>a content</p>'
        a = PageForm(a_post, instance=p)
        self.failIf(a.is_valid())
        self.failUnless(PageForm.conflict_warning in str(a.errors))
        
        a_post = a.data
        a = PageForm(a_post, instance=p)
        self.failUnless(a.is_valid())
        a.save()
        p = Page.objects.get(pk=p.pk)
        self.failUnless('Edit conflict!' in p.content)

class TestModel(models.Model):
    save_time = models.DateTimeField(auto_now=True)
    contents = models.TextField()
            
class TestForm(MergeModelForm):
    class Meta:
        model = TestModel
        
class TestMergeForm(MergeModelForm):
    class Meta:
        model = TestModel
    
    def merge(self, yours, theirs, ancestor):
        yours['contents'] += theirs['contents']
        return yours

class MergeModelFormTest(TestCase):
    
    def test_get_version_date(self):
        """
        Should return empty string or value of auto_now field
        """
        m = TestModel()
        m.contents = 'abc'
        f = TestForm(instance=m)
        # before save, should return empty string
        self.failUnless(f.get_version_date(m) == '')
        m.save()
        # after save, should return value of auto_now field
        self.failUnless(f.get_version_date(m) == m.save_time)
        
    def test_renders_version_date(self):
        """
        Should output current version in form
        """
        m = TestModel()
        m.contents = 'abc'
        m.save()
        f = TestForm(instance=m)
        self.failUnless(str(m.save_time) in f.as_table())
        
    def test_detects_conflict(self):
        """
        Should raise exception if the model object has been changed since form was created
        """
        m_old = TestModel()
        m_old.contents = 'old contents'
        m_old.save()
        # a and b get a form
        a = TestForm(instance=m_old)
        b = TestForm(instance=m_old)
        
        #b edits and posts
        b_post = b.initial
        b_post['contents'] = 'b contents'
        b = TestForm(b_post, instance=m_old)
        self.failUnless(b.is_valid()) 
        b.save()
        m_new = TestModel.objects.get(pk=m_old.pk)
        
        #a edits and posts
        a_post = a.initial
        a_post['contents'] = 'a contents'
        a = TestForm(a_post, instance=m_new)
        self.failIf(a.is_valid())
        self.failUnless(MergeModelForm.conflict_warning in str(a.errors))
        
        #repeated save with the same form rendered again should work, though
        a_post = a.data
        a = TestForm(a_post, instance=m_new)
        self.failUnless(a.is_valid())
        a.save()
        m_new = TestModel.objects.get(pk=m_old.pk)
        self.failUnless(m_new.contents == 'a contents')
        
    def test_detects_conflict_and_merges(self):
        """
        Should call merge() when there is a conflict
        """
        m_old = TestModel()
        m_old.contents = 'old contents'
        m_old.save()
        # a and b get a form
        a = TestMergeForm(instance=m_old)
        b = TestMergeForm(instance=m_old)
        
        #b edits and posts
        b_post = b.initial
        b_post['contents'] = 'def'
        b = TestMergeForm(b_post, instance=m_old)
        self.failUnless(b.is_valid()) 
        b.save()
        m_new = TestModel.objects.get(pk=m_old.pk)
        
        #a edits and posts
        a_post = a.initial
        a_post['contents'] = 'abc'
        a = TestMergeForm(a_post, instance=m_new)
        #this should pass because TestMergeForm will merge anything
        self.failUnless(a.is_valid())
        a.save()
        m_new = TestModel.objects.get(pk=m_old.pk)
        # merge() in this case concatenates the two versions
        self.failUnless(m_new.contents == 'abcdef')
        
