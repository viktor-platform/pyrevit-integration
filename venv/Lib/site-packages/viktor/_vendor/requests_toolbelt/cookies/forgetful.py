"""The module containing the code for ForgetfulCookieJar."""
from viktor._vendor.requests.cookies import RequestsCookieJar


class ForgetfulCookieJar(RequestsCookieJar):
    def set_cookie(self, *args, **kwargs):
        return
