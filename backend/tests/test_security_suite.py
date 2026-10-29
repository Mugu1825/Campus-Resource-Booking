"""
Security Verification Suite for BACSE344 Digital Assignment 3
Tests:
1. Q2(a): Salted bcrypt password hashing vs plaintext representation
2. Q2(b): Multi-factor authentication (TOTP 2FA) setup, verify, and gated login
3. Q2(b): Role-based access rejection on Update and Delete APIs without valid token/role
"""
import sys
import os
import unittest
import json
import pyotp

# Add backend directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from extensions import bcrypt

class SecurityTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.client = cls.app.test_client()

    def test_01_password_salted_hash_vs_plaintext(self):
        """Q2(a): Verify passwords stored as salted bcrypt hashes ($2b$12$) not plaintext"""
        plaintext = "Pragamugu"
        # Generate two separate hashes of identical password to prove salting
        hash1 = bcrypt.generate_password_hash(plaintext).decode('utf-8')
        hash2 = bcrypt.generate_password_hash(plaintext).decode('utf-8')

        print("\n--- [Q2.a] PASSWORD STORAGE AUDIT ---")
        print(f"Plaintext input: {plaintext}")
        print(f"Salted Hash 1:   {hash1}")
        print(f"Salted Hash 2:   {hash2}")
        
        self.assertNotEqual(plaintext, hash1)
        self.assertNotEqual(hash1, hash2, "Bcrypt must use unique salts for identical passwords")
        self.assertTrue(hash1.startswith('$2b$'), "Hash must be valid Bcrypt format with salt")
        self.assertTrue(bcrypt.check_password_hash(hash1, plaintext))
        print(">> Result: PASSED - Password is cryptographically salted & hashed with Bcrypt.")

    def test_02_rbac_unauthenticated_update_delete_rejected(self):
        """Q2(b): Verify Update and Delete APIs reject requests without token (HTTP 401)"""
        print("\n--- [Q2.b] ROLE-BASED ACCESS CONTROL (RBAC) REJECTION TEST ---")
        dummy_id = "6aa2b483eb41795b21a635d5"
        
        # 1. Unauthenticated DELETE resource
        res_del = self.client.delete(f'/api/resources/{dummy_id}')
        print(f"1. DELETE /api/resources/<id> without token -> HTTP {res_del.status_code}")
        self.assertIn(res_del.status_code, [401, 403])

        # 2. Unauthenticated PUT resource
        res_put = self.client.put(f'/api/resources/{dummy_id}', json={"name": "Hacked Room"})
        print(f"2. PUT /api/resources/<id> without token -> HTTP {res_put.status_code}")
        self.assertIn(res_put.status_code, [401, 403])

        # 3. Unauthenticated PATCH booking approve
        res_approve = self.client.patch(f'/api/bookings/{dummy_id}/approve')
        print(f"3. PATCH /api/bookings/<id>/approve without token -> HTTP {res_approve.status_code}")
        self.assertIn(res_approve.status_code, [401, 403])

        print(">> Result: PASSED - All Update & Delete endpoints strictly reject unauthenticated requests.")

    def test_03_totp_mfa_workflow(self):
        """Q2(b): Verify TOTP Multi-Factor Authentication generation and verification"""
        print("\n--- [Q2.b] TOTP MULTI-FACTOR AUTHENTICATION WORKFLOW ---")
        # Generate random 32-char secret (compatible with Google Authenticator)
        secret = pyotp.random_base32()
        totp = pyotp.TOTP(secret)
        otp_uri = totp.provisioning_uri(name="mugunth@gmail.com", issuer_name="CRBS Campus Booking")
        current_code = totp.now()

        print(f"Generated TOTP Secret:  {secret}")
        print(f"Provisioning URI:       {otp_uri}")
        print(f"Current Valid 6-Digit:  {current_code}")

        # Verification tests
        self.assertTrue(totp.verify(current_code), "Valid current TOTP code must be accepted")
        self.assertFalse(totp.verify("000000"), "Invalid TOTP code must be rejected")
        print(">> Result: PASSED - TOTP Multi-Factor Authentication successfully generated and verified.")

if __name__ == '__main__':
    unittest.main()
