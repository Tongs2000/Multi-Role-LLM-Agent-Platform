let socket = null;
let token = null;
let currentUser = null;

function showLogin() {
    document.getElementById('loginForm').classList.remove('hidden');
    document.getElementById('registerForm').classList.add('hidden');
}

function showRegister() {
    document.getElementById('loginForm').classList.add('hidden');
    document.getElementById('registerForm').classList.remove('hidden');
}

async function login() {
    const username = document.getElementById('loginUsername').value;
    const password = document.getElementById('loginPassword').value;
    
    try {
        const response = await fetch('/token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `username=${encodeURIComponent(username)}&password=${encodeURIComponent(password)}`
        });
        
        if (!response.ok) {
            throw new Error('Login failed');
        }
        
        const data = await response.json();
        token = data.access_token;
        currentUser = username;
        
        document.getElementById('authSection').classList.add('hidden');
        document.getElementById('chatSection').classList.remove('hidden');
        
        connectWebSocket();
        loadMessageHistory();
    } catch (error) {
        alert('Login failed: ' + error.message);
    }
}

async function register() {
    const username = document.getElementById('registerUsername').value;
    const password = document.getElementById('registerPassword').value;
    
    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username,
                password
            })
        });
        
        if (!response.ok) {
            throw new Error('Registration failed');
        }
        
        alert('Registration successful! Please login.');
        showLogin();
        document.getElementById('registerUsername').value = '';
        document.getElementById('registerPassword').value = '';
    } catch (error) {
        alert('Registration failed: ' + error.message);
    }
}

function logout() {
    if (socket) {
        socket.close();
        socket = null;
    }
    token = null;
    currentUser = null;
    document.getElementById('chatMessages').innerHTML = '';
    document.getElementById('messageInput').value = '';
    document.getElementById('authSection').classList.remove('hidden');
    document.getElementById('chatSection').classList.add('hidden');
}

function connectWebSocket() {
    socket = new WebSocket(`ws://${window.location.host}/ws/${token}`);
    
    socket.onopen = () => {
        console.log('WebSocket connected');
    };
    
    socket.onmessage = (event) => {
        const messagesDiv = document.getElementById('chatMessages');
        const messageDiv = document.createElement('div');
        messageDiv.className = 'message';
        
        // Check if the message is from the current user
        if (event.data.startsWith(currentUser + ':')) {
            messageDiv.classList.add('own-message');
        }
        
        messageDiv.innerHTML = `
            <div class="sender">${event.data.split(':')[0]}</div>
            <div class="content">${event.data.split(':').slice(1).join(':')}</div>
            <div class="timestamp">${new Date().toLocaleTimeString()}</div>
        `;
        
        messagesDiv.appendChild(messageDiv);
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    };
    
    socket.onclose = () => {
        console.log('WebSocket disconnected');
    };
}

async function loadMessageHistory() {
    try {
        const response = await fetch('/messages', {
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });
        
        if (!response.ok) {
            throw new Error('Failed to load message history');
        }
        
        const messages = await response.json();
        const messagesDiv = document.getElementById('chatMessages');
        messagesDiv.innerHTML = '';
        
        messages.reverse().forEach(msg => {
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message';
            
            if (msg.sender === currentUser) {
                messageDiv.classList.add('own-message');
            }
            
            messageDiv.innerHTML = `
                <div class="sender">${msg.sender}</div>
                <div class="content">${msg.content}</div>
                <div class="timestamp">${new Date(msg.timestamp).toLocaleString()}</div>
            `;
            
            messagesDiv.appendChild(messageDiv);
        });
        
        messagesDiv.scrollTop = messagesDiv.scrollHeight;
    } catch (error) {
        console.error('Error loading message history:', error);
    }
}

function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();
    
    if (message && socket && socket.readyState === WebSocket.OPEN) {
        socket.send(message);
        input.value = '';
    }
}

// Allow sending message with Enter key
document.getElementById('messageInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        sendMessage();
    }
});

// Initialize
showLogin();