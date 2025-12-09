from flask import Flask, request, jsonify, send_from_directory
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
import auth, syscall_proxy, logger_db, os

# Flask app: static_folder points to frontend/static so /static/... works
app = Flask(__name__, static_folder="../frontend/static", template_folder="../frontend")
app.secret_key = "replace_with_a_real_secret"   # demo only - change for production

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id): self.id = id

@login_manager.user_loader
def load_user(uid):
    if uid in auth.USERS: return User(uid)
    return None

# Serve login page
@app.route("/")
def index():
    return send_from_directory("../frontend", "login.html")

# Explicit route for dashboard so /dashboard.html works
@app.route("/dashboard.html")
@login_required
def dashboard():
    return send_from_directory("../frontend", "dashboard.html")

# Static files are served automatically at /static/* thanks to static_folder.
# (If you want a favicon, add it to frontend/static and it will be reachable at /static/favicon.ico)

# Login API
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.json or {}
    u = data.get("username"); p = data.get("password")
    if not u or not p:
        return jsonify({"ok":False,"error":"missing"}), 400
    if auth.verify(u,p):
        user = User(u); login_user(user)
        return jsonify({"ok":True,"role":auth.role_of(u)})
    return jsonify({"ok":False,"error":"bad_credentials"}), 401

# Logout API
@app.route("/api/logout", methods=["POST"])
@login_required
def api_logout():
    logout_user()
    return jsonify({"ok":True})

# List available actions for UI (frontend uses to show allowed options)
@app.route("/api/actions", methods=["GET"])
@login_required
def api_actions():
    role = auth.role_of(current_user.id)
    # define which actions exist and which roles can call them
    ACTIONS = {
        "read_file": {"label":"Read file (sandbox)", "roles":["admin","user","auditor"]},
        "list_dir":  {"label":"List directory (sandbox)", "roles":["admin","user","auditor"]},
        "get_loadavg":{"label":"Get system load (admin/auditor)", "roles":["admin","auditor"]},
        "delete_file":{"label":"Delete file (admin only)", "roles":["admin"]}
    }
    # mark allowed for this user
    available = {k:{**v,"allowed": role in v["roles"]} for k,v in ACTIONS.items()}
    return jsonify({"ok":True,"actions":available})

# Dispatcher with RBAC checks
@app.route("/api/dispatch", methods=["POST"])
@login_required
def api_dispatch():
    data = request.json or {}
    action = data.get("action")
    params = data.get("params", {})
    ip = request.remote_addr or "unknown"
    user = current_user.id
    role = auth.role_of(user)

    # Simple RBAC policy - duplicate definition with allowed roles
    role_rules = {
        "read_file": ["admin","user","auditor"],
        "list_dir": ["admin","user","auditor"],
        "get_loadavg": ["admin","auditor"],
        "delete_file": ["admin"]
    }
    if action not in role_rules:
        return jsonify({"ok":False,"error":"not_allowed"}), 403
    if role not in role_rules[action]:
        # Log the unauthorized attempt
        logger_db.log(user, action, params, "unauthorized")
        return jsonify({"ok":False,"error":"unauthorized"}), 403

    # Call proxy functions
    if action == "read_file":
        res, status = syscall_proxy.read_file(user, params.get("path",""))
        return jsonify(res), status

    if action == "list_dir":
        res, status = syscall_proxy.list_dir(user, params.get("path",""))
        return jsonify(res), status

    if action == "get_loadavg":
        res, status = syscall_proxy.get_loadavg(user, params)
        return jsonify(res), status

    if action == "delete_file":
        # implement delete safely (only in sandbox)
        try:
            res, status = syscall_proxy.delete_file(user, params.get("path",""))
            return jsonify(res), status
        except Exception as e:
            logger_db.log(user, action, {"path":params.get("path",""), "err":str(e)}, "error")
            return jsonify({"ok":False,"error":"error"}), 500

    return jsonify({"ok":False,"error":"unknown"}), 400

# Logs endpoint (only admin/auditor)
@app.route("/api/logs", methods=["GET"])
@login_required
def api_logs():
    if auth.role_of(current_user.id) not in ("admin","auditor"):
        return jsonify({"ok":False,"error":"unauthorized"}), 403
    rows = logger_db.fetch_logs(500)
    items = []
    for id,ts,user,action,params,outcome in rows:
        items.append({"id":id,"ts":ts,"user":user,"action":action,"params":params,"outcome":outcome})
    return jsonify({"ok":True,"logs":items})

if __name__ == "__main__":
    # ensure sandbox exists
    os.makedirs("sandbox", exist_ok=True)
    # Run dev server
    app.run(host="0.0.0.0", port=5000, debug=True)
