"""
URLs for edx_rbac.
"""

from django.urls import re_path
from django.views.generic import TemplateView

urlpatterns = [
    re_path(r'', TemplateView.as_view(template_name="edx_rbac/base.html")),
]
