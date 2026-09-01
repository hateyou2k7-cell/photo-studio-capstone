"""
Test Selenium - Chuc nang Create/Delete Room
Project: Photo Studio Management System (Capstone)
URL: http://127.0.0.1:9999

Mo ta: Script test tinh nang Tao va Xoa Room tren he thong quan ly photo studio.
Su dung Selenium WebDriver de kiem tra trang web hoat dong dung,
ket hop requests de goi API endpoints.
"""
import unittest
import time
import json
import subprocess
import sys
import os
import urllib.request
import urllib.error
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By


BASE_URL = 'http://127.0.0.1:9999'


def api_call(method, path, body=None):
    """Goi API den Flask server."""
    url = f'{BASE_URL}{path}'
    headers = {'Content-Type': 'application/json'}
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        resp = urllib.request.urlopen(req, timeout=10)
        raw = resp.read()
        return resp.status, json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        raw = e.read()
        return e.code, json.loads(raw) if raw else {}


class TestRoomCreateDelete(unittest.TestCase):
    """Test chuc nang Tao va Xoa Room tren Flask API."""

    server = None

    @classmethod
    def setUpClass(cls):
        """Khoi dong Flask server truoc khi chay toan bo test."""
        os.system('lsof -ti:9999 | xargs kill -9 2>/dev/null')
        time.sleep(2)
        env = os.environ.copy()
        env['FLASK_ENV'] = 'production'
        src_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
        cls.server = subprocess.Popen(
            [sys.executable, 'app.py'],
            cwd=src_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        # Cho server khoi dong
        for _ in range(20):
            try:
                urllib.request.urlopen(f'{BASE_URL}/rooms/', timeout=2)
                break
            except Exception:
                time.sleep(1)
        else:
            raise RuntimeError('Flask server khong khoi dong duoc')

    def setUp(self):
        """Khoi dong Firefox headless browser."""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--width=1280')
        options.add_argument('--height=900')
        options.binary_location = '/snap/firefox/current/usr/lib/firefox/firefox'
        self.driver = webdriver.Firefox(options=options)
        self.driver.implicitly_wait(5)

    def _browser_check_page(self, url, expected_text=None):
        """Dung Selenium de mo trang va kiem tra noi dung."""
        self.driver.get(url)
        time.sleep(1)
        page_source = self.driver.page_source
        self.assertNotIn('error', self.driver.current_url.lower(),
                         f'Browser loi khi truy cap: {url}')
        if expected_text:
            self.assertIn(expected_text, page_source,
                          f'Khong tim thay "{expected_text}" trong trang')
        return page_source

    # ================================================================
    # TEST CREATE ROOM
    # ================================================================

    def test_01_create_room_success(self):
        """TC01: Tao room hop le -> 201 Created."""
        res = api_call('POST', '/rooms/', {
            'name': 'Selenium Test Room 1',
            'description': 'Tao boi Selenium test',
            'room_type': 'studio',
            'capacity': 10,
            'price_per_hour': 150000,
            'status': 'available'
        })
        self.assertEqual(res[0], 201, f"Status: {res}")
        data = res[1]
        self.assertIn('id', data)
        self.assertEqual(data['name'], 'Selenium Test Room 1')
        self.assertEqual(data['room_type'], 'studio')
        self.assertEqual(data['capacity'], 10)
        self.assertEqual(data['price_per_hour'], 150000.0)
        self.assertEqual(data['status'], 'available')

        # Selenium: kiem tra room xuat hien trong danh sach
        self._browser_check_page(
            f'{BASE_URL}/rooms/', 'Selenium Test Room 1')

    def test_02_create_room_duplicate_name(self):
        """TC02: Tao room trung ten -> 409 Conflict."""
        res = api_call('POST', '/rooms/', {
            'name': 'Selenium Test Room 1',
            'room_type': 'vip',
            'capacity': 5,
            'price_per_hour': 200000,
            'status': 'available'
        })
        self.assertEqual(res[0], 409, f"Status: {res}")
        self.assertIn('already exists', res[1]['message'].lower())

    def test_03_create_room_missing_fields(self):
        """TC03: Tao room thieu truong bat buoc -> 400 Bad Request."""
        res = api_call('POST', '/rooms/', {
            'name': 'Chi co ten'
        })
        self.assertEqual(res[0], 400, f"Status: {res}")

    def test_04_create_room_invalid_type(self):
        """TC04: Room type khong hop le -> 400 Bad Request."""
        res = api_call('POST', '/rooms/', {
            'name': 'Room Sai Type',
            'room_type': 'loai_khong_ton_tai',
            'capacity': 5,
            'price_per_hour': 100000,
            'status': 'available'
        })
        self.assertEqual(res[0], 400, f"Status: {res}")

    def test_05_create_room_invalid_status(self):
        """TC05: Status khong hop le -> 400 Bad Request."""
        res = api_call('POST', '/rooms/', {
            'name': 'Room Sai Status',
            'room_type': 'standard',
            'capacity': 5,
            'price_per_hour': 100000,
            'status': 'status_sai'
        })
        self.assertEqual(res[0], 400, f"Status: {res}")

    def test_06_create_room_negative_capacity(self):
        """TC06: Capacity am -> 400 Bad Request."""
        res = api_call('POST', '/rooms/', {
            'name': 'Room Capacity Am',
            'room_type': 'standard',
            'capacity': -1,
            'price_per_hour': 100000,
            'status': 'available'
        })
        self.assertEqual(res[0], 400, f"Status: {res}")

    def test_07_create_room_empty_name(self):
        """TC07: Ten trong -> 400 Bad Request."""
        res = api_call('POST', '/rooms/', {
            'name': '',
            'room_type': 'standard',
            'capacity': 5,
            'price_per_hour': 100000,
            'status': 'available'
        })
        self.assertEqual(res[0], 400, f"Status: {res}")

    def test_08_create_second_room(self):
        """TC08: Tao room thu hai thanh cong -> 201 Created."""
        res = api_call('POST', '/rooms/', {
            'name': 'Selenium Test Room 2',
            'description': 'Room thu 2 de test xoa',
            'room_type': 'vip',
            'capacity': 20,
            'price_per_hour': 300000,
            'status': 'booked'
        })
        self.assertEqual(res[0], 201, f"Status: {res}")
        self.assertEqual(res[1]['name'], 'Selenium Test Room 2')

    # ================================================================
    # TEST GET ROOM
    # ================================================================

    def test_09_get_rooms_list(self):
        """TC09: Lay danh sach rooms qua Selenium browser."""
        # Dung Selenium de truy cap API va doc JSON tu trang
        page_source = self._browser_check_page(f'{BASE_URL}/rooms/')
        self.assertIn('Selenium Test Room 1', page_source)
        self.assertIn('Selenium Test Room 2', page_source)

    def test_10_get_room_by_id(self):
        """TC10: Lay room theo ID -> 200 OK."""
        res_list = api_call('GET', '/rooms/')
        selenium_rooms = [r for r in res_list[1]
                          if r['name'].startswith('Selenium Test Room')]
        room_id = selenium_rooms[0]['id']

        res = api_call('GET', f'/rooms/{room_id}')
        self.assertEqual(res[0], 200, f"Status: {res}")
        self.assertEqual(res[1]['id'], room_id)

        # Selenium: kiem tra trang hien thi dung room
        self._browser_check_page(f'{BASE_URL}/rooms/{room_id}',
                                 'Selenium Test Room')

    def test_11_get_room_not_found(self):
        """TC11: Lay room khong ton tai -> 404 Not Found."""
        res = api_call('GET', '/rooms/999999')
        self.assertEqual(res[0], 404, f"Status: {res}")

    # ================================================================
    # TEST DELETE ROOM
    # ================================================================

    def test_12_delete_room_success(self):
        """TC12: Xoa room thanh cong -> 204 No Content."""
        res_list = api_call('GET', '/rooms/')
        room_2 = [r for r in res_list[1]
                   if r['name'] == 'Selenium Test Room 2']
        self.assertGreater(len(room_2), 0, 'Selenium Test Room 2 khong ton tai')
        room_id = room_2[0]['id']

        res = api_call('DELETE', f'/rooms/{room_id}')
        self.assertEqual(res[0], 204, f"Status: {res}")

    def test_13_delete_room_not_found(self):
        """TC13: Xoa room khong ton tai -> 404 Not Found."""
        res = api_call('DELETE', '/rooms/999999')
        self.assertEqual(res[0], 404, f"Status: {res}")

    def test_14_verify_deleted_room(self):
        """TC14: Xac nhan room da bi xoa."""
        res_list = api_call('GET', '/rooms/')
        room_2 = [r for r in res_list[1]
                   if r['name'] == 'Selenium Test Room 2']
        self.assertEqual(len(room_2), 0,
                         'Selenium Test Room 2 van ton tai sau khi xoa')

        # Selenium: xac nhan khong hien trong danh sach
        page_source = self._browser_check_page(f'{BASE_URL}/rooms/')
        self.assertNotIn('Selenium Test Room 2', page_source)

    # ================================================================
    # TEST DELETE THEN RECREATE
    # ================================================================

    def test_15_delete_and_recreate(self):
        """TC15: Xoa Room 1, tao lai cung ten -> 201 Created."""
        res_list = api_call('GET', '/rooms/')
        room_1 = [r for r in res_list[1]
                   if r['name'] == 'Selenium Test Room 1']
        if room_1:
            api_call('DELETE', f'/rooms/{room_1[0]["id"]}')

        res = api_call('POST', '/rooms/', {
            'name': 'Selenium Test Room 1',
            'description': 'Tao lai sau khi xoa',
            'room_type': 'conference',
            'capacity': 30,
            'price_per_hour': 500000,
            'status': 'available'
        })
        self.assertEqual(res[0], 201, f"Status: {res}")

        # Selenium: kiem tra room moi xuat hien
        page_source = self._browser_check_page(f'{BASE_URL}/rooms/')
        self.assertIn('Selenium Test Room 1', page_source)

    # ================================================================
    # CLEANUP
    # ================================================================

    def test_16_cleanup(self):
        """TC16: Don dep - xoa tat ca Selenium test rooms."""
        res_list = api_call('GET', '/rooms/')
        selenium_rooms = [r for r in res_list[1]
                          if r['name'].startswith('Selenium Test Room')]
        for room in selenium_rooms:
            api_call('DELETE', f'/rooms/{room["id"]}')

        res_list = api_call('GET', '/rooms/')
        remaining = [r for r in res_list[1]
                     if r['name'].startswith('Selenium Test Room')]
        self.assertEqual(len(remaining), 0,
                         f'Con lai {len(remaining)} room chua xoa')

    def tearDown(self):
        """Dong browser sau moi test case."""
        self.driver.quit()

    @classmethod
    def tearDownClass(cls):
        """Tat Flask server sau khi het test."""
        if cls.server:
            cls.server.terminate()
            cls.server.wait(timeout=5)


if __name__ == '__main__':
    unittest.main(verbosity=2)
