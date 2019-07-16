from django.urls import path, include

from . import views

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'plugs', views.PlugViewSet, 'plug')
router.register(r'user', views.UserSelfViewSet, 'user')

urlpatterns = [
    path('', views.LoggedOutView.as_view()),
    path('docs', views.DocsView.as_view(), name='docs'),
    path('privacy', views.PrivacyView.as_view(), name='privacy'),
    path('terms', views.TermsView.as_view(), name='terms'),
    path('api/', include(router.urls)),
    path('serve/<uuid:serve_id>', views.serve_plug, name='serve_plug'),
    path('tc/<int:plug_id>', views.track_click, name='track_click'),
    path('js/v1/plugserv.js', views.JsV1.as_view(), name='js_v1'),
]
