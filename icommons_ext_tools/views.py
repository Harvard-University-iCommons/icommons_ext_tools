from django.shortcuts import render

# TLT-426: For all errors 403, 404, 500 show the custom error page (called 500.html) with appropriate
# modifiers. This keeps to DRY principles by not duplicating template code.

def handler403(request):
    return render(request, '500.html', status=403, dictionary={'unauthorized': 'true'})


def handler404(request):
    return render(request, '500.html', status=404)


def handler500(request):
    return render(request, '500.html')
