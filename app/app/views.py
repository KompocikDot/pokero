from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView
from django.contrib.auth.forms import UserCreationForm

class MainPageView(TemplateView):
    template_name = "main_page.html"

# This view is created only, because built-in django auth does not come with such view.
class RegisterView(CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "register_form.html"

    
