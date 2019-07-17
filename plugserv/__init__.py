from concurrent.futures import ThreadPoolExecutor
import hashlib
import logging

import google_measurement_protocol as gmp

SALT = b'P6e!f3x%rvipP^N4'
DEFAULT_UA = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:15.0) Gecko/20100101 Firefox/15.0.1'


logger = logging.getLogger(__name__)
thread_pool = ThreadPoolExecutor(4)


def get_client_ip(request):
    # cloudflare-specific, should be available in prod
    cf_h = request.headers.get('Cf-Connecting-Ip')
    if cf_h:
        return cf_h

    # proxy ips are appended
    forwarded_h = request.headers.get('X-Forwarded-For')
    if forwarded_h:
        return forwarded_h.split(',')[0].strip()

    # fall back to what may be a proxy's ip
    return request.headers.get('X-Real-Ip', request.headers.get('Remote-Addr'))


def report_ga_event_async(request, tracking_id, **event_kwargs):
    """
    Report a Universal Analytics event in another thread.

    event_kwargs must have category and action, and may have label and value.
    """
    from django.conf import settings  # avoid import-time issues where we get prod settings

    ip = get_client_ip(request)
    if not ip:
        ip = 'anonymous'
    else:
        event_kwargs['uip'] = ip

    # client id must be set (even if we couldn't get an ip)
    # https://support.google.com/analytics/answer/6366371?hl=en#hashed
    h = hashlib.sha256()
    h.update(SALT)
    h.update(ip.encode())
    client_id = h.hexdigest()

    user_agent = request.headers.get('User-Agent', DEFAULT_UA)

    if settings.SEND_GA_EVENTS:
        thread_pool.submit(_report_event, client_id, user_agent, tracking_id, **event_kwargs)


def _report_event(client_id, user_agent, tracking_id, **event_kwargs):
    # without a proper user agent, GA may consider the traffic a bot/crawler (though it may still blacklist us by ip)
    event_kwargs['extra_headers'] = {'User-Agent': user_agent}
    try:
        logger.info("sending ga event: %r", event_kwargs)
        event = gmp.event(**event_kwargs)
        gmp.report(tracking_id, client_id, event)
    except:  # noqa
        logger.exception("failed to report event: %r", event_kwargs)
