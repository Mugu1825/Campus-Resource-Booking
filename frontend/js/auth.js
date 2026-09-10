document.addEventListener('DOMContentLoaded', () => {
  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const btn = document.getElementById('login-btn');
      btn.disabled = true;
      try {
        const body = {
          email: document.getElementById('email').value,
          password: document.getElementById('password').value
        };
        const data = await api.post('/auth/login', body);
        localStorage.setItem('crbs_token', data.token);
        localStorage.setItem('crbs_role', data.role);
        localStorage.setItem('crbs_user_id', data.user_id);
        localStorage.setItem('crbs_name', data.name);
        if (data.dept) localStorage.setItem('crbs_dept', data.dept);
        
        if (data.role === 'student') window.location.href = 'dashboard.html';
        else if (data.role === 'staff') window.location.href = 'staff.html';
        else if (data.role === 'admin') window.location.href = 'admin.html';
      } catch (err) {
        showAlert('login-alert', err.message);
        btn.disabled = false;
      }
    });
  }

  const regStudentForm = document.getElementById('register-student-form');
  if (regStudentForm) {
    const regNoInput = document.getElementById('reg_no');
    const hint = document.getElementById('reg-hint');
    const regex = /^\d{2}(CSE|ECE|EEE|MEE|INT|CIV|CHE|AER|BIO|MBA|MCA)\d{4}$/;
    
    regNoInput.addEventListener('input', () => {
      if (regex.test(regNoInput.value)) {
        regNoInput.style.borderColor = 'var(--success)';
        hint.style.color = 'var(--success)';
        hint.innerText = 'Valid format ✓';
      } else {
        regNoInput.style.borderColor = 'var(--danger)';
        hint.style.color = 'var(--danger)';
        hint.innerText = 'Format: YY + 3-char dept (e.g. CSE) + 4 digits ✗';
      }
    });

    regStudentForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const p1 = document.getElementById('password').value;
      const p2 = document.getElementById('confirm_password').value;
      if (p1 !== p2) return showAlert('register-alert', 'Passwords do not match');
      if (!regex.test(regNoInput.value)) return showAlert('register-alert', 'Invalid register number format');
      
      const btn = document.getElementById('register-btn');
      btn.disabled = true;
      
      try {
        const body = {
          name: document.getElementById('name').value.trim(),
          email: document.getElementById('email').value.trim(),
          register_no: regNoInput.value.trim().toUpperCase(),
          reg_no: regNoInput.value.trim().toUpperCase(),
          password: p1
        };
        await api.post('/auth/register/student', body);
        showAlert('register-alert', 'Registration successful! You can now login.', 'success');
        setTimeout(() => window.location.href = 'login.html', 2000);
      } catch (err) {
        showAlert('register-alert', err.message);
        btn.disabled = false;
      }
    });
  }

  const regStaffForm = document.getElementById('register-staff-form');
  if (regStaffForm) {
    regStaffForm.addEventListener('submit', async (e) => {
      e.preventDefault();
      const p1 = document.getElementById('password').value;
      const p2 = document.getElementById('confirm_password').value;
      if (p1 !== p2) return showAlert('register-alert', 'Passwords do not match');
      
      const btn = document.getElementById('register-btn');
      btn.disabled = true;
      
      try {
        const body = {
          name: document.getElementById('name').value,
          email: document.getElementById('email').value,
          department: document.getElementById('department').value,
          password: p1
        };
        await api.post('/auth/register/staff', body);
        showAlert('register-alert', 'Your registration has been submitted. An admin will review and approve your account before you can log in.', 'success');
        setTimeout(() => window.location.href = 'login.html', 4000);
      } catch (err) {
        showAlert('register-alert', err.message);
        btn.disabled = false;
      }
    });
  }
});
