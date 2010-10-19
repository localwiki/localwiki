from django.shortcuts import render_to_response

def debug(request):
    info = {
      'message': 'hi',
    }
    return render_to_response('debug.html', { 'info': info })
