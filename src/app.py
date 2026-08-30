from flask import Flask, jsonify, send_from_directory
import os
# from api.routes import register_routes
from api.swagger import spec
from api.controllers.todo_controller import bp as todo_bp
from api.controllers.auth_controller import auth_bp as auth_bp
from api.controllers.room_controller import bp as room_bp
from api.controllers.space_image_controller import bp as space_image_bp
from api.controllers.space_schedule_controller import bp as space_schedule_bp
from api.controllers.space_controller import bp as space_bp
from api.controllers.reservation_controller import bp as reservation_bp
from api.controllers.billing_controller import bp as billing_bp
from api.controllers.equipment_controller import bp as equipment_bp
from api.controllers.package_booking_controller import bp as package_booking_bp
from api.controllers.chatbot_controller import bp as chatbot_bp
from api.controllers.recommendation_controller import bp as recommendation_bp
from api.middleware import middleware
from api.responses import success_response
from infrastructure.databases import init_db
from config import Config
from flasgger import Swagger
from config import SwaggerConfig
from flask_swagger_ui import get_swaggerui_blueprint


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Swagger(app)
    # Đăng ký blueprint trước
    app.register_blueprint(todo_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(room_bp)
    app.register_blueprint(space_image_bp)
    app.register_blueprint(space_schedule_bp)
    app.register_blueprint(space_bp)
    app.register_blueprint(reservation_bp)
    app.register_blueprint(billing_bp)
    app.register_blueprint(equipment_bp)
    app.register_blueprint(package_booking_bp)
    app.register_blueprint(chatbot_bp)
    app.register_blueprint(recommendation_bp)
    # register_routes(app)
     # Thêm Swagger UI blueprint
    SWAGGER_URL = '/docs'
    API_URL = '/swagger.json'
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL,
        API_URL,
        config={'app_name': "Todo API"}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

    try:
        init_db(app)
    except Exception as e:
        print(f"Error initializing database: {e}")

    # Register middleware
    middleware(app)

    # Register routes
    with app.test_request_context():
        for rule in app.url_map.iter_rules():
            # Thêm các endpoint khác nếu cần
            if rule.endpoint.startswith(('todo.', 'course.', 'user.', 'auth.', 'room.', 'space.', 'space_image.', 'space_schedule.', 'reservation.', 'billing.', 'equipment.', 'package_booking.', 'chatbot.', 'recommendation.')):
                view_func = app.view_functions[rule.endpoint]
                print(f"Adding path: {rule.rule} -> {view_func}")
                spec.path(view=view_func)
            
    @app.route("/")
    def index():
        from flask import Response
        html = '''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8"><title>Photo Studio - Test GUI</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Arial,sans-serif;background:#1a1a2e;color:#eee;min-height:100vh}
.topbar{background:#16213e;padding:15px 30px;display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #0f3460}
.topbar h1{font-size:22px;color:#e94560}
.topbar a{color:#aaa;text-decoration:none;margin-left:15px;font-size:14px}
.topbar a:hover{color:#e94560}
.container{max-width:1200px;margin:0 auto;padding:20px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(350px,1fr));gap:20px;margin-top:20px}
.card{background:#16213e;border-radius:10px;padding:20px;border:1px solid #0f3460;transition:0.3s}
.card:hover{border-color:#e94560;transform:translateY(-2px)}
.card h2{color:#e94560;font-size:16px;margin-bottom:10px;display:flex;align-items:center;gap:8px}
.card p{color:#888;font-size:13px;margin-bottom:12px}
.card .links a{display:inline-block;padding:6px 12px;margin:3px;border-radius:5px;font-size:12px;text-decoration:none;font-weight:bold}
.link-get{background:#0f3460;color:#53a8b6}
.link-post{background:#1a472a;color:#4caf50}
.link-del{background:#4a1a1a;color:#f44336}
.link-doc{background:#2a1a4a;color:#bb86fc}
.link-get:hover{background:#1a4a6a}
.link-post:hover{background:#2a6a3a}
.link-del:hover{background:#6a2a2a}
.msg{padding:10px;margin-bottom:15px;border-radius:6px;display:none;font-size:14px}
.msg-ok{background:#1a472a;color:#4caf50;border:1px solid #4caf50}
.msg-err{background:#4a1a1a;color:#f44336;border:1px solid #f44336}
.section{margin-top:30px}
.section h2{color:#eee;font-size:18px;margin-bottom:15px;padding-bottom:8px;border-bottom:1px solid #0f3460}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:8px;text-align:left;border-bottom:1px solid #0f3460}
th{color:#e94560;background:#0f3460}
.form-row{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:8px}
.form-row input,.form-row select{padding:6px;border:1px solid #0f3460;border-radius:4px;background:#1a1a2e;color:#eee;font-size:13px;flex:1;min-width:100px}
.btn{padding:6px 14px;border:none;border-radius:4px;cursor:pointer;font-size:13px;font-weight:bold}
.btn-green{background:#4caf50;color:#fff}.btn-red{background:#f44336;color:#fff}.btn-blue{background:#2196f3;color:#fff}
.output{background:#0d1117;border:1px solid #0f3460;border-radius:6px;padding:10px;margin-top:10px;font-family:monospace;font-size:12px;color:#53a8b6;max-height:200px;overflow:auto;white-space:pre-wrap;display:none}
</style>
</head>
<body>
<div class="topbar">
<h1>Photo Studio Management</h1>
<span style="background:#e94560;color:#fff;padding:4px 10px;border-radius:4px;font-size:12px">TEST GUI</span>
<div>
<a href="/docs">Swagger UI</a>
<a href="/swagger.json">API JSON</a>
<a href="/rooms/">API: /rooms/</a>
</div>
</div>
<div class="container">
<div id="msg" class="msg"></div>

<h2 style="color:#e94560;margin-top:10px">Tong Quan</h2>
<div class="grid">

<div class="card">
<h2>Auth</h2>
<p>Dang nhap / Dang ky tai khoan</p>
<a class="links link-post" href="#" onclick="apiTest('POST','/auth/login',{username:'admin',password:'admin123'})">POST /auth/login</a>
<a class="links link-get" href="#" onclick="apiTest('GET','/auth/check_router')">GET /auth/check_router</a>
</div>

<div class="card">
<h2>Rooms</h2>
<p>Quan ly phong chup / phong lam viec</p>
<a class="links link-get" href="#" onclick="apiTest('GET','/rooms/')">GET /rooms/</a>
<a class="links link-post" href="#" onclick="apiTest('POST','/rooms/',{name:'Test Room',room_type:'studio',capacity:10,price_per_hour:150000,status:'available'})">POST /rooms/</a>
</div>

<div class="card">
<h2>Spaces</h2>
<p>Quan ly khong gian chup anh</p>
<a class="links link-get" href="#" onclick="apiTest('GET','/spaces/')">GET /spaces/</a>
<a class="links link-get" href="#" onclick="apiTest('GET','/spaces/search?q=studio')">GET /spaces/search</a>
</div>

<div class="card">
<h2>Reservations</h2>
<p>Quan ly dat phong - duyet - checkin/checkout</p>
<a class="links link-get" href="#" onclick="apiTest('GET','/v1/reservations/')">GET /v1/reservations/</a>
<a class="links link-post" href="#" onclick="apiTest('POST','/v1/reservations/',{user_id:2,provider_id:2,space_id:4,start_time:'2026-11-01T09:00:00',end_time:'2026-11-01T11:00:00',total_price:600000})">POST /v1/reservations/</a>
</div>

<div class="card">
<h2>Equipment</h2>
<p>Thiet bi chup anh - enlarger, scanner, lighting...</p>
<a class="links link-get" href="#" onclick="apiTest('GET','/api/v1/equipment')">GET /api/v1/equipment</a>
<a class="links link-post" href="#" onclick="apiTest('POST','/api/v1/equipment',{provider_id:2,name:'Canon EOS R5',equipment_type:'camera',condition:'excellent',price_per_hour:100000})">POST /api/v1/equipment</a>
</div>

<div class="card">
<h2>Package Bookings</h2>
<p>Dat goi dich vu - kiem tra tai nguyen</p>
<a class="links link-get" href="#" onclick="apiTest('GET','/api/v1/package-bookings')">GET /api/v1/package-bookings</a>
</div>

<div class="card">
<h2>Billing</h2>
<p>Hoa don, san pham, khach hang, thanh toan</p>
<a class="links link-get" href="#" onclick="apiTest('GET','/v1/billing/products')">GET /products</a>
<a class="links link-get" href="#" onclick="apiTest('GET','/v1/billing/customers')">GET /customers</a>
<a class="links link-get" href="#" onclick="apiTest('GET','/v1/billing/invoices')">GET /invoices</a>
</div>

<div class="card">
<h2>Chatbot AI</h2>
<p>Chatbot tro ly - hoi dap ve dich vu studio</p>
<a class="links link-post" href="#" onclick="apiTest('POST','/api/v1/chatbot/ask',{message:'Phim 35mm la gi?'})">POST /api/v1/chatbot/ask</a>
<a class="links link-get" href="#" onclick="apiTest('GET','/api/v1/chatbot/health')">GET /health</a>
</div>

<div class="card">
<h2>Recommendations</h2>
<p>Goi y khong gian theo lich su dat</p>
<a class="links link-get" href="#" onclick="apiTest('GET','/api/v1/recommendations/2')">GET /recommendations/2</a>
</div>

</div>

<div class="section">
<h2>Test API</h2>
<div class="form-row">
<select id="method"><option>GET</option><option>POST</option><option>PUT</option><option>DELETE</option></select>
<input id="api-path" placeholder="/rooms/" value="/rooms/">
<button class="btn btn-blue" onclick="runApi()">Go</button>
<button class="btn btn-red" onclick="document.getElementById('output').style.display='none'">Clear</button>
</div>
<div id="output" class="output"></div>
</div>

<div class="section">
<h2>Quan Ly Room</h2>
<div class="form-row">
<input id="r-name" placeholder="Ten room">
<select id="r-type"><option value="standard">Standard</option><option value="vip">VIP</option><option value="studio">Studio</option><option value="conference">Conference</option></select>
<input id="r-cap" type="number" value="10" min="1" placeholder="Suc chua">
<input id="r-price" type="number" value="150000" min="0" placeholder="Gia/gio">
<select id="r-status"><option value="available">Available</option><option value="booked">Booked</option><option value="maintenance">Maintenance</option></select>
<button class="btn btn-green" onclick="createRoom()">Tao</button>
</div>
<table><thead><tr><th>ID</th><th>Ten</th><th>Loai</th><th>Chua</th><th>Gia/gio</th><th>TT</th><th></th></tr></thead><tbody id="rl"></tbody></table>
</div>

</div>
<script>
const API='http://127.0.0.1:9999';
function showMsg(t,ok){const m=document.getElementById('msg');m.className='msg '+(ok?'msg-ok':'msg-err');m.textContent=t;m.style.display='block';setTimeout(()=>m.style.display='none',4000)}
async function apiTest(method,path,body){
const out=document.getElementById('output');out.style.display='block';out.textContent='Loading '+method+' '+path+'...';
try{const opt={method,headers:{'Content-Type':'application/json'}};
if(body&&method!=='GET')opt.body=JSON.stringify(body);
const r=await fetch(API+path,opt);const t=await r.text();
out.textContent=method+' '+path+'\\nStatus: '+r.status+'\\n\\n'+JSON.stringify(JSON.parse(t||'{}'),null,2)}catch(e){out.textContent='Error: '+e.message}}
async function runApi(){const m=document.getElementById('method').value;const p=document.getElementById('api-path').value;apiTest(m,p)}
async function loadRooms(){try{const r=await fetch(API+'/rooms/');const d=await r.json();const tb=document.getElementById('rl');tb.innerHTML='';d.forEach(r=>{const tr=document.createElement('tr');tr.innerHTML='<td>'+r.id+'</td><td>'+r.name+'</td><td>'+r.room_type+'</td><td>'+r.capacity+'</td><td>'+Number(r.price_per_hour).toLocaleString()+'</td><td>'+r.status+'</td><td><button class="btn btn-red" onclick="delRoom('+r.id+',\\''+r.name+'\\')">Xoa</button></td>';tb.appendChild(tr)});if(!d.length)tb.innerHTML='<tr><td colspan="7" style="text-align:center;color:#666">Khong co room</td></tr>'}catch(e){}}
async function createRoom(){const d={name:document.getElementById('r-name').value,room_type:document.getElementById('r-type').value,capacity:parseInt(document.getElementById('r-cap').value),price_per_hour:parseFloat(document.getElementById('r-price').value),status:document.getElementById('r-status').value};if(!d.name){showMsg('Nhap ten!',false);return}try{const r=await fetch(API+'/rooms/',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});const j=await r.json();if(r.ok){showMsg('Tao thanh cong: '+j.name,true);document.getElementById('r-name').value='';loadRooms()}else showMsg(j.message||'Loi',false)}catch(e){showMsg(e.message,false)}}
async function delRoom(id,name){if(!confirm('Xoa "'+name+'"?'))return;try{const r=await fetch(API+'/rooms/'+id,{method:'DELETE'});if(r.ok){showMsg('Da xoa',true);loadRooms()}else showMsg('Khong xoa duoc',false)}catch(e){showMsg(e.message,false)}}
loadRooms();
</script></body></html>'''
        return Response(html, mimetype='text/html')

    @app.route("/swagger.json")
    def swagger_json():
        return jsonify(spec.to_dict())

    upload_folder = Config.UPLOAD_FOLDER
    os.makedirs(upload_folder, exist_ok=True)

    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        return send_from_directory(upload_folder, filename)

    return app
# Run the application

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=9999, debug=True)