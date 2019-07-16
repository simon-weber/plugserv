function _plugserve(config) {
  /* config must have:
    * elementId: dom element of which to set innerHTML
    * endpoint: a plugserve serve/... url
  */
  var request = new XMLHttpRequest();
  request.open('GET', config.endpoint);
  request.responseType = 'json';
  request.send();
  request.onload = function() {
    var res = request.response;
    var e = document.getElementById(config.elementId);
    e.innerHTML = res.plug.html_content;
    console.log("plugserv: updated", e, "with", res.plug.html_content);
    if (res.click_url) {
      if (!navigator.sendBeacon) {
        console.warn("plugserv: sendBeacon unavailable, clicks not being sent");
      } else if (window["_gaUserPrefs"] && window['_gaUserPrefs'].ioo && window['_gaUserPrefs'].ioo()) {
        /* https://news.ycombinator.com/item?id=18685854 */
        console.warn("plugserv: GA opt-out detected, clicks not being sent");
      } else {
        e.addEventListener('click', function() {
          if (navigator.sendBeacon(res.click_url, '')) {
            console.log("plugserv: beacon request queued");
          } else {
            console.warn("plugserv: beacon request not queued");
          }
        });
      }
    }
  }
}
_plugserve(window.plugserv_config);{% comment %}do not modify this file! it's versioned and included via SRI.{% endcomment %}
