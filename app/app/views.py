import logging
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.forms import UserCreationForm

logger = logging.getLogger(__name__)

class MainPageView(TemplateView):
    template_name = "main_page.html"

    def get(self, request, *args, **kwargs):
        # <--- 3. Przykładowy log
        logger.info(f"Main page accessed from IP: {request.META.get('REMOTE_ADDR')}")
        return super().get(request, *args, **kwargs)

# This view is created only, because built-in django auth does not come with such view.
class RegisterView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "register_form.html"

    def form_valid(self, form):
        # <--- Log: Successful registration
        logger.info(f"New user registered: {form.cleaned_data.get('username')}")
        return super().form_valid(form)
