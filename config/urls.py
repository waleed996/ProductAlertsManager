from django.urls import path, include
from django.views.generic import TemplateView

urlpatterns = [
    path('product-alerts-manager/api/v1/', include('app.routes.v1.urls')),
    path('docs/swagger', TemplateView.as_view(template_name='templates/swagger-ui.html',
                                              extra_context={'schema_url': 'swagger.json'}), name='swagger-api-docs-ui')
]
