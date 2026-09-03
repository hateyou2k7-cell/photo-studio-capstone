from flask import Flask, jsonify, send_from_directory
import os
# from api.routes import register_routes
from api.swagger import spec
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
from api.controllers.course_controller import bp as course_bp
from api.controllers.provider_controller import bp as provider_bp
from api.controllers.community_controller import bp as community_bp
from api.middleware import middleware
from api.responses import success_response
from database.databases import init_db
from config import Config
from flasgger import Swagger
from config import SwaggerConfig
from flask_swagger_ui import get_swaggerui_blueprint


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    Swagger(app)
    # Đăng ký blueprint trước
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
    app.register_blueprint(course_bp)
    app.register_blueprint(provider_bp)
    app.register_blueprint(community_bp)
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
            if rule.endpoint.startswith(('course.', 'user.', 'auth.', 'room.', 'space.', 'space_image.', 'space_schedule.', 'reservation.', 'billing.', 'equipment.', 'package_booking.', 'chatbot.', 'recommendation.', 'community.')):
                view_func = app.view_functions[rule.endpoint]
                print(f"Adding path: {rule.rule} -> {view_func}")
                spec.path(view=view_func)
            
    @app.route("/")
    def index():
        from flask import Response
        html = r'''<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8"><title>Photo Studio - Test GUI</title>
<style>
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:Arial,sans-serif;background:#1a1a2e;color:#eee;min-height:100vh}
.topbar{background:#16213e;padding:15px 30px;display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #0f3460}
.topbar h1{font-size:20px;color:#e94560}
.topbar a{color:#aaa;text-decoration:none;margin-left:15px;font-size:13px}
.topbar a:hover{color:#e94560}
.container{max-width:1200px;margin:0 auto;padding:20px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(340px,1fr));gap:16px;margin-top:16px}
.card{background:#16213e;border-radius:10px;padding:16px;border:1px solid #0f3460;transition:0.3s}
.card:hover{border-color:#e94560}
.card h2{color:#e94560;font-size:15px;margin-bottom:8px}
.card p{color:#888;font-size:12px;margin-bottom:10px}
.btn{padding:5px 12px;border:none;border-radius:4px;cursor:pointer;font-size:12px;font-weight:bold;margin:2px}
.btn-green{background:#4caf50;color:#fff}
.btn-red{background:#f44336;color:#fff}
.btn-blue{background:#2196f3;color:#fff}
.btn-orange{background:#ff9800;color:#fff}
.btn:hover{opacity:0.85}
.msg{padding:10px;margin-bottom:15px;border-radius:6px;display:none;font-size:13px}
.msg-ok{background:#1a472a;color:#4caf50;border:1px solid #4caf50}
.msg-err{background:#4a1a1a;color:#f44336;border:1px solid #f44336}
.toast{position:fixed;top:20px;right:20px;padding:12px 20px;border-radius:8px;font-size:14px;font-weight:bold;z-index:9999;display:none;max-width:400px;box-shadow:0 4px 12px rgba(0,0,0,0.4);animation:slideIn 0.3s ease}
.toast-ok{background:#1a472a;color:#4caf50;border:2px solid #4caf50}
.toast-err{background:#4a1a1a;color:#f44336;border:2px solid #f44336}
.toast-info{background:#0d47a1;color:#64b5f6;border:2px solid #2196f3}
@keyframes slideIn{from{transform:translateX(100px);opacity:0}to{transform:translateX(0);opacity:1}}
.section{margin-top:24px}
.section h2{color:#e94560;font-size:16px;margin-bottom:12px;padding-bottom:6px;border-bottom:1px solid #0f3460}
table{width:100%;border-collapse:collapse;font-size:12px}
th,td{padding:6px 8px;text-align:left;border-bottom:1px solid #0f3460}
th{color:#e94560;background:#0f3460}
.form-row{display:flex;gap:6px;flex-wrap:wrap;margin-bottom:6px}
.form-row input,.form-row select{padding:5px;border:1px solid #0f3460;border-radius:4px;background:#1a1a2e;color:#eee;font-size:12px;flex:1;min-width:80px}
.output{background:#0d1117;border:1px solid #0f3460;border-radius:6px;padding:10px;margin-top:8px;font-family:monospace;font-size:11px;color:#53a8b6;max-height:300px;overflow:auto;white-space:pre-wrap;display:none}
#auth-bar{display:flex;align-items:center;gap:10px}
#auth-bar span{color:#4caf50;font-size:13px}
.hidden{display:none}
input,select,textarea{font-size:12px !important}
</style>
</head>
<body>
<div id="toast" class="toast"></div>
<div class="topbar">
<h1>Photo Studio Management</h1>
<div id="auth-bar">
<span id="auth-status" style="color:#f44336">Chua dang nhap</span>
<button class="btn btn-red" id="btn-logout" onclick="doLogout()" style="display:none">Logout</button>
<a href="/docs">Swagger</a>
<a href="/swagger.json">JSON</a>
</div>
</div>
<div class="container">
<div id="msg" class="msg"></div>

<!-- AUTH SECTION -->
<div class="section">
<h2>1. Dang ky / Dang nhap</h2>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:16px">
<div class="card">
<h2>Dang ky</h2>
<div class="form-row"><input id="su-user" placeholder="Username"></div>
<div class="form-row"><input id="su-email" placeholder="Email" type="email"></div>
<div class="form-row"><input id="su-pass" placeholder="Password" type="password"></div>
<div class="form-row"><input id="su-pass2" placeholder="Xac nhan password" type="password"></div>
<div class="form-row"><select id="su-role"><option value="user">User</option><option value="photographer">Photographer</option><option value="provider">Provider</option><option value="expert">Expert</option></select></div>
<button class="btn btn-green" onclick="doSignup()">Dang ky</button>
</div>
<div class="card">
<h2>Dang nhap</h2>
<div class="form-row"><input id="li-user" placeholder="Username"></div>
<div class="form-row"><input id="li-pass" placeholder="Password" type="password"></div>
<button class="btn btn-blue" onclick="doLogin()">Dang nhap</button>
<div id="user-info" style="margin-top:8px;font-size:12px;color:#888"></div>
</div>
</div>
</div>

<!-- ROOMS -->
<div class="section">
<h2>2. Rooms</h2>
<div class="form-row">
<input id="r-name" placeholder="Ten room">
<select id="r-type"><option value="standard">Standard</option><option value="vip">VIP</option><option value="studio">Studio</option><option value="conference">Conference</option></select>
<input id="r-cap" type="number" value="10" min="1">
<input id="r-price" type="number" value="150000" min="0">
<button class="btn btn-green" onclick="createRoom()">Tao</button>
<button class="btn btn-blue" onclick="loadRooms()">Load</button>
</div>
<table><thead><tr><th>ID</th><th>Ten</th><th>Loai</th><th>Chua</th><th>Gia/gio</th><th>TT</th><th></th></tr></thead><tbody id="rl"></tbody></table>
</div>

<!-- SPACES -->
<div class="section">
<h2>3. Spaces</h2>
<div class="form-row">
<input id="sp-name" placeholder="Ten space">
<select id="sp-type"><option value="studio">Studio</option><option value="darkroom">Darkroom</option><option value="outdoor">Outdoor</option></select>
<input id="sp-price" type="number" value="150000" min="0">
<input id="sp-cap" type="number" value="5" min="1">
<button class="btn btn-green" onclick="createSpace()">Tao</button>
<button class="btn btn-blue" onclick="loadSpaces()">Load</button>
<button class="btn btn-orange" onclick="searchSpaces()">Search</button>
</div>
<table><thead><tr><th>ID</th><th>Ten</th><th>Loai</th><th>Gia/gio</th><th>Chua</th><th>TT</th><th></th></tr></thead><tbody id="spl"></tbody></table>
</div>

<!-- EQUIPMENT -->
<div class="section">
<h2>4. Equipment</h2>
<div class="form-row">
<input id="eq-name" placeholder="Ten thiet bi">
<select id="eq-type"><option value="camera">Camera</option><option value="lighting">Lighting</option><option value="tripod">Tripod</option><option value="enlarger">Enlarger</option><option value="scanner">Scanner</option><option value="tank">Tank</option><option value="other">Other</option></select>
<input id="eq-price" type="number" value="100000" min="0">
<button class="btn btn-green" onclick="createEquipment()">Tao</button>
<button class="btn btn-blue" onclick="loadEquipment()">Load</button>
</div>
<table><thead><tr><th>ID</th><th>Ten</th><th>Loai</th><th>Gia/gio</th><th>TT</th><th></th></tr></thead><tbody id="eql"></tbody></table>
</div>

<!-- RESERVATIONS -->
<div class="section">
<h2>5. Reservations</h2>
<div class="form-row">
<select id="res-sid" onchange="calcPrice()"><option value="">-- Chon space --</option></select>
<input id="res-start" type="datetime-local" value="2026-09-04T09:00" onchange="calcPrice()">
<input id="res-end" type="datetime-local" value="2026-09-04T12:00" onchange="calcPrice()">
<span id="res-price-display" style="color:#4caf50;font-weight:bold;font-size:14px">0</span>
<button class="btn btn-green" onclick="createReservation()">Dat cho</button>
<button class="btn btn-blue" onclick="loadReservations()">Load</button>
</div>
<table><thead><tr><th>ID</th><th>Space</th><th>Start</th><th>End</th><th>Gia</th><th>Status</th><th>Thao tac</th></tr></thead><tbody id="resl"></tbody></table>
</div>

<!-- BILLING -->
<div class="section">
<h2>6. Billing (can JWT token)</h2>
<div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px">
<div class="card">
<h2>Khach hang</h2>
<div class="form-row"><input id="c-name" placeholder="Ten KH"></div>
<div class="form-row"><input id="c-email" placeholder="Email"></div>
<div class="form-row"><input id="c-phone" placeholder="Phone"></div>
<button class="btn btn-green" onclick="createCustomer()">Tao</button>
<button class="btn btn-blue" onclick="loadCustomers()">Load</button>
<div id="cl"></div>
</div>
<div class="card">
<h2>San pham</h2>
<div class="form-row"><input id="p-name" placeholder="Ten SP"></div>
<div class="form-row"><input id="p-code" placeholder="Ma SP"></div>
<button class="btn btn-green" onclick="createProduct()">Tao</button>
<button class="btn btn-blue" onclick="loadProducts()">Load</button>
<div id="pl"></div>
</div>
<div class="card">
<h2>Hoa don</h2>
<button class="btn btn-blue" onclick="loadInvoices()">Load</button>
<div id="il"></div>
</div>
</div>
</div>

<!-- PACKAGE BOOKINGS -->
<div class="section">
<h2>7. Package Bookings</h2>
<div class="form-row">
<input id="bk-pkg" type="number" placeholder="Package ID" value="1">
<input id="bk-sp" type="number" placeholder="Space ID" value="1">
<input id="bk-uid" type="number" placeholder="Customer ID" value="1">
<input id="bk-start" type="datetime-local" value="2026-12-28T09:00">
<input id="bk-end" type="datetime-local" value="2026-12-28T12:00">
<button class="btn btn-green" onclick="createBooking()">Tao</button>
<button class="btn btn-blue" onclick="loadBookings()">Load</button>
</div>
<table><thead><tr><th>ID</th><th>Package</th><th>Space</th><th>Customer</th><th>Start</th><th>End</th><th>Gia</th><th>Status</th><th></th></tr></thead><tbody id="bkl"></tbody></table>
</div>

<!-- COURSES -->
<div class="section">
<h2>8. Courses</h2>
<div class="form-row">
<input id="co-name" placeholder="Ten khoa hoc">
<input id="co-desc" placeholder="Mo ta">
<button class="btn btn-green" onclick="createCourse()">Tao</button>
<button class="btn btn-blue" onclick="loadCourses()">Load</button>
</div>
<table><thead><tr><th>ID</th><th>Ten</th><th>Mo ta</th><th>Status</th><th></th></tr></thead><tbody id="col"></tbody></table>
</div>

<!-- CHATBOT -->
<div class="section">
<h2>9. Chatbot AI</h2>
<div class="form-row">
<input id="chat-msg" placeholder="Nhap cau hoi ve dich vu studio..." style="flex:3">
<button class="btn btn-green" onclick="askChatbot()">Hoi</button>
<button class="btn btn-blue" onclick="chatHealth()">Health</button>
</div>
<div id="chat-out" class="output"></div>
</div>

<!-- RECOMMENDATIONS -->
<div class="section">
<h2>10. Recommendations</h2>
<div class="form-row">
<input id="rec-uid" type="number" placeholder="User ID" value="1">
<button class="btn btn-blue" onclick="getRecommendations()">Goi y</button>
</div>
<div id="rec-out" class="output"></div>
</div>

<!-- CUSTOM API TEST -->
<div class="section">
<h2>11. Custom API Test</h2>
<div class="form-row">
<select id="method"><option>GET</option><option>POST</option><option>PUT</option><option>DELETE</option><option>PATCH</option></select>
<input id="api-path" placeholder="/rooms/" value="/rooms/">
<button class="btn btn-blue" onclick="runApi()">Go</button>
<button class="btn btn-red" onclick="document.getElementById('output').style.display='none'">Clear</button>
</div>
<textarea id="api-body" rows="3" placeholder='{"key":"value"}' style="width:100%;background:#0d1117;color:#eee;border:1px solid #0f3460;border-radius:4px;padding:8px;font-family:monospace;font-size:12px;resize:vertical"></textarea>
<div id="output" class="output"></div>
</div>

</div>
<script>
const API='http://127.0.0.1:9999';
let TOKEN=null;

function showMsg(t,ok){const m=document.getElementById('msg');m.className='msg '+(ok?'msg-ok':'msg-err');m.textContent=t;m.style.display='block';setTimeout(()=>m.style.display='none',5000);toast(t,ok?'ok':'err')}
function toast(t,type){
const el=document.getElementById('toast');
el.className='toast toast-'+type;
el.textContent=(type==='ok'?'✓ ':'✗ ')+t;
el.style.display='block';
el.style.animation='none';el.offsetHeight;el.style.animation='slideIn 0.3s ease';
setTimeout(()=>{el.style.display='none'},4000)}
function authHeaders(){return TOKEN?{Authorization:'Bearer '+TOKEN}:{}}
function showOut(id,data){const el=document.getElementById(id);el.style.display='block';el.textContent=typeof data==='string'?data:JSON.stringify(data,null,2)}

// AUTH
async function doSignup(){
  const u=document.getElementById('su-user').value,e=document.getElementById('su-email').value,p=document.getElementById('su-pass').value,p2=document.getElementById('su-pass2').value,role=document.getElementById('su-role').value;
  if(!u||!e||!p){toast('Vui long nhap day du thong tin!','err');return}
  if(p!==p2){toast('Mat khau khong khop!','err');return}
  try{const r=await fetch(API+'/auth/signup',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,email:e,password:p,passwordconfirm:p2,role:role})});
  const d=await r.json();if(r.ok){toast('Dang ky thanh cong! Username: '+d.username,true);document.getElementById('su-user').value='';document.getElementById('su-email').value='';document.getElementById('su-pass').value='';document.getElementById('su-pass2').value=''}else toast(d.message||'Dang ky that bai',false)}catch(e){toast('Loi: '+e.message,false)}
}
async function doLogin(){
  const u=document.getElementById('li-user').value,p=document.getElementById('li-pass').value;
  if(!u||!p){toast('Vui long nhap username va password!','err');return}
  try{const r=await fetch(API+'/auth/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({username:u,password:p})});
  const d=await r.json();if(r.ok){TOKEN=d.token;localStorage.setItem('token',d.token);localStorage.setItem('user_id',d.user_id);localStorage.setItem('role',d.role);localStorage.setItem('provider_profile_id',d.provider_profile_id||'');
  document.getElementById('auth-status').textContent='Da dang nhap: '+u+' (ID:'+d.user_id+' | '+d.role+')';document.getElementById('auth-status').style.color='#4caf50';
  document.getElementById('btn-logout').style.display='inline-block';document.getElementById('user-info').textContent='user_id='+d.user_id+' role='+d.role;toast('Dang nhap thanh cong! Xin chao '+u+' ('+d.role+')',true);document.getElementById('li-user').value='';document.getElementById('li-pass').value=''}else toast(d.error||'Sai username hoac password',false)}catch(e){toast('Loi: '+e.message,false)}
}
function doLogout(){TOKEN=null;localStorage.removeItem('token');localStorage.removeItem('user_id');localStorage.removeItem('role');localStorage.removeItem('provider_profile_id');document.getElementById('auth-status').textContent='Chua dang nhap';document.getElementById('auth-status').style.color='#f44336';document.getElementById('btn-logout').style.display='none';document.getElementById('user-info').textContent=''}
(function(){const t=localStorage.getItem('token'),uid=localStorage.getItem('user_id'),role=localStorage.getItem('role');if(t){TOKEN=t;document.getElementById('auth-status').textContent='Da dang nhap (ID:'+uid+' | '+role+')';document.getElementById('auth-status').style.color='#4caf50';document.getElementById('btn-logout').style.display='inline-block'}})();

// GENERIC API CALL
async function apiCall(method,path,body,auth){
  const opt={method,headers:{'Content-Type':'application/json'}};
  if(auth)Object.assign(opt.headers,authHeaders());
  if(body&&method!=='GET')opt.body=JSON.stringify(body);
  const r=await fetch(API+path,opt);
  const t=await r.text();
  let d;try{d=JSON.parse(t)}catch(e){d=t}
  return{status:r.status,data:d,ok:r.ok};
}

// ROOMS
async function loadRooms(){const{data}=await apiCall('GET','/rooms/',null,true);const tb=document.getElementById('rl');tb.innerHTML='';(Array.isArray(data)?data:[]).forEach(r=>{const tr=document.createElement('tr');tr.innerHTML='<td>'+r.id+'</td><td>'+r.name+'</td><td>'+r.room_type+'</td><td>'+r.capacity+'</td><td>'+Number(r.price_per_hour).toLocaleString()+'</td><td>'+r.status+'</td><td><button class="btn btn-red" onclick="delRoom('+r.id+')">Xoa</button></td>';tb.appendChild(tr)});if(!Array.isArray(data)||!data.length)tb.innerHTML='<tr><td colspan="7" style="text-align:center;color:#666">Khong co room</td></tr>'}
async function createRoom(){const d={name:document.getElementById('r-name').value,room_type:document.getElementById('r-type').value,capacity:parseInt(document.getElementById('r-cap').value),price_per_hour:parseFloat(document.getElementById('r-price').value),status:'available'};if(!d.name){showMsg('Nhap ten!',false);return}const{ok,data}=await apiCall('POST','/rooms/',d,true);showMsg(ok?'Tao thanh cong: '+data.name:(data.message||'Loi'),ok);if(ok)loadRooms()}
async function delRoom(id){if(!confirm('Xoa room #'+id+'?'))return;const{ok}=await apiCall('DELETE','/rooms/'+id,null,true);showMsg(ok?'Da xoa':'Khong xoa duoc',ok);if(ok)loadRooms()}

// SPACES
async function loadSpaces(){const{data}=await apiCall('GET','/spaces/',null,true);const tb=document.getElementById('spl');tb.innerHTML='';const items=(data&&data.items)?data.items:(Array.isArray(data)?data:[]);items.forEach(r=>{const tr=document.createElement('tr');tr.innerHTML='<td>'+r.id+'</td><td>'+r.name+'</td><td>'+(r.space_type||r.type||'-')+'</td><td>'+Number(r.base_price_per_hour||0).toLocaleString()+'</td><td>'+r.max_capacity+'</td><td>'+(r.status?'Active':'Inactive')+'</td><td><button class="btn btn-red" onclick="delSpace('+r.id+')">Xoa</button></td>';tb.appendChild(tr)});if(!items.length)tb.innerHTML='<tr><td colspan="7" style="text-align:center;color:#666">Khong co space</td></tr>'}
async function createSpace(){const pid=parseInt(localStorage.getItem('provider_profile_id'));if(!pid){showMsg('Ban can dang nhap voi tai khoan Provider!',false);return}const d={provider_id:pid,name:document.getElementById('sp-name').value,space_type:document.getElementById('sp-type').value,base_price_per_hour:parseFloat(document.getElementById('sp-price').value),max_capacity:parseInt(document.getElementById('sp-cap').value),status:true};if(!d.name){showMsg('Nhap ten!',false);return}const{ok,data}=await apiCall('POST','/spaces/',d,true);showMsg(ok?'Tao thanh cong: '+data.name:(data.message||'Loi'),ok);if(ok)loadSpaces()}
async function delSpace(id){if(!confirm('Xoa space #'+id+'?'))return;const{ok}=await apiCall('DELETE','/spaces/'+id,null,true);showMsg(ok?'Da xoa':'Khong xoa duoc',ok);if(ok)loadSpaces()}
async function searchSpaces(){const q=document.getElementById('sp-name').value||'studio';const{data}=await apiCall('GET','/spaces/search?q='+encodeURIComponent(q),null,true);const tb=document.getElementById('spl');tb.innerHTML='';const items=(data&&data.items)?data.items:(Array.isArray(data)?data:[]);items.forEach(r=>{const tr=document.createElement('tr');tr.innerHTML='<td>'+r.id+'</td><td>'+r.name+'</td><td>'+(r.space_type||r.type||'-')+'</td><td>'+Number(r.base_price_per_hour||0).toLocaleString()+'</td><td>'+r.max_capacity+'</td><td>'+(r.status?'Active':'Inactive')+'</td><td>-</td>';tb.appendChild(tr)});if(!items.length)tb.innerHTML='<tr><td colspan="7" style="text-align:center;color:#666">Khong tim thay</td></tr>'}

// EQUIPMENT
async function loadEquipment(){const{data}=await apiCall('GET','/api/v1/equipment',null,true);const tb=document.getElementById('eql');tb.innerHTML='';const items=(data&&data.items)?data.items:(Array.isArray(data)?data:[]);items.forEach(r=>{const tr=document.createElement('tr');tr.innerHTML='<td>'+r.id+'</td><td>'+r.name+'</td><td>'+(r.type||r.equipment_type||'-')+'</td><td>'+Number(r.price_per_hour||0).toLocaleString()+'</td><td>'+(r.is_available!==false?'Yes':'No')+'</td><td><button class="btn btn-red" onclick="delEquipment('+r.id+')">Xoa</button></td>';tb.appendChild(tr)});if(!items.length)tb.innerHTML='<tr><td colspan="6" style="text-align:center;color:#666">Khong co thiet bi</td></tr>'}
async function createEquipment(){const pid=parseInt(localStorage.getItem('provider_profile_id'));if(!pid){showMsg('Ban can dang nhap voi tai khoan Provider!',false);return}const d={provider_id:pid,name:document.getElementById('eq-name').value,type:document.getElementById('eq-type').value,price_per_hour:parseFloat(document.getElementById('eq-price').value),condition:'good',is_available:true};if(!d.name){showMsg('Nhap ten!',false);return}const{ok,data}=await apiCall('POST','/api/v1/equipment',d,true);showMsg(ok?'Tao thanh cong: '+data.name:(data.message||'Loi'),ok);if(ok)loadEquipment()}
async function delEquipment(id){if(!confirm('Xoa thiet bi #'+id+'?'))return;const{ok}=await apiCall('DELETE','/api/v1/equipment/'+id,null,true);showMsg(ok?'Da xoa':'Khong xoa duoc',ok);if(ok)loadEquipment()}

// RESERVATIONS
let _spaceMap={};
async function loadSpaceOptions(){const{data}=await apiCall('GET','/spaces/',null,true);const items=(data&&data.items)?data.items:(Array.isArray(data)?data:[]);const sel=document.getElementById('res-sid');sel.innerHTML='<option value="">-- Chon space --</option>';_spaceMap={};items.forEach(s=>{_spaceMap[s.id]=s;sel.innerHTML+='<option value="'+s.id+'">'+s.name+' ('+Number(s.base_price_per_hour||0).toLocaleString()+'/h)</option>'})}
function calcPrice(){const sid=parseInt(document.getElementById('res-sid').value);const sp=_spaceMap[sid];if(!sp){document.getElementById('res-price-display').textContent='0';return}const s=new Date(document.getElementById('res-start').value);const e=new Date(document.getElementById('res-end').value);const hours=Math.max(0,(e-s)/(1000*60*60));const total=hours*sp.base_price_per_hour;document.getElementById('res-price-display').textContent=hours+'h x '+Number(sp.base_price_per_hour).toLocaleString()+'/h = '+Number(total).toLocaleString()}
async function loadReservations(){const{data}=await apiCall('GET','/v1/reservations/',null,true);const tb=document.getElementById('resl');tb.innerHTML='';const items=(data&&data.items)?data.items:(Array.isArray(data)?data:[]);items.forEach(r=>{const sp=_spaceMap[r.space_id]||{};const tr=document.createElement('tr');tr.innerHTML='<td>'+r.id+'</td><td>'+(sp.name||'Space #'+r.space_id)+'</td><td>'+(r.start_time||'').slice(0,16)+'</td><td>'+(r.end_time||'').slice(0,16)+'</td><td>'+Number(r.total_price||0).toLocaleString()+'</td><td>'+r.status+'</td><td><button class="btn btn-orange" onclick="confirmRes('+r.id+')">Confirm</button> <button class="btn btn-blue" onclick="approveRes('+r.id+')">Approve</button></td>';tb.appendChild(tr)});if(!items.length)tb.innerHTML='<tr><td colspan="7" style="text-align:center;color:#666">Khong co reservation</td></tr>'}
async function createReservation(){const uid=parseInt(localStorage.getItem('user_id'));const sid=parseInt(document.getElementById('res-sid').value);const sp=_spaceMap[sid];if(!sid||!sp){showMsg('Chon space!',false);return}const s=new Date(document.getElementById('res-start').value);const e=new Date(document.getElementById('res-end').value);const hours=Math.max(0,(e-s)/(1000*60*60));const total=hours*sp.base_price_per_hour;const d={user_id:uid,provider_id:sp.provider_id,space_id:sid,start_time:document.getElementById('res-start').value+':00',end_time:document.getElementById('res-end').value+':00',total_price:total};const{ok,data}=await apiCall('POST','/v1/reservations/',d,true);showMsg(ok?'Dat cho thanh cong #'+data.id+' - '+Number(total).toLocaleString()+'d':(data.message||'Loi'),ok);if(ok)loadReservations()}
async function confirmRes(id){const{ok,data}=await apiCall('POST','/v1/reservations/'+id+'/confirm',null,true);showMsg(ok?'Confirmed #'+id:(data.message||'Loi'),ok);loadReservations()}
async function approveRes(id){const{ok,data}=await apiCall('POST','/v1/reservations/'+id+'/approve',null,true);showMsg(ok?'Approved #'+id:(data.message||'Loi'),ok);loadReservations()}

// BILLING
async function loadCustomers(){const{data}=await apiCall('GET','/v1/billing/customers',null,true);const el=document.getElementById('cl');el.innerHTML='';(Array.isArray(data)?data:[]).forEach(c=>{el.innerHTML+='<div style="font-size:11px;padding:3px 0;border-bottom:1px solid #0f3460">#'+c.id+' '+c.customer_name+' | '+c.email+' <button class="btn btn-red" style="padding:1px 6px" onclick="delCustomer('+c.id+')">x</button></div>'})}
async function createCustomer(){const d={customer_name:document.getElementById('c-name').value,email:document.getElementById('c-email').value,phone:document.getElementById('c-phone').value};if(!d.customer_name){showMsg('Nhap ten!',false);return}const{ok}=await apiCall('POST','/v1/billing/customers',d,true);showMsg(ok?'Tao KH thanh cong':'Loi',ok);if(ok)loadCustomers()}
async function delCustomer(id){const{ok}=await apiCall('DELETE','/v1/billing/customers/'+id,null,true);if(ok)loadCustomers()}
async function loadProducts(){const{data}=await apiCall('GET','/v1/billing/products',null,true);const el=document.getElementById('pl');el.innerHTML='';(Array.isArray(data)?data:[]).forEach(p=>{el.innerHTML+='<div style="font-size:11px;padding:3px 0;border-bottom:1px solid #0f3460">#'+p.id+' '+p.product_name+' ('+p.product_code+') <button class="btn btn-red" style="padding:1px 6px" onclick="delProduct('+p.id+')">x</button></div>'})}
async function createProduct(){const d={product_name:document.getElementById('p-name').value,product_code:document.getElementById('p-code').value};if(!d.product_name){showMsg('Nhap ten!',false);return}const{ok}=await apiCall('POST','/v1/billing/products',d,true);showMsg(ok?'Tao SP thanh cong':'Loi',ok);if(ok)loadProducts()}
async function delProduct(id){const{ok}=await apiCall('DELETE','/v1/billing/products/'+id,null,true);if(ok)loadProducts()}
async function loadInvoices(){const{data}=await apiCall('GET','/v1/billing/invoices',null,true);const el=document.getElementById('il');el.innerHTML='';(Array.isArray(data)?data:[]).forEach(i=>{el.innerHTML+='<div style="font-size:11px;padding:3px 0;border-bottom:1px solid #0f3460">#'+i.id+' '+i.invoice_code+' | '+Number(i.total_amount||0).toLocaleString()+' | '+i.status+'</div>'})}

// PACKAGE BOOKINGS
async function loadBookings(){const{data}=await apiCall('GET','/api/v1/package-bookings',null,true);const tb=document.getElementById('bkl');tb.innerHTML='';(Array.isArray(data)?data:[]).forEach(r=>{const tr=document.createElement('tr');tr.innerHTML='<td>'+r.id+'</td><td>'+r.package_id+'</td><td>'+r.space_id+'</td><td>'+r.customer_id+'</td><td>'+(r.start_time||'').slice(0,16)+'</td><td>'+(r.end_time||'').slice(0,16)+'</td><td>'+Number(r.total_price||0).toLocaleString()+'</td><td>'+r.status+'</td><td><button class="btn btn-red" onclick="cancelBooking('+r.id+')">Cancel</button></td>';tb.appendChild(tr)});if(!Array.isArray(data)||!data.length)tb.innerHTML='<tr><td colspan="9" style="text-align:center;color:#666">Khong co booking</td></tr>'}
async function createBooking(){const d={package_id:parseInt(document.getElementById('bk-pkg').value),space_id:parseInt(document.getElementById('bk-sp').value),customer_id:parseInt(document.getElementById('bk-uid').value),start_time:document.getElementById('bk-start').value.replace('T','T')+':00',end_time:document.getElementById('bk-end').value.replace('T','T')+':00',notes:'Test'};const{ok,data}=await apiCall('POST','/api/v1/package-bookings',d,true);showMsg(ok?'Tao booking #'+data.id:(data.message||'Loi'),ok);if(ok)loadBookings()}
async function cancelBooking(id){const{ok,data}=await apiCall('PATCH','/api/v1/package-bookings/'+id+'/cancel',null,true);showMsg(ok?'Cancelled #'+id:(data.message||'Loi'),ok);loadBookings()}

// COURSES
async function loadCourses(){const{data}=await apiCall('GET','/courses/',null,true);const tb=document.getElementById('col');tb.innerHTML='';(Array.isArray(data)?data:[]).forEach(c=>{const tr=document.createElement('tr');tr.innerHTML='<td>'+c.id+'</td><td>'+c.course_name+'</td><td>'+c.description+'</td><td>'+c.status+'</td><td><button class="btn btn-red" onclick="delCourse('+c.id+')">Xoa</button></td>';tb.appendChild(tr)});if(!Array.isArray(data)||!data.length)tb.innerHTML='<tr><td colspan="5" style="text-align:center;color:#666">Khong co khoa hoc</td></tr>'}
async function createCourse(){const d={course_name:document.getElementById('co-name').value,description:document.getElementById('co-desc').value,status:'active',start_date:'2026-11-01',end_date:'2026-12-01'};if(!d.course_name){showMsg('Nhap ten!',false);return}const{ok,data}=await apiCall('POST','/courses/',d,true);showMsg(ok?'Tao khoa hoc: '+data.course_name:(data.message||'Loi'),ok);if(ok)loadCourses()}
async function delCourse(id){if(!confirm('Xoa khoa hoc #'+id+'?'))return;const{ok}=await apiCall('DELETE','/courses/'+id,null,true);showMsg(ok?'Da xoa':'Khong xoa duoc',ok);if(ok)loadCourses()}

// CHATBOT
async function askChatbot(){const msg=document.getElementById('chat-msg').value;if(!msg){showMsg('Nhap cau hoi!',false);return}showOut('chat-out','Dang xu ly...');const{ok,data}=await apiCall('POST','/api/v1/chatbot/ask',{message:msg});showOut('chat-out',ok?(data.answer||JSON.stringify(data)):(data.error||'Loi'))}
async function chatHealth(){const{ok,data}=await apiCall('GET','/api/v1/chatbot/health');showOut('chat-out',JSON.stringify(data))}

// RECOMMENDATIONS
async function getRecommendations(){const uid=document.getElementById('rec-uid').value;showOut('rec-out','Dang tai...');const{ok,data}=await apiCall('GET','/api/v1/recommendations/'+uid);showOut('rec-out',JSON.stringify(data,null,2))}

// CUSTOM API
async function runApi(){const m=document.getElementById('method').value;const p=document.getElementById('api-path').value;const bodyStr=document.getElementById('api-body').value;let body=null;if(bodyStr)try{body=JSON.parse(bodyStr)}catch(e){showMsg('JSON body khong hop le!',false);return}const out=document.getElementById('output');out.style.display='block';out.textContent='Loading '+m+' '+p+'...';const{status,data}=await apiCall(m,p,body,true);out.textContent=m+' '+p+'\nStatus: '+status+'\n\n'+JSON.stringify(data,null,2)}

// Auto load
loadRooms();
loadSpaceOptions();
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