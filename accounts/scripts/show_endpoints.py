from django.urls import get_resolver

def run():
    resolver = get_resolver()

    def walk(patterns, prefix=""):
        for p in patterns:
            pattern_str = prefix + str(p.pattern)

            # include() -> recorrer internamente
            if hasattr(p, "url_patterns"):
                walk(p.url_patterns, pattern_str)
                continue

            # callback
            callback = getattr(p, "callback", None)
            if not callback:
                print(f"{pattern_str}   ->  UNKNOWN")
                continue

            # método / viewclass
            view = getattr(callback, "view_class", None)

            if view and hasattr(view, "http_method_names"):
                allowed = [m.upper() for m in view.http_method_names if m != "options"]
            else:
                allowed = []

            view_name = f"{callback.__module__}.{callback.__name__}"

            print(f"{pattern_str:<50} --> {', '.join(allowed) or 'UNKNOWN'}  ({view_name})")

    walk(resolver.url_patterns)
