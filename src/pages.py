RETRY = '<a class="btn primary" href="javascript:location.reload()">Try again</a>'
HOME = '<a class="btn primary" href="https://wikioasis.org/">Go home</a>'
STATUS = '<a class="btn" href="https://status.wikioasis.org/">Status</a>'
DISCORD = '<a class="btn" href="https://discord.gg/GrrTcsVC2x">Discord</a>'
CONTACT = '<a class="btn" href="mailto:tech@wikioasis.org">Contact us</a>'
REPORT = '<a class="btn" href="https://wikioasis.atlassian.net/jira/core/form/009f9508-56d7-43f9-bb55-25aa555b3192" target="_blank" rel="noopener">Report frequent challenges</a>'


def haproxy(code, reason, description, actions, headers=None):
    return {
        'code': code,
        'reason': reason,
        'title': reason,
        'heading': '%d: %s' % (code, reason),
        'description': description,
        'actions': actions + DISCORD + STATUS,
        'headers': headers or {},
        'body': '',
        'script': '',
    }


HAPROXY = [
    haproxy(400, 'Bad Request', 'Your browser sent a request we couldn’t understand. Reloading usually fixes it.', RETRY),
    haproxy(403, 'Forbidden', 'You don’t have permission to open this page.', HOME),
    haproxy(404, 'Not Found', 'There’s nothing at this address. It may have moved, or the link is out of date.', HOME),
    haproxy(405, 'Method Not Allowed', 'This address doesn’t accept that kind of request.', HOME),
    haproxy(408, 'Request Timeout', 'We didn’t receive your request in time. Check your connection and try again.', RETRY),
    haproxy(410, 'Gone', 'What you’re looking for has been removed.', HOME),
    haproxy(413, 'Payload Too Large', 'The request was larger than we accept. Try again with less data.', HOME),
    haproxy(425, 'Too Early', 'The request arrived before the connection was ready. Try again in a moment.', RETRY),
    haproxy(429, 'Too Many Requests', 'You’ve sent a lot of requests recently. Wait a little while, then try again.', RETRY, {'Retry-After': '30'}),
    haproxy(500, 'Internal Server Error', 'Something went wrong on our end. Please try again in a few moments.', RETRY),
    haproxy(501, 'Not Implemented', 'The server doesn’t support what your request asked for.', HOME),
    haproxy(502, 'Bad Gateway', 'One of our servers returned an error. Please try again in a few moments.', RETRY),
    haproxy(503, 'Service Unavailable', 'There are no servers ready to handle your request. Try again in a few moments.', RETRY, {'Retry-After': '30'}),
    haproxy(504, 'Gateway Timeout', 'Our servers didn’t answer in time. Please try again in a few moments.', RETRY),
]


def cloudflare(path, code, reason, description, actions, body, script=''):
    return {
        'path': path,
        'code': code,
        'title': reason,
        'heading': reason if code == 'Checkpoint' else '%s: %s' % (code, reason),
        'description': description,
        'actions': actions,
        'body': body,
        'script': script,
    }


def box(content):
    return '  <div class="cf-error-wrap">\n    <div class="cf-error-box">%s</div>\n  </div>' % content


CHALLENGE_BODY = """  <p class="ray-id">Ray ID: ::RAY_ID::</p>
  <div class="cf-error-wrap">
    <div class="challenge-spinner-row" id="challenge-spinner-row">
      <div class="challenge-spinner"></div>
      <span>Loading security check…</span>
    </div>
    <div class="cf-error-box" id="challenge-box">::CAPTCHA_BOX::</div>
  </div>"""

CHALLENGE_SCRIPT = """<script>
(function () {
  var box = document.getElementById('challenge-box');
  var row = document.getElementById('challenge-spinner-row');
  function reveal() {
    box.classList.add('visible');
    row.classList.add('hidden');
    setTimeout(function () { row.remove(); }, 300);
  }
  var observer = new MutationObserver(function () {
    if (box.querySelector('iframe')) {
      reveal();
      observer.disconnect();
    }
  });
  observer.observe(box, { childList: true, subtree: true });
  setTimeout(function () {
    if (box.classList.contains('visible')) return;
    reveal();
    observer.disconnect();
  }, 4000);
})();
</script>"""

CLOUDFLARE = [
    cloudflare('cf/500.html', '5xx', 'Server Error',
               'Something went wrong on our end. Please try again in a few moments.',
               DISCORD + STATUS, box('::CLOUDFLARE_ERROR_500S_BOX::')),
    cloudflare('cf/1000.html', '10xx', 'Configuration Error',
               'Something isn’t set right, we’re working to fix it.',
               DISCORD + STATUS, box('::CLOUDFLARE_ERROR_1000S_BOX::')),
    cloudflare('cf/block.html', '403', 'Blocked',
               'Your connection seemed suspicious, your connection has been blocked.',
               DISCORD + CONTACT, box('Ray ID: ::RAY_ID::')),
    cloudflare('cf/challenge.html', 'Checkpoint', 'Security Checkpoint',
               'Just double checking that you are a human, please wait.',
               DISCORD + STATUS + REPORT, CHALLENGE_BODY, CHALLENGE_SCRIPT),
]
