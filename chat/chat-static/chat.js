let websocket = null; 


function searchUser() {
    const searchValue = document.getElementById("user-search").value.trim();
    if (searchValue === "") {
        alert("Пожалуйста, введите имя пользователя для поиска.");
        return;
    }
    document.getElementById("user-search").value = "";

    fetch(`/search-user?username=${encodeURIComponent(searchValue)}`, {
        method: 'GET'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Пользователь не существует.");
        }
        return response.json();
    })
    .then(guessData => {
        openChat(guessData);
    })
    .catch(error => {
        alert("Пользователь не существует или при поиске произошла ошибка.");
    });
}


function openChat(guess) {
    const token = localStorage.getItem('access_token'); 
    const chatHistoryDiv = document.getElementById("chat-history");
    chatHistoryDiv.innerHTML = ""; 

    fetch(`/messages/${guess.id}?token=${token}`, { 
        method: 'GET'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Не удалось получить историю сообщений");
        }
        return response.json();
    })
    .then(data => {
        const messages = data.messages; 
        const chat_id = data.chat_id;   
        const chat_title = data.chat_title;
        document.getElementById("chat-header").innerHTML = `<h2>${chat_title}</h2>`;
 
        messages.forEach(message => {
            const messageElement = document.createElement("div");
            messageElement.className = "message";
            messageElement.innerHTML = `${message.sender_name}: ${message.content}`;
            chatHistoryDiv.appendChild(messageElement);
        });

        connectWebSocket(chat_id);
    })
    .catch(error => {
        alert("Не удалось получить историю сообщений, или произошла ошибка.");
    });
}


function connectWebSocket(chatId) {
    if (websocket) {
        websocket.close(); 
    }

    websocket = new WebSocket(`ws://localhost:8080/ws/chat/${chatId}`);

    websocket.onopen = () => {
        console.log("Подключен к WebSocket");
    };

    websocket.onmessage = (event) => {
        const message = event.data;
        const chatHistoryDiv = document.getElementById("chat-history");
        const messageElement = document.createElement("div");
        messageElement.className = "message";
        messageElement.innerHTML = message;
        chatHistoryDiv.appendChild(messageElement);
    };

    websocket.onclose = () => {
        console.log("WebSocket закрыт.");
    };

    websocket.onerror = (error) => {
        console.error("Ошибка WebSocket:", error);
    };
}

function sendMessage() {
    const token = localStorage.getItem('access_token'); 
    const content = document.getElementById("message-input").value.trim();
    if (!websocket || websocket.readyState !== WebSocket.OPEN) {
        alert("Невозможно отправить сообщение, WebSocket не подключен.");
        return;
    }
    fetch(`/get_user?token=${token}`, { 
        method: 'GET'
    })
    .then(response => {
        if (!response.ok) {
            throw new Error("Невозможно получить информацию о пользователе");
        }
        return response.json();
    })
    .then(data =>{
        const message = {
            content: content,
            sender_id: data.id
        };
        websocket.send(JSON.stringify(message));
        document.getElementById("message-input").value = ""; 
        
        loadChatList();
    })
}
function loadChatList() {
    const token = localStorage.getItem('access_token'); 
    fetch(`/chats/recent_messages?token=${token}`, { method: 'GET' })
    .then(response => {
        if (!response.ok) {
            throw new Error("Невозможно загрузить список чатов");
        }
        return response.json();
    })
    .then(chatRooms => {
        const { chats, guess} = chatRooms;
        const chatListDiv = document.getElementById("chat-list");
        chatListDiv.innerHTML = ""; 

        chats.forEach(chat => {
            const chatItem = document.createElement("div");
            chatItem.className = "chat-item";
            
            const matchedGuess = guess.find(g => g.id === chat.guess_id || g.id === chat.owner_id);
            
            chatItem.onclick = () => {
                if (matchedGuess) {
                    openChat(matchedGuess); 
                } else {
                    openChat(chat); 
                }
            };

            chatItem.innerHTML = `
                <div class="chat-info">
                    <div class="name">${chat.name}</div>
                    <div class="last-message">${chat.last_message.sender_name}: ${chat.last_message.content}</div>
                </div>
            `;
            chatListDiv.appendChild(chatItem);
        });
    })
    .catch(error => {
        alert("Не удалось загрузить список чатов, или произошла ошибка.");
    });
}
