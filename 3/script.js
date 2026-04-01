const passwordInput = document.getElementById('password');
const confirmInput = document.getElementById('confirm_password');
const form = document.getElementById('register-form');

const lengthReq = document.getElementById('length-req');
const uppercaseReq = document.getElementById('uppercase-req');
const lowercaseReq = document.getElementById('lowercase-req');
const numberReq = document.getElementById('number-req');

function checkPasswordStrength() {
    const password = passwordInput.value;
    
    if (password.length >= 8) {
        lengthReq.innerHTML = '✓ Минимум 8 символов';
        lengthReq.className = 'requirement valid';
    } else {
        lengthReq.innerHTML = '✗ Минимум 8 символов';
        lengthReq.className = 'requirement invalid';
    }
    
    if (/[A-Z]/.test(password)) {
        uppercaseReq.innerHTML = '✓ Заглавная буква';
        uppercaseReq.className = 'requirement valid';
    } else {
        uppercaseReq.innerHTML = '✗ Заглавная буква';
        uppercaseReq.className = 'requirement invalid';
    }
    
    if (/[a-z]/.test(password)) {
        lowercaseReq.innerHTML = '✓ Строчная буква';
        lowercaseReq.className = 'requirement valid';
    } else {
        lowercaseReq.innerHTML = '✗ Строчная буква';
        lowercaseReq.className = 'requirement invalid';
    }
    
    if (/[0-9]/.test(password)) {
        numberReq.innerHTML = '✓ Цифра';
        numberReq.className = 'requirement valid';
    } else {
        numberReq.innerHTML = '✗ Цифра';
        numberReq.className = 'requirement invalid';
    }
}

function checkPasswordMatch() {
    const password = passwordInput.value;
    const confirm = confirmInput.value;
    const confirmError = document.getElementById('confirm-error');
    
    if (confirm !== '' && password !== confirm) {
        confirmError.textContent = 'Пароли не совпадают';
        confirmError.style.display = 'block';
        return false;
    } else {
        confirmError.style.display = 'none';
        return true;
    }
}

passwordInput.addEventListener('input', function() {
    checkPasswordStrength();
    checkPasswordMatch();
});

confirmInput.addEventListener('input', checkPasswordMatch);

form.addEventListener('submit', function(event) {
    event.preventDefault();
    
    const username = document.getElementById('username').value;
    const email = document.getElementById('email').value;
    const password = passwordInput.value;
    const confirm = confirmInput.value;
    
    let isValid = true;
    
    if (!username) {
        document.getElementById('username-error').textContent = 'Введите логин';
        document.getElementById('username-error').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('username-error').style.display = 'none';
    }
    
    if (!email) {
        document.getElementById('email-error').textContent = 'Введите email';
        document.getElementById('email-error').style.display = 'block';
        isValid = false;
    } else if (!email.includes('@')) {
        document.getElementById('email-error').textContent = 'Введите корректный email';
        document.getElementById('email-error').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('email-error').style.display = 'none';
    }
    
    if (password.length < 8) {
        document.getElementById('password-error').textContent = 'Пароль должен быть не менее 8 символов';
        document.getElementById('password-error').style.display = 'block';
        isValid = false;
    } else if (!/(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/.test(password)) {
        document.getElementById('password-error').textContent = 'Пароль должен содержать заглавную, строчную буквы и цифру';
        document.getElementById('password-error').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('password-error').style.display = 'none';
    }
    
    if (password !== confirm) {
        document.getElementById('confirm-error').textContent = 'Пароли не совпадают';
        document.getElementById('confirm-error').style.display = 'block';
        isValid = false;
    } else {
        document.getElementById('confirm-error').style.display = 'none';
    }
    
    if (isValid) {
        const successDiv = document.getElementById('success-message');
        successDiv.textContent = 'Отправка данных...';
        successDiv.style.display = 'block';
        
        fetch('/api/register/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: username,
                email: email,
                password: password,
                confirm_password: confirm
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message) {
                successDiv.textContent = data.message;
                successDiv.style.background = '#2ecc71';
                form.reset();
                checkPasswordStrength();
                setTimeout(() => {
                    successDiv.style.display = 'none';
                }, 3000);
            } else if (data.errors) {
                successDiv.textContent = 'Ошибка регистрации';
                successDiv.style.background = '#e74c3c';
                setTimeout(() => {
                    successDiv.style.display = 'none';
                }, 3000);
                
                if (data.errors.email) {
                    document.getElementById('email-error').textContent = data.errors.email[0];
                    document.getElementById('email-error').style.display = 'block';
                }
                if (data.errors.username) {
                    document.getElementById('username-error').textContent = data.errors.username[0];
                    document.getElementById('username-error').style.display = 'block';
                }
            }
        })
        .catch(error => {
            successDiv.textContent = 'Ошибка соединения';
            successDiv.style.background = '#e74c3c';
            successDiv.style.display = 'block';
            setTimeout(() => {
                successDiv.style.display = 'none';
            }, 3000);
        });
    }
});