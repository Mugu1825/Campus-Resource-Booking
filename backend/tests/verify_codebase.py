import urllib.request
import json
import sys

BASE = 'http://localhost:5000/api'

def req(url, method='GET', data=None, token=None):
    headers = {'Content-Type': 'application/json'}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    encoded_data = json.dumps(data).encode('utf-8') if data is not None else None
    request = urllib.request.Request(url, data=encoded_data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request) as response:
            body = response.read().decode('utf-8')
            return response.status, json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(body)
        except Exception:
            return e.code, {'raw': body}

passed = 0
failed = 0

def test(name, condition, extra=""):
    global passed, failed
    if condition:
        print(f"  ✅ PASS: {name} {extra}")
        passed += 1
    else:
        print(f"  ❌ FAIL: {name} {extra}")
        failed += 1

print("="*70)
print("🚀 CAMPUS RESOURCE BOOKING SYSTEM — AUTOMATED VERIFICATION SUITE")
print("="*70)

# ---------------------------------------------------------
print("\n[1] Health Check & Public Routes")
# ---------------------------------------------------------
s, data = req(f'{BASE}/health')
test("Health check responds 200 OK", s == 200 and data.get('status') == 'ok')

s, data = req(f'{BASE}/auth/departments')
test("Get departments list", s == 200 and 'CSE' in data.get('departments', []))

# ---------------------------------------------------------
print("\n[2] Register Number Validation")
# ---------------------------------------------------------
# Invalid dept code (XYZ)
s, d = req(f'{BASE}/auth/register/student', 'POST', {
    'name': 'Bad Student', 'email': 'bad1@campus.edu', 'password': 'Password123!', 'reg_no': '25XYZ1011'
})
test("Reject invalid department code (25XYZ1011)", s == 400)

# Invalid format length / structure
s, d = req(f'{BASE}/auth/register/student', 'POST', {
    'name': 'Bad Student', 'email': 'bad2@campus.edu', 'password': 'Password123!', 'reg_no': '12345'
})
test("Reject non-compliant register number (12345)", s == 400)

# Valid registration
import time
uid = int(time.time()) % 10000
test_student_email = f'stu_{uid}@campus.edu'
test_student_reg = f'25ECE{uid:04d}'
s, d = req(f'{BASE}/auth/register/student', 'POST', {
    'name': f'Student {uid}', 'email': test_student_email, 'password': 'Password123!', 'reg_no': test_student_reg
})
test("Accept valid register number format", s == 201)

# Login with created student
s, stu_auth = req(f'{BASE}/auth/login', 'POST', {'email': test_student_email, 'password': 'Password123!'})
stu_token = stu_auth.get('token')
test("Student login & department extraction (ECE)", s == 200 and stu_auth.get('department') == 'ECE')

# ---------------------------------------------------------
print("\n[3] Staff Registration & Approval Lifecycle")
# ---------------------------------------------------------
test_staff_email = f'staff_{uid}@campus.edu'
s, d = req(f'{BASE}/auth/register/staff', 'POST', {
    'name': f'Staff {uid}', 'email': test_staff_email, 'department': 'CSE', 'password': 'StaffPassword123!'
})
test("Staff self-registration created as pending", s == 201)

# Login while pending should be BLOCKED (403)
s, d = req(f'{BASE}/auth/login', 'POST', {'email': test_staff_email, 'password': 'StaffPassword123!'})
test("Staff login blocked while pending (HTTP 403)", s == 403 and 'approval' in d.get('error', '').lower())

# Admin logs in
s, adm_auth = req(f'{BASE}/auth/login', 'POST', {'email': 'mugunth@gmail.com', 'password': 'Pragamugu'})
adm_token = adm_auth.get('token')
test("Admin login successful", s == 200 and adm_auth.get('role') == 'admin')

# Admin fetches pending staff
s, pending_list = req(f'{BASE}/admin/pending-staff', 'GET', None, adm_token)
staff_obj = next((x for x in pending_list if x['email'] == test_staff_email), None)
test("Pending staff appears in Admin approval queue", staff_obj is not None)

# Admin approves staff
s, app_res = req(f'{BASE}/admin/staff/{staff_obj["id"]}/approve', 'PATCH', None, adm_token)
test("Admin approves staff account", s == 200 and app_res.get('status') == 'active')

