import { CONFIG } from './config.js';

function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    fetch(`${CONFIG.API_BASE_URL}/login`, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
    })
    .then(response => response.json())
    .then(window.location.href = '/shopping-list.html');
}

function register() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    fetch(`${CONFIG.API_BASE_URL}/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, username: email })
    })
    .then(response => response.json())
    .then(data => alert(data.message));
}

function provider(provider) {
    window.location.href = `${CONFIG.API_BASE_URL}/login/${provider}`;
}

document.getElementById('login-button').addEventListener('click', login);

document.getElementById('register-button').addEventListener('click', register);

