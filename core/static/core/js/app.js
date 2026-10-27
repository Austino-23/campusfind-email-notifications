document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.querySelector('.nav-toggle');
  const links = document.querySelector('.nav-links');
  if (toggle && links) toggle.addEventListener('click', () => {
    const open = links.classList.toggle('open');
    toggle.setAttribute('aria-expanded', String(open));
  });
  document.querySelectorAll('[data-mode]').forEach(button => button.addEventListener('click', () => {
    const mode = button.dataset.mode;
    const login = document.querySelector('#login-form');
    const register = document.querySelector('#register-form');
    if (!login || !register) return;
    login.classList.toggle('hidden', mode !== 'login');
    register.classList.toggle('hidden', mode !== 'register');
    document.querySelectorAll('.auth-tab[data-mode]').forEach(tab => tab.classList.toggle('active', tab.dataset.mode === mode));
    const hidden = document.querySelector(`#${mode === 'login' ? 'login-form' : 'register-form'} input[name="mode"]`);
    if (hidden) hidden.value = mode;
  }));
  const registerForm = document.querySelector('#register-form');
  if (registerForm) registerForm.addEventListener('submit', event => {
    const p = registerForm.querySelector('[name="password"]');
    const c = registerForm.querySelector('[name="confirm_password"]');
    if (p.value !== c.value) { event.preventDefault(); c.setCustomValidity('Passwords do not match.'); c.reportValidity(); }
    else c.setCustomValidity('');
  });
});