# Staff login now SUCCEEDS
s, staff_auth = req(f'{BASE}/auth/login', 'POST', {'email': test_staff_email, 'password': 'StaffPassword123!'})
staff_token = staff_auth.get('token')
test("Staff login succeeds after admin approval", s == 200 and staff_auth.get('role') == 'staff')

# ---------------------------------------------------------
print("\n[4] Resource Tiering & Role Authorization Guards")
# ---------------------------------------------------------
# Staff attempts to add PREMIUM resource -> should be FORBIDDEN (403)
s, d = req(f'{BASE}/resources', 'POST', {
    'name': 'Forbidden Premium Hall', 'type': 'auditorium', 'tier': 'premium', 'location': 'Block Z', 'capacity': 500
}, staff_token)
test("Staff cannot create Premium tier resource (HTTP 403)", s == 403)

# Staff creates STANDARD resource -> allowed (201)
s, std_res = req(f'{BASE}/resources', 'POST', {
    'name': f'Standard Lab {uid}', 'type': 'lab', 'tier': 'standard', 'location': 'Block D Room 10', 'capacity': 30
}, staff_token)
std_res_id = std_res.get('id') or std_res.get('_id') or (std_res.get('resource') or {}).get('id')
test("Staff can create Standard tier resource (HTTP 201)", s == 201 and std_res_id is not None)

# Admin creates PREMIUM resource -> allowed (201)
s, prem_res = req(f'{BASE}/admin/resources', 'POST', {
    'name': f'Premium Supercomputing Center {uid}', 'type': 'equipment', 'tier': 'premium', 'location': 'Block S', 'capacity': 20
}, adm_token)
prem_res_id = prem_res.get('id') or prem_res.get('_id') or (prem_res.get('resource') or {}).get('id')
test("Admin can create Premium tier resource (HTTP 201)", s == 201 and prem_res_id is not None)

# ---------------------------------------------------------
print("\n[5] Booking Engine & Business Logic Enforcement")
# ---------------------------------------------------------
# Test A: Exceeding 4 regular slots (e.g. 09:00 to 15:00 = 6 slots) -> 400
s, d = req(f'{BASE}/bookings', 'POST', {
    'resource_id': std_res_id, 'date_start': '2026-10-01', 'date_end': '2026-10-01',
    'start_slot': '09:00', 'end_slot': '15:00', 'is_hackathon': False
}, stu_token)
test("Reject regular booking exceeding 4 hours limit (HTTP 400)", s == 400)

# Test B: Regular booking across different dates -> 400
s, d = req(f'{BASE}/bookings', 'POST', {
    'resource_id': std_res_id, 'date_start': '2026-10-01', 'date_end': '2026-10-02',
    'start_slot': '10:00', 'end_slot': '12:00', 'is_hackathon': False
}, stu_token)
test("Reject multi-day regular booking (HTTP 400)", s == 400)

# Test C: Hackathon booking exceeding 2 days (48 hrs) -> 400
s, d = req(f'{BASE}/bookings', 'POST', {
    'resource_id': std_res_id, 'date_start': '2026-10-01', 'date_end': '2026-10-05',
    'start_slot': '09:00', 'end_slot': '21:00', 'is_hackathon': True, 'hackathon_event': 'Overlong Hackathon'
}, stu_token)
test("Reject hackathon exceeding 2-day limit (HTTP 400)", s == 400)

# Test D: Valid Standard booking creation
s, b1 = req(f'{BASE}/bookings', 'POST', {
    'resource_id': std_res_id, 'date_start': '2026-10-10', 'date_end': '2026-10-10',
    'start_slot': '10:00', 'end_slot': '12:00', 'is_hackathon': False
}, stu_token)
b1_id = b1.get('booking_id')
test("Create valid regular booking (10:00 - 12:00)", s == 201 and b1_id is not None)

# Test E: Overlapping conflict detection on same resource and date
# Overlaps 11:00 - 13:00 with 10:00 - 12:00
s, d = req(f'{BASE}/bookings', 'POST', {
    'resource_id': std_res_id, 'date_start': '2026-10-10', 'date_end': '2026-10-10',
    'start_slot': '11:00', 'end_slot': '13:00', 'is_hackathon': False
}, stu_token)
test("Prevent double booking: overlapping slot rejected (HTTP 400)", s == 400 and 'conflict' in d.get('error', '').lower())

