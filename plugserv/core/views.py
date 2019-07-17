import logging
import os
import time

from django.conf import settings
from django.shortcuts import redirect
from django.http import JsonResponse
from django.views.generic import TemplateView
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.cache import cache_control
from django.utils.decorators import method_decorator

from plugserv import report_ga_event_async
from .models import Plug, PlugSerializer, User, UserSerializer

from rest_framework.reverse import reverse
from rest_framework import viewsets, mixins
from rest_framework import permissions
from rest_framework.decorators import list_route, detail_route
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.response import Response
import tldextract

# the venv dir is kept read-only in prod
extract_tld = tldextract.TLDExtract(cache_file=os.path.join(settings.BASE_DIR, '..', 'tld.cache'))
tldextract = None  # prevent accidental usage

logger = logging.getLogger(__name__)


class IsOwnerOrSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, User):
            return obj == request.user
        else:
            return obj.owner == request.user


class UserSelfViewSet(mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    """
    This is your user. Your serve_id is included in the snippet configuration to identify your account.
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrSelf)
    template_name = 'user.html'

    # redirect to the currently-authed user.
    # makes an entry at the top of the browable api listing.
    def list(self, request):
        return redirect(reverse('user-detail', args=[request.user.id], request=request))

    @list_route(renderer_classes=[TemplateHTMLRenderer])
    def hlist(self, request, *args, **kwargs):
        return redirect(reverse('user-hretrieve', args=[request.user.id], request=request))

    @detail_route(renderer_classes=[TemplateHTMLRenderer])
    def hretrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'serializer': serializer})

    @detail_route(renderer_classes=[TemplateHTMLRenderer], methods=['post'])
    def hpatch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'serializer': serializer, 'user': instance})

        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return redirect(reverse('user-hretrieve', args=[request.user.id], request=request))

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)


class PlugViewSet(viewsets.ModelViewSet):
    """
    Use the form below to create or edit a plug.
    To select an individual plug for editing, click its url in the response.
    """
    serializer_class = PlugSerializer
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrSelf)
    template_name = 'plug.html'

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def get_queryset(self):
        return Plug.objects.filter(owner=self.request.user)

    # I'm not sure if I'm missing something, but it seems like DRF's mixins aren't built for use with html at all.
    # These are essentially copied from https://github.com/encode/django-rest-framework/blob/master/rest_framework/mixins.py
    #  except they keep the serializer around rather than throw it away when returning a response.
    @list_route(renderer_classes=[TemplateHTMLRenderer], template_name='plugs.html')
    def hlist(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        # note that this ignores pagination
        return Response({'plugs': queryset})

    @list_route(renderer_classes=[TemplateHTMLRenderer])
    def hnew(self, request, *args, **kwargs):
        serializer = self.get_serializer()
        return Response({'serializer': serializer})

    @list_route(renderer_classes=[TemplateHTMLRenderer], methods=['post'])
    def hcreate(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response({'serializer': serializer})
        self.perform_create(serializer)
        return redirect(reverse('plug-hlist', request=request))

    @detail_route(renderer_classes=[TemplateHTMLRenderer], methods=['post'])
    def hdestroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return redirect(reverse('plug-hlist', request=request))

    @detail_route(renderer_classes=[TemplateHTMLRenderer])
    def hretrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response({'serializer': serializer, 'plug': instance})

    @detail_route(renderer_classes=[TemplateHTMLRenderer], methods=['post'])
    def hpatch(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response({'serializer': serializer, 'plug': instance})

        self.perform_update(serializer)
        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return redirect(reverse('plug-hretrieve', args=args, kwargs=kwargs, request=request))


@method_decorator(cache_control(public=True, max_age=3600), name='dispatch')
class CachedView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cached_view'] = True  # base.html looks for this
        context['serve_id'] = settings.EXAMPLE_SERVE_ID
        return context


class LoggedOutView(CachedView):
    template_name = 'logged_out.html'


class DocsView(CachedView):
    template_name = 'docs.html'


class PrivacyView(CachedView):
    template_name = 'privacy.html'


class TermsView(CachedView):
    template_name = 'terms.html'


class JsV1(CachedView):
    # this is a view rather than a static file to more easily control CORS and the path.
    # since it's cached via cloudflare it shouldn't make a big performance difference.
    template_name = 'plugserv_v1.js'

    def dispatch(self, *args, **kwargs):
        response = super(JsV1, self).dispatch(*args, **kwargs)
        response['Access-Control-Allow-Origin'] = '*'
        response['Content-Type'] = 'application/javascript'
        return response


def _get_origin(request):
    origin = None
    if 'origin' in request.headers:
        extracted = extract_tld(request.headers['origin'])
        if extracted:
            # we may want to handle subdomains differently at some point
            origin = '.'.join(e for e in extracted if e)
            logger.info("extracted origin %r to %r", request.headers['origin'], origin)
        else:
            logger.warning("could not extract domain from %r", request.headers['origin'])

    return origin


@require_http_methods(['GET'])
def serve_plug(request, serve_id):
    origin = _get_origin(request)

    plugs = list(Plug.objects.filter(owner__serve_id=serve_id).exclude(domain=origin).order_by('id'))
    days_into_year = time.localtime().tm_yday
    plug = plugs[days_into_year % len(plugs)]
    logger.info("serving %r to %r", plug, origin)

    click_url = None
    if plug.owner.ga_tracking_id:
        report_ga_event_async(
            request,
            plug.owner.ga_tracking_id,
            category='impression',
            action=plug.domain,
            label=origin,
        )
        click_url = request.build_absolute_uri(reverse('track_click', args=(plug.id, )))

    report_ga_event_async(
        request,
        settings.GA_TRACKING_ID,
        category='impression',
        action=plug.domain,
        label=origin,
    )
    res = JsonResponse({
        'click_url': click_url,
        'plug': PlugSerializer(plug, context={'request': request}).data
    })
    res["Access-Control-Allow-Origin"] = "*"
    res["Access-Control-Allow-Methods"] = "GET, OPTIONS"

    return res


@csrf_exempt
@require_http_methods(['POST'])
def track_click(request, plug_id):
    origin = _get_origin(request)

    plug = Plug.objects.get(id=plug_id)
    if plug.owner.ga_tracking_id:
        report_ga_event_async(
            request,
            plug.owner.ga_tracking_id,
            category='click',
            action=plug.domain,
            label=origin,
        )
    else:
        logger.warn("click tracking requested for %r but GA id not set", plug)

    report_ga_event_async(
        request,
        settings.GA_TRACKING_ID,
        category='click',
        action=plug.domain,
        label=origin,
    )

    res = JsonResponse({})
    res["Access-Control-Allow-Origin"] = "*"
    res["Access-Control-Allow-Methods"] = "POST, OPTIONS"

    return res
