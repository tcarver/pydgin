from django.shortcuts import render
from django.contrib.auth.decorators import login_required, permission_required,\
    user_passes_test
from pydgin_auth.decorators import is_in_group
from django.template.context import RequestContext
from rest_framework.authtoken.models import Token
import logging


def index(request):
    if request.user.is_authenticated():
        try:
            token, is_created = Token.objects.get_or_create(user=request.user)  # @UnusedVariable
        except Token.DoesNotExist:
            logging.debug('Exception while creating tokens')
            pass

        # context = RequestContext(request, {'request': request, 'user': request.user, 'api_key': token})
        request_context = RequestContext(request)
        request_context.push({"api_key": token})
        request_context.push({"foo": "boo"})
        print(token)
        return render(request, 'auth_test/index.html', context_instance=request_context)
    else:
        return render(request, 'auth_test/index.html')


def login_success(request):
    return render(request, 'auth_test/auth_test.html')


def check_section_perms(request):
    return render(request, 'auth_test/check_perms.html')


def check_green(request):
    return render(request, 'auth_test/green_page.html')


@login_required(login_url='/accounts/login/')
@permission_required('auth_test.can_read', login_url='/accounts/permission_denied/')
def check_blue(request):
    return render(request, 'auth_test/blue_page.html')


@login_required(login_url='/accounts/login/')
@is_in_group("CURATOR", login_url='/accounts/permission_denied/')
def check_yellow(request):
    return render(request, 'auth_test/yellow_page.html')


@login_required(login_url='/accounts/login/')
@is_in_group("PYDGIN_ADMIN", login_url='/accounts/permission_denied/')
def check_red(request):
    return render(request, 'auth_test/red_page.html')


@login_required(login_url='/accounts/login/')
@user_passes_test(lambda u: u.is_superuser, login_url='/accounts/permission_denied/')
def check_black(request):
    return render(request, 'auth_test/black_page.html')


def check_section_perms_templatetags(request):
    return render(request, 'auth_test/section_check_perms.html')
