import os
import urlparse

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.views.generic.simple import direct_to_template


def ck_upload(request, upload_folder):
    """
    Save file uploaded via CKEditor.
    """
    error_message = 'Unable to upload'

    upload_location = os.path.join(settings.MEDIA_ROOT, upload_folder)
    upload_url = urlparse.urljoin(settings.MEDIA_URL, upload_folder)

    if request.method == "POST":
        filesystem = FileSystemStorage(location=upload_location,
                                       base_url=upload_url)
        try:
            uploaded_file = request.FILES['upload']
            saved_file = filesystem.save(uploaded_file.name, uploaded_file)
            saved_url = filesystem.url(saved_file)
        except Exception:
            return ck_upload_result(request, message=error_message)
    else:
        ck_upload_result(request, message=error_message)

    return ck_upload_result(request, url=saved_url)


def ck_upload_result(request, url='', message=''):
    """
    Notify CKEditor of upload via JS callback
    """
    try:
        callback = request.GET['CKEditorFuncNum']
    except KeyError:
        callback = ''

    context = {
        'callback': callback,
        'saved_url': url,
        'message': message,
        }

    return direct_to_template(request, 'ckeditor/upload_result.html', context)
