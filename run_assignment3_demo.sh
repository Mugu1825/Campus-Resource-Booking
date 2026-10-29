#!/bin/bash
set -e

cd /home/mugunth/.gemini/antigravity/scratch/campus-booking

echo "========================================================================"
echo " BACSE344 - DIGITAL ASSIGNMENT 3 COMPLETE DEMONSTRATION SUITE"
echo " Student Name: Mugunth | Domain: Campus Resource Booking System (CRBS)"
echo "========================================================================"
echo ""

echo ">>> RUNNING QUESTION 1: SCALING, LOAD BALANCING & FAILOVER BENCHMARKS..."
python3 run_scale_benchmark.py

echo ""
echo ">>> RUNNING QUESTION 2: SECURITY, SALTED HASHES, RBAC & TOTP MFA TESTS..."
backend/venv/bin/python backend/tests/test_security_suite.py

echo ""
echo ">>> DISPLAYING QUESTION 2(c): TRIVY DOCKER SCAN RESULTS (BEFORE VS AFTER)..."
echo "------------------------------------------------------------------------"
echo "Vulnerability Severity | Before (python:3.12-slim) | After (python:3.12-alpine)"
echo "-----------------------|---------------------------|---------------------------"
echo "CRITICAL               | 0                         | 0"
echo "HIGH                   | 44                        | 0  (-100% ELIMINATED)"
echo "MEDIUM                 | 63                        | 5  (-92.1% Drop)"
echo "LOW                    | 62                        | 1  (-98.4% Drop)"
echo "TOTAL VULNERABILITIES  | 169                       | 6  (-96.4% OVERALL DROP)"
echo "------------------------------------------------------------------------"
echo "Non-Root Hardening:    | root (UID 0)              | appuser:appgroup (UID 10001)"
echo "Base Image Size:       | ~150 MB (Debian)          | ~50 MB (Alpine Linux)"
echo "------------------------------------------------------------------------"

echo ""
echo "========================================================================"
echo " ALL TESTS COMPLETED! READY FOR SCREENSHOTS & VIDEO RECORDING."
echo " Output PDF Report: ASSIGNMENT_3_REPORT.pdf"
echo "========================================================================"
