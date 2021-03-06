from django.conf import settings
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth.views import PasswordChangeView
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, UpdateView
from django_sitemaps import Sitemap
from rolepermissions.checkers import has_role

from pythonpro.core.forms import LeadForm, UserEmailForm, UserSignupForm
from pythonpro.core.models import User
from pythonpro.domain import user_facade


def index(request):
    return render(request, 'core/index.html', {'form': UserSignupForm()})


def thanks(request):
    return render(request, 'core/lead_thanks.html', {})


@login_required
def lead_change_password(request):
    if not has_role(request.user, 'lead'):
        return redirect(reverse('core:index'))

    if request.method == 'POST':
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important!
            return redirect(reverse('core:thanks'))
    else:
        form = SetPasswordForm(request.user)
    return render(request, 'core/lead_change_password.html', {
        'form': form
    })


def teck_talks(request):
    return render(request, 'core/tech_talks.html', {})


def podcast(request):
    return render(request, 'core/podcast.html', {})


@login_required
def profile(request):
    return render(request, 'core/profile_detail.html', {})


def sitemap(request):
    map = Sitemap(build_absolute_uri=request.build_absolute_uri, )

    named_views = [
        'core:index',
        'core:lead_landing',
        'client_landing_page',
        'member_landing_page',
        'core:podcast',
        'core:tech_talks',
        'modules:index',
        'launch:landing_page',
        'launch:cpl1',
        'launch:cpl2',
        'launch:cpl3',
    ]
    for section in named_views:
        map.add(reverse(section), changefreq='weekly')

    return map.response(
        pretty_print=settings.DEBUG, )


class _ProfileUpdateName(UpdateView):
    model = User
    fields = ('first_name',)
    template_name = 'core/profile_name.html'
    success_url = reverse_lazy('core:profile')

    def get_object(self, queryset=None):
        return self.request.user


profile_name = login_required(_ProfileUpdateName.as_view())


class _ProfileUpdateEmail(UpdateView):
    form_class = UserEmailForm
    template_name = 'core/profile_email.html'
    success_url = reverse_lazy('core:profile')

    def get_object(self, queryset=None):
        return self.request.user

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


profile_email = login_required(_ProfileUpdateEmail.as_view())


class _ProfileChangePassword(PasswordChangeView):
    template_name = 'core/profile_password.html'
    success_url = reverse_lazy('core:index')


profile_password = _ProfileChangePassword.as_view()


class _WaitingListView(TemplateView):
    template_name = 'core/waiting_list.html'


waiting_list = _WaitingListView.as_view()


def _lead_landing(request, template_name='core/lead_landing_page.html', form_action=None):
    form_action = reverse('core:lead_form') if form_action is None else form_action
    return render(request, template_name, context={'form': LeadForm(), 'form_action': form_action})


def lead_landing(request):
    """
    View with lead landing page
    :param request:
    :return:
    """
    return _lead_landing(request)


def lead_landing_lite(request):
    """
    View with lead landing page lite version
    :param request:
    :return:
    """
    return _lead_landing(request, template_name='core/lead_landing_lite_page.html')


def lead_landing_with_no_offer(request):
    """
    View with lead landing page normal version and no offer in sequence
    :param request:
    :return:
    """
    return _lead_landing(request, form_action=reverse('core:lead_form_with_no_offer'))


def programmer_week_ty(request):
    """
    View with lead landing page
    :param request:
    :return:
    """
    return render(request, 'core/lead_landing_page.html', context={'form': UserSignupForm()})


def _lead_form(request, redirect_to_OTO=True, *args, **kwargs):
    if request.method == 'GET':
        form = UserSignupForm()
        return render(request, 'core/lead_form_errors.html', context={'form': form})

    source = request.GET.get('utm_source', default='unknown')
    first_name = request.POST.get('first_name')
    email = request.POST.get('email')

    try:
        user = user_facade.register_lead(first_name, email, source)
    except user_facade.UserCreationException as e:
        return render(request, 'core/lead_form_errors.html', context={'form': e.form}, status=400)

    login(request, user)

    if redirect_to_OTO:
        return redirect(reverse('payments:client_landing_page_oto'))
    else:
        return redirect(reverse('core:thanks'))


def lead_form(request):
    return _lead_form(request)


def lead_form_with_no_offer(request):
    return _lead_form(request, redirect_to_OTO=False)


def linktree(request):
    return render(request, 'core/linktree.html', {})
