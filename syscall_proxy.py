import pathlib, os
from logger_db import log

BASE = pathlib.Path(__file__).parent / "sandbox"
BASE = BASE.resolve()

def _safe_path(rel):
    p = (BASE / rel).resolve()
    if not str(p).startswith(str(BASE)):
        raise PermissionError("outside sandbox")
    return p

def read_file(user, relpath):
    action = "read_file"
    try:
        p = _safe_path(relpath)
        if not p.exists() or not p.is_file():
            log(user, action, {"path":relpath}, "not_found"); return {"ok":False, "error":"not_found"}, 404
        if p.stat().st_size > 200_000:
            log(user, action, {"path":relpath}, "too_large"); return {"ok":False, "error":"too_large"}, 413
        content = p.read_text(errors='replace')
        log(user, action, {"path":relpath}, "success")
        return {"ok":True, "content":content}, 200
    except PermissionError:
        log(user, action, {"path":relpath}, "permission_denied")
        return {"ok":False, "error":"permission_denied"}, 403
    except Exception as e:
        log(user, action, {"path":relpath,"err":str(e)}, "error")
        return {"ok":False, "error":"error"}, 500

def list_dir(user, relpath):
    action = "list_dir"
    try:
        p = _safe_path(relpath or ".")
        if not p.exists() or not p.is_dir():
            log(user, action, {"path":relpath}, "not_found"); return {"ok":False, "error":"not_found"}, 404
        items = []
        for x in p.iterdir():
            items.append({"name": x.name, "is_dir": x.is_dir(), "size": x.stat().st_size})
        log(user, action, {"path":relpath}, "success")
        return {"ok":True, "items": items}, 200
    except PermissionError:
        log(user, action, {"path":relpath}, "permission_denied")
        return {"ok":False, "error":"permission_denied"}, 403
    except Exception as e:
        log(user, action, {"path":relpath,"err":str(e)}, "error")
        return {"ok":False, "error":"error"}, 500

def get_loadavg(user, params):
    action = "get_loadavg"
    try:
        load = os.getloadavg()
        log(user, action, {}, "success")
        return {"ok":True, "load": load}, 200
    except Exception as e:
        log(user, action, {"err":str(e)}, "error")
        return {"ok":False, "error":"error"}, 500

def delete_file(user, relpath):
    action = "delete_file"
    try:
        p = _safe_path(relpath)
        if not p.exists():
            log(user, action, {"path":relpath}, "not_found"); return {"ok":False, "error":"not_found"}, 404
        if p.is_dir():
            log(user, action, {"path":relpath}, "is_dir"); return {"ok":False, "error":"is_dir"}, 400
        p.unlink()
        log(user, action, {"path":relpath}, "deleted")
        return {"ok":True, "deleted": relpath}, 200
    except PermissionError:
        log(user, action, {"path":relpath}, "permission_denied")
        return {"ok":False, "error":"permission_denied"}, 403
    except Exception as e:
        log(user, action, {"path":relpath,"err":str(e)}, "error")
        return {"ok":False, "error":"error"}, 500