# Test F: Student books Premium resource
s, b_prem = req(f'{BASE}/bookings', 'POST', {
    'resource_id': prem_res_id, 'date_start': '2026-10-12', 'date_end': '2026-10-12',
    'start_slot': '10:00', 'end_slot': '12:00', 'is_hackathon': False
}, stu_token)
b_prem_id = b_prem.get('booking_id')
test("Create booking for Premium resource", s == 201 and b_prem_id is not None)

# Test G: Student books Hackathon
s, b_hack = req(f'{BASE}/bookings', 'POST', {
    'resource_id': std_res_id, 'date_start': '2026-10-15', 'date_end': '2026-10-16',
    'start_slot': '09:00', 'end_slot': '21:00', 'is_hackathon': True, 'hackathon_event': 'Annual Hackathon'
}, stu_token)
b_hack_id = b_hack.get('booking_id')
test("Create multi-day Hackathon booking", s == 201 and b_hack_id is not None)

# ---------------------------------------------------------
print("\n[6] Approval Permissions & Queue Governance")
# ---------------------------------------------------------
# Staff approves Standard regular booking -> allowed
s, d = req(f'{BASE}/bookings/{b1_id}/approve', 'PATCH', None, staff_token)
test("Staff can approve Standard regular booking (HTTP 200)", s == 200 and d.get('booking', {}).get('status') == 'approved')

# Staff attempts to approve Premium resource booking -> FORBIDDEN (403)
s, d = req(f'{BASE}/bookings/{b_prem_id}/approve', 'PATCH', None, staff_token)
test("Staff CANNOT approve Premium resource booking (HTTP 403)", s == 403)

# Staff attempts to approve Hackathon booking -> FORBIDDEN (403)
s, d = req(f'{BASE}/bookings/{b_hack_id}/approve', 'PATCH', None, staff_token)
test("Staff CANNOT approve Hackathon booking (HTTP 403)", s == 403)

# Admin approves Premium booking -> allowed
s, d = req(f'{BASE}/bookings/{b_prem_id}/approve', 'PATCH', None, adm_token)
test("Admin can approve Premium resource booking (HTTP 200)", s == 200 and d.get('booking', {}).get('status') == 'approved')

# Admin approves Hackathon booking -> allowed
s, d = req(f'{BASE}/bookings/{b_hack_id}/approve', 'PATCH', None, adm_token)
test("Admin can approve Hackathon booking (HTTP 200)", s == 200 and d.get('booking', {}).get('status') == 'approved')

# ---------------------------------------------------------
print("\n[7] Student Self-Service & Cancellation Rules")
# ---------------------------------------------------------
# Create another pending booking to test cancel
s, b_cancel = req(f'{BASE}/bookings', 'POST', {
    'resource_id': std_res_id, 'date_start': '2026-10-20', 'date_end': '2026-10-20',
    'start_slot': '14:00', 'end_slot': '16:00', 'is_hackathon': False
}, stu_token)
b_cancel_id = b_cancel.get('booking_id')

s, d = req(f'{BASE}/bookings/{b_cancel_id}/cancel', 'PATCH', None, stu_token)
test("Student can cancel their own pending booking (HTTP 200)", s == 200)

# Student attempts to cancel already approved booking -> should be blocked
s, d = req(f'{BASE}/bookings/{b1_id}/cancel', 'PATCH', None, stu_token)
test("Student CANNOT cancel an already approved booking (HTTP 400)", s == 400)

# ---------------------------------------------------------
print("\n[8] Dynamic Slot Availability Endpoint")
# ---------------------------------------------------------
s, avail = req(f'{BASE}/resources/{std_res_id}/availability?date=2026-10-10')
booked_slots = avail.get('booked_slots', [])
test("Availability endpoint accurately lists booked slots", '10:00' in booked_slots and '11:00' in booked_slots)

# ---------------------------------------------------------
print("\n[9] Admin Overview Stats & Governance")
# ---------------------------------------------------------
s, stats = req(f'{BASE}/admin/stats', 'GET', None, adm_token)
test("Admin stats aggregation returns valid non-zero counts", 
     s == 200 and stats.get('total_resources', 0) > 0 and stats.get('total_users', 0) > 0)

print("\n" + "="*70)
print(f"📊 VERIFICATION SUMMARY: {passed} PASSED | {failed} FAILED")
print("="*70)

if failed > 0:
    sys.exit(1)
