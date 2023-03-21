# scrubbing sensitive information
import hashlib
import os
import re
import six


try:
    from collective.sentry import error_handler
except ImportError:
    error_handler = None


SCRUBBING_SENTRY_DATA = (
    os.environ.get("SCRUBBING_SENTRY_DATA", "false").lower() == "true"
)


def hashdata(w):
    return hashlib.md5(w.encode(errors="ignore")).hexdigest()[:9]


def scrub_cookies(cookies):
    for cookie_name in cookies:
        if cookie_name in ("__ac", "auth_token"):
            cookies[cookie_name] = hashdata(cookies[cookie_name])
    return cookies


def scrub_headers(headers):
    for header_name in headers:
        if header_name in ("REMOTE_ADDR", "REMOTE_HOST"):
            headers[header_name] = hashdata(headers[header_name])
    return headers


def scrub_user(user):
    for attr in user:
        if isinstance(user[attr], (six.string_types, six.text_type)):
            user[attr] = hashdata(user[attr])
    return user


def scrub_breadcrumb(breadcrumb):
    if breadcrumb.get("message"):
        breadcrumb["message"] = re.sub(
            r"^(\d+\.\d+\.\d+\.\d+) - ([^ ]+)",
            lambda m: "{} - {}".format(hashdata(m.group(1)), hashdata(m.group(2))),
            breadcrumb["message"],
        )
    return breadcrumb


def scrub_breadcrumbs(values):
    return [scrub_breadcrumb(item) for item in values]


def apply():
    if SCRUBBING_SENTRY_DATA and error_handler:

        def scrubbing(fun):
            def wrapper(event, hint):
                data = fun(event, hint)
                if (data.get("extra") or {}).get("cookies"):
                    data["extra"]["cookies"] = scrub_cookies(data["extra"]["cookies"])
                if ((data.get("extra") or {}).get("request") or {}).get("headers"):
                    data["extra"]["request"]["headers"] = scrub_headers(
                        data["extra"]["request"]["headers"]
                    )
                if data.get("user"):
                    data["user"] = scrub_user(data["user"])
                if (data.get("breadcrumbs") or {}).get("values"):
                    data["breadcrumbs"]["values"] = scrub_breadcrumbs(
                        data["breadcrumbs"]["values"]
                    )
                return data

            return wrapper

        error_handler._before_send = scrubbing(error_handler._before_send)
