import os
import urlparse

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.views.generic.simple import direct_to_template

@csrf_exempt
def ck_upload(request, upload_folder):
    error_message = 'Unable to upload'
    
    upload_location = os.path.join(settings.MEDIA_ROOT, upload_folder)
    upload_url = urlparse.urljoin(settings.MEDIA_URL, upload_folder)
    
    if request.method == "POST":
        filesystem = FileSystemStorage(location=upload_location, base_url=upload_url)
        try:
            uploaded_file = request.FILES['upload']
            saved_file = filesystem.save(uploaded_file.name, uploaded_file)
            saved_url = filesystem.url(saved_file)
        except Error:
            return HttpResponse(error_message)
          
        try:
            callback = request.GET['CKEditorFuncNum']
        except KeyError:
            callback = ''
    else:
        return HttpResponse(error_message)
         
    context = {
        'callback': callback,
        'saved_url': saved_url,
        }
    
    return direct_to_template(request, 'ckeditor/upload_result.html', context)