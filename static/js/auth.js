/**
 * Authentication & Login Page JavaScript
 */

document.addEventListener('DOMContentLoaded', () => {
  // Password Show / Hide Toggle
  const togglePwdBtn = document.getElementById('togglePassword');
  const passwordInput = document.getElementById('password');

  if (togglePwdBtn && passwordInput) {
    togglePwdBtn.addEventListener('click', () => {
      const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordInput.setAttribute('type', type);
      
      const icon = togglePwdBtn.querySelector('i');
      if (icon) {
        if (type === 'text') {
          icon.classList.remove('bi-eye');
          icon.classList.add('bi-eye-slash');
        } else {
          icon.classList.remove('bi-eye-slash');
          icon.classList.add('bi-eye');
        }
      }
    });
  }

  // Role Selector Tabs
  const roleButtons = document.querySelectorAll('.role-tab-btn');
  const roleInput = document.getElementById('roleInput');

  roleButtons.forEach((btn) => {
    btn.addEventListener('click', () => {
      // Remove active from all
      roleButtons.forEach((b) => b.classList.remove('active'));
      // Add active to clicked
      btn.classList.add('active');
      // Set hidden input value
      const role = btn.getAttribute('data-role');
      if (roleInput) {
        roleInput.value = role;
      }
    });
  });

  // Client-side form submission visual feedback
  const loginForm = document.getElementById('collegeLoginForm');
  const submitBtn = document.getElementById('loginSubmitBtn');

  if (loginForm && submitBtn) {
    loginForm.addEventListener('submit', (e) => {
      const loginId = document.getElementById('loginId')?.value.trim();
      const pwd = passwordInput?.value.trim();

      if (!loginId || !pwd) {
        return; // HTML5 required handles it
      }

      // Show spinner on button
      submitBtn.disabled = true;
      submitBtn.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        <span>Authenticating...</span>
      `;
    });
  }
});

/**
 * 1-Click Quick Fill Demo Credentials for instant testing
 */
function fillDemoCredentials(role) {
  const loginIdInput = document.getElementById('loginId');
  const pwdInput = document.getElementById('password');
  const roleInput = document.getElementById('roleInput');
  const roleButtons = document.querySelectorAll('.role-tab-btn');

  if (!loginIdInput || !pwdInput || !roleInput) return;

  if (role === 'admin') {
    loginIdInput.value = 'admin@college.edu';
    pwdInput.value = 'admin123';
    roleInput.value = 'admin';
  } else if (role === 'faculty') {
    loginIdInput.value = 'anurag.verma@college.edu';
    pwdInput.value = 'faculty123';
    roleInput.value = 'faculty';
  } else if (role === 'student') {
    loginIdInput.value = 'aarav.patel@college.edu';
    pwdInput.value = 'student123';
    roleInput.value = 'student';
  }

  // Sync active tab visual
  roleButtons.forEach((btn) => {
    if (btn.getAttribute('data-role') === role) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  // Highlight fields briefly
  loginIdInput.style.backgroundColor = '#ecfdf5';
  pwdInput.style.backgroundColor = '#ecfdf5';
  setTimeout(() => {
    loginIdInput.style.backgroundColor = '';
    pwdInput.style.backgroundColor = '';
  }, 600);
}
