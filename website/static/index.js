document.getElementById('login').addEventListener('submit', async function(event) {
    event.preventDefault(); 

    const username = document.getElementById('loginusername').value;
    const password = document.getElementById('loginpassword').value;

    const loginData = {
        username: username,
        password: password
    };

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loginData),
        });

        if (response.ok) {
            const result = await response.json();
            localStorage.setItem('access_token', result.access_token);
            alert("Login successfully");
            window.location.href = `http://localhost:8080/chat`;
        } else {
            const result = await response.json();
            alert(result.message);
        }
    } catch (error) {
        console.error(error);
    }
});
document.getElementById('register').addEventListener('submit', async function(event) {
    event.preventDefault();

    const name = document.getElementById('name').value;
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;
    const email = document.getElementById('email').value;

    const loginData = {
        name : name,
        username: username,
        password: password,
        email: email
    };

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(loginData),
        });

        if (response.ok) {
            const result = await response.json();
            alert(result.message);
        } else{
            const result = await response.json();
            alert(result.detail);
        }
    } catch (error) {
        alert(error.message);
    }
});