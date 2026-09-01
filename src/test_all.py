import os, sys, json

os.environ['FLASK_ENV'] = 'testing'
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
app = create_app()
client = app.test_client()

results = []

def test(name, method, path, data=None, headers=None):
    try:
        if method == 'GET':
            r = client.get(path, headers=headers)
        elif method == 'POST':
            r = client.post(path, json=data, headers=headers)
        elif method == 'PUT':
            r = client.put(path, json=data, headers=headers)
        elif method == 'DELETE':
            r = client.delete(path, headers=headers)
        elif method == 'PATCH':
            r = client.patch(path, json=data, headers=headers)
        status = r.status_code
        ok = status < 400
        results.append((name, status, ok))
        sym = "OK" if ok else "FAIL"
        print(f"  [{sym}] {status} {method:6s} {path} - {name}")
        return r
    except Exception as e:
        results.append((name, 0, False))
        print(f"  [ERR] {method:6s} {path} - {name}: {e}")
        return None

print("=" * 60)
print("PHOTO STUDIO - FULL ENDPOINT TEST")
print("=" * 60)

# === 1. AUTH ===
print("\n--- 1. Auth ---")
test("Check router", "GET", "/auth/check_router")
test("Signup", "POST", "/auth/signup", {"username":"testfinal2","password":"test1234","passwordconfirm":"test1234","email":"final2@example.com"})
r = test("Login", "POST", "/auth/login", {"username":"testfinal2","password":"test1234"})
token = r.get_json()['token'] if r and r.status_code == 200 else None
h = {"Authorization": f"Bearer {token}"} if token else {}

# Get valid provider_id from DB
from database.databases.factory_database import FactoryDatabase
session = FactoryDatabase.get_database('POSTGREE').session
from database.models.film_user_model import User, ProviderProfile
from database.models.film_space_model import Space, Resource, Consumable, SpaceResource
from database.models.film_package_model import ServicePackage, PackageItem
from database.models.film_reservation_model import Reservation, Review, ServiceSession
from database.models.auth.auth_user_model import AuthUserModel
from database.models.equipment_model import Equipment

profiles = session.query(ProviderProfile).all()
provider_id = profiles[0].id if profiles else 2
spaces = session.query(Space).all()
space_id = spaces[0].id if spaces else 1
resources = session.query(Resource).all()
consumables = session.query(Consumable).all()
packages = session.query(ServicePackage).all()
equipments = session.query(Equipment).all()
db_user = session.query(User).first()
user_id_for_test = db_user.id if db_user else 2

print(f"  DB: provider_id={provider_id}, space_id={space_id}, user_id={user_id_for_test}")

# === 2. ROOMS ===
print("\n--- 2. Rooms ---")
test("List rooms", "GET", "/rooms/")
r = test("Create room", "POST", "/rooms/", {"name":"TestRoom_Final","room_type":"studio","capacity":10,"price_per_hour":200000,"status":"available"})
room_id = r.get_json()['id'] if r and r.status_code == 201 else None
if room_id:
    test("Get room", "GET", f"/rooms/{room_id}")
    test("Update room", "PUT", f"/rooms/{room_id}", {"name":"TestRoom_Updated","room_type":"studio","capacity":15,"price_per_hour":250000,"status":"available"})
    test("Delete room", "DELETE", f"/rooms/{room_id}")

