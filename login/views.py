from crispy_forms.helper import FormHelper
from django.contrib.auth.views import LoginView
from django.contrib import messages


class CustomLoginView(LoginView):
    template_name = 'login.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.form_tag = False
        return form

    def form_valid(self, form):
        messages.success(self.request, 'You are now logged in.')
        return super().form_valid(form)