# === 3. SPACES ===
print("\n--- 3. Spaces ---")
test("List spaces", "GET", "/spaces/")
test("Search spaces", "GET", "/spaces/search?q=studio")
r = test("Create space", "POST", "/spaces/", {"provider_id":provider_id,"name":"Space_Final","space_type":"darkroom","description":"Test space","address":"123 Test","max_capacity":5,"base_price_per_hour":150000,"status":True})
new_space_id = r.get_json()['id'] if r and r.status_code == 201 else None
if new_space_id:
    test("Get space", "GET", f"/spaces/{new_space_id}")
    test("Update space", "PUT", f"/spaces/{new_space_id}", {"provider_id":provider_id,"name":"Space_Updated","space_type":"darkroom","base_price_per_hour":180000})
    # Images
    test("List images", "GET", f"/spaces/{new_space_id}/images")
    # Schedules
    test("List schedules", "GET", f"/spaces/{new_space_id}/schedule")
    r = test("Create schedule", "POST", f"/spaces/{new_space_id}/schedule", {"day_of_week":1,"start_time":"08:00","end_time":"22:00","is_available":True})
    sched_id = r.get_json()['id'] if r and r.status_code == 201 else None
    if sched_id:
        test("Update schedule", "PUT", f"/spaces/{new_space_id}/schedule/{sched_id}", {"day_of_week":2,"start_time":"09:00","end_time":"21:00","is_available":True})
        test("Delete schedule", "DELETE", f"/spaces/{new_space_id}/schedule/{sched_id}")
    test("Delete space", "DELETE", f"/spaces/{new_space_id}")

# === 4. EQUIPMENT ===
print("\n--- 4. Equipment ---")
test("List equipment", "GET", "/api/v1/equipment")
r = test("Create equipment", "POST", "/api/v1/equipment", {"provider_id":provider_id,"name":"CanonR5_Final","type":"camera","condition":"excellent","price_per_hour":100000})
eq_id = r.get_json()['id'] if r and r.status_code == 201 else None
if eq_id:
    test("Get equipment", "GET", f"/api/v1/equipment/{eq_id}")
    test("Update equipment", "PUT", f"/api/v1/equipment/{eq_id}", {"name":"CanonR5_Updated","type":"camera","condition":"good","price_per_hour":120000})
    test("Delete equipment", "DELETE", f"/api/v1/equipment/{eq_id}")

# === 5. RESERVATIONS ===
print("\n--- 5. Reservations ---")
test("List reservations", "GET", "/v1/reservations/")
r = test("Create reservation", "POST", "/v1/reservations/", {
    "user_id": user_id_for_test, "provider_id": provider_id, "space_id": space_id,
    "start_time": "2026-11-10T09:00:00", "end_time": "2026-11-10T11:00:00", "total_price": 300000
}, h)
res_id = r.get_json()['id'] if r and r.status_code == 201 else None
if res_id:
    test("Get reservation", "GET", f"/v1/reservations/{res_id}")
    test("List items", "GET", f"/v1/reservations/{res_id}/items")
    test("Add item", "POST", f"/v1/reservations/{res_id}/items", {"item_type":"space","item_id":space_id,"quantity":1,"price_at_booking":300000})
    test("Confirm", "POST", f"/v1/reservations/{res_id}/confirm", None, h)
    test("Approve", "POST", f"/v1/reservations/{res_id}/approve", None, h)
    test("Get payment", "GET", f"/v1/reservations/{res_id}/payment")
    test("Create payment", "POST", f"/v1/reservations/{res_id}/payment", {"user_id":user_id_for_test,"amount":300000,"method":"cash"}, h)
    test("List reviews", "GET", f"/v1/reservations/{res_id}/reviews")
    test("Add review", "POST", f"/v1/reservations/{res_id}/reviews", {"user_id":user_id_for_test,"space_id":space_id,"rating":5,"comment":"Great!"}, h)
    test("Checkin", "POST", f"/v1/reservations/{res_id}/checkin", None, h)
    test("Checkout", "POST", f"/v1/reservations/{res_id}/checkout", None, h)

# === 6. BILLING ===
print("\n--- 6. Billing ---")
# Customers
test("List customers", "GET", "/v1/billing/customers")
r = test("Create customer", "POST", "/v1/billing/customers", {"customer_name":"Cust_Final","email":"cf@x.com","phone":"0900000000"}, h)
cust_id = r.get_json()['id'] if r and r.status_code == 201 else None
if cust_id:
    test("Get customer", "GET", f"/v1/billing/customers/{cust_id}")
    test("Update customer", "PUT", f"/v1/billing/customers/{cust_id}", {"customer_name":"Cust_Updated"}, h)
# Products
test("List products", "GET", "/v1/billing/products")
r = test("Create product", "POST", "/v1/billing/products", {"product_name":"Film_Final","description":"35mm","product_code":"FF001"}, h)
prod_id = r.get_json()['id'] if r and r.status_code == 201 else None
if prod_id:
    test("Get product", "GET", f"/v1/billing/products/{prod_id}")
    test("Update product", "PUT", f"/v1/billing/products/{prod_id}", {"product_name":"Film_Updated"}, h)
# Invoices
test("List invoices", "GET", "/v1/billing/invoices")
r = test("Create invoice", "POST", "/v1/billing/invoices", {"customer_id":cust_id,"total_amount":500000,"status":"pending"}, h)
inv_id = r.get_json()['id'] if r and r.status_code == 201 else None
if inv_id:
    test("Get invoice", "GET", f"/v1/billing/invoices/{inv_id}")
    test("Update invoice", "PUT", f"/v1/billing/invoices/{inv_id}", {"status":"paid","total_amount":550000}, h)
    test("List invoice items", "GET", f"/v1/billing/invoices/{inv_id}/items")
    if prod_id:
        test("Add invoice item", "POST", f"/v1/billing/invoices/{inv_id}/items", {"product_id":prod_id,"quantity":2,"unit_price":250000,"total_price":500000}, h)
    test("List payments", "GET", f"/v1/billing/invoices/{inv_id}/payments")

test("Delete product (cleanup)", "DELETE", f"/v1/billing/products/{prod_id}", None, h)

# === 7. PACKAGE BOOKINGS ===
print("\n--- 7. Package Bookings ---")
test("List package bookings", "GET", "/api/v1/package-bookings")
if packages:
    pkg_id = packages[0].id
    r = test("Create booking", "POST", "/api/v1/package-bookings", {
        "package_id": pkg_id, "space_id": space_id, "customer_id": user_id_for_test,
        "start_time": "2026-12-20T09:00:00", "end_time": "2026-12-20T12:00:00", "notes": "Test"
    })
    bk_id = r.get_json()['id'] if r and r.status_code == 201 else None
    if bk_id:
        test("Get booking", "GET", f"/api/v1/package-bookings/{bk_id}")
        test("Cancel booking", "PATCH", f"/api/v1/package-bookings/{bk_id}/cancel")

# === 8. CHATBOT ===
print("\n--- 8. Chatbot ---")
test("Health", "GET", "/api/v1/chatbot/health")
test("Ask", "POST", "/api/v1/chatbot/ask", {"message":"Phim 35mm la gi?"})

# === 9. RECOMMENDATIONS ===
print("\n--- 9. Recommendations ---")
test("Get recommendations", "GET", f"/api/v1/recommendations/{user_id_for_test}")

# === 10. COURSES ===
print("\n--- 10. Courses ---")
test("List courses", "GET", "/courses/")
r = test("Create course", "POST", "/courses/", {"course_name":"Film_Final","description":"Intro","status":"active","start_date":"2026-11-01","end_date":"2026-12-01"})
c_id = r.get_json()['id'] if r and r.status_code == 201 else None
if c_id:
    test("Get course", "GET", f"/courses/{c_id}")
    test("Update course", "PUT", f"/courses/{c_id}", {"course_name":"Film_Updated","description":"Updated","status":"active","start_date":"2026-11-01","end_date":"2026-12-01"})
    test("Delete course", "DELETE", f"/courses/{c_id}")

# SUMMARY
print("\n" + "=" * 60)
total = len(results)
passed = sum(1 for _, _, ok in results if ok)
failed = total - passed
print(f"TOTAL: {total} | PASSED: {passed} | FAILED: {failed}")
print("=" * 60)

if failed > 0:
    print("\nFailed tests:")
    for name, status, ok in results:
        if not ok:
            print(f"  - {name} (status: {status})")
