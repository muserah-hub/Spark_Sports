document.addEventListener('DOMContentLoaded', () => {
    // --- Mobile Menu Toggle ---
    const menuToggle = document.querySelector('.menu-toggle');
    const navMenu = document.querySelector('.nav-menu');

    if (menuToggle && navMenu) {
        menuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            const spans = menuToggle.querySelectorAll('span');
            spans.forEach(span => span.classList.toggle('active'));
        });
    }

    // --- Automatically Dismiss Alert Messages ---
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.transform = 'translateX(120%)';
            alert.style.opacity = '0';
            alert.style.transition = 'all 0.5s ease';
            setTimeout(() => alert.remove(), 500);
        }, 5000);

        const closeBtn = alert.querySelector('.alert-close');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                alert.style.transform = 'translateX(120%)';
                alert.style.opacity = '0';
                alert.style.transition = 'all 0.5s ease';
                setTimeout(() => alert.remove(), 500);
            });
        }
    });

    // --- Floating Chatbot Panel Toggle ---
    const chatbotBubble = document.getElementById('chatbotBubble');
    const chatbotPanel = document.getElementById('chatbotPanel');
    const chatCloseBtn = document.getElementById('chatCloseBtn');

    if (chatbotBubble && chatbotPanel) {
        chatbotBubble.addEventListener('click', () => {
            chatbotPanel.classList.toggle('open');
            if (chatbotPanel.classList.contains('open')) {
                document.getElementById('chatInput').focus();
            }
        });

        if (chatCloseBtn) {
            chatCloseBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                chatbotPanel.classList.remove('open');
            });
        }
    }

    // --- Make Chatbot Bubble Draggable ---
    if (chatbotBubble) {
        let isDragging = false;
        let startX, startY;
        let initialX, initialY;

        const dragStart = (e) => {
            // Ignore drags on form inputs inside the panel if bubble is attached
            if (e.target.closest('#chatbotPanel')) return;

            if (e.type === "touchstart") {
                startX = e.touches[0].clientX - chatbotBubble.getBoundingClientRect().left;
                startY = e.touches[0].clientY - chatbotBubble.getBoundingClientRect().top;
            } else {
                startX = e.clientX - chatbotBubble.getBoundingClientRect().left;
                startY = e.clientY - chatbotBubble.getBoundingClientRect().top;
            }
            
            initialX = chatbotBubble.offsetLeft;
            initialY = chatbotBubble.offsetTop;
            isDragging = true;
        };

        const drag = (e) => {
            if (!isDragging) return;
            
            let clientX = e.type === "touchmove" ? e.touches[0].clientX : e.clientX;
            let clientY = e.type === "touchmove" ? e.touches[0].clientY : e.clientY;

            let x = clientX - startX;
            let y = clientY - startY;

            const padding = 10;
            const minX = padding;
            const minY = padding;
            const maxX = window.innerWidth - chatbotBubble.offsetWidth - padding;
            const maxY = window.innerHeight - chatbotBubble.offsetHeight - padding;

            x = Math.max(minX, Math.min(x, maxX));
            y = Math.max(minY, Math.min(y, maxY));

            chatbotBubble.style.left = `${x}px`;
            chatbotBubble.style.top = `${y}px`;
            chatbotBubble.style.bottom = 'auto';
            chatbotBubble.style.right = 'auto';

            if (chatbotPanel) {
                const panelPadding = 10;
                let panelX = x + chatbotBubble.offsetWidth - chatbotPanel.offsetWidth;
                let panelY = y - chatbotPanel.offsetHeight - panelPadding;

                panelX = Math.max(padding, Math.min(panelX, window.innerWidth - chatbotPanel.offsetWidth - padding));
                panelY = Math.max(padding, Math.min(panelY, window.innerHeight - chatbotPanel.offsetHeight - padding));

                chatbotPanel.style.left = `${panelX}px`;
                chatbotPanel.style.top = `${panelY}px`;
                chatbotPanel.style.bottom = 'auto';
                chatbotPanel.style.right = 'auto';
            }
        };

        const dragEnd = () => {
            isDragging = false;
        };

        chatbotBubble.addEventListener('mousedown', dragStart);
        document.addEventListener('mousemove', drag);
        document.addEventListener('mouseup', dragEnd);

        chatbotBubble.addEventListener('touchstart', dragStart, { passive: true });
        document.addEventListener('touchmove', drag, { passive: false });
        document.addEventListener('touchend', dragEnd);
    }

    // --- Interactive AJAX Chat Logic ---
    const chatInput = document.getElementById('chatInput');
    const chatSendBtn = document.getElementById('chatSendBtn');
    const chatBody = document.getElementById('chatBody');

    if (chatInput && chatSendBtn && chatBody) {
        // Send message trigger
        const sendMessage = () => {
            const query = chatInput.value.trim();
            if (!query) return;

            // Render user bubble
            appendMessage(query, 'user');
            chatInput.value = '';

            // Render typing indicator
            const typingIndicator = showTypingIndicator();

            // Fetch CSRF Token
            const csrftoken = getCookie('csrftoken');

            // Collect active product context if set on detail page
            const payload = {
                message: query,
                product_context: window.sparkProductContext || null
            };

            // Call endpoint
            fetch('/chatbot/message/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify(payload)
            })
            .then(res => {
                if (!res.ok) throw new Error('API server returned error');
                return res.json();
            })
            .then(data => {
                typingIndicator.remove();
                appendMessage(data.response, 'bot');
            })
            .catch(err => {
                typingIndicator.remove();
                appendMessage("⚠️ I'm sorry, I am having trouble connecting to my servers. Please try again later.", 'bot');
            });
        };

        chatSendBtn.addEventListener('click', sendMessage);
        chatInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    }

    // --- Helper function to append bubbles ---
    function appendMessage(text, sender) {
        const chatBody = document.getElementById('chatBody');
        if (!chatBody) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `chat-message ${sender}`;

        // Format raw markdown response to clean HTML
        messageDiv.innerHTML = formatMarkdown(text);

        const timeDiv = document.createElement('div');
        timeDiv.className = 'chat-message-time';
        timeDiv.innerText = 'Just now';
        messageDiv.appendChild(timeDiv);

        chatBody.appendChild(messageDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
    }

    // --- Helper to show typing indicator ---
    function showTypingIndicator() {
        const chatBody = document.getElementById('chatBody');
        const loaderDiv = document.createElement('div');
        loaderDiv.className = 'chat-loading';
        loaderDiv.innerHTML = '<span></span><span></span><span></span>';
        chatBody.appendChild(loaderDiv);
        chatBody.scrollTop = chatBody.scrollHeight;
        return loaderDiv;
    }

    // --- Helper to parse simple markdown ---
    function formatMarkdown(text) {
        let formatted = text
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;");

        // Format headings: ### Heading
        formatted = formatted.replace(/^### (.*$)/gim, '<h4 style="font-weight: 700; margin-top: 10px; margin-bottom: 5px;">$1</h4>');
        formatted = formatted.replace(/^## (.*$)/gim, '<h4 style="font-weight: 700; margin-top: 10px; margin-bottom: 5px;">$1</h4>');
        
        // Format bold markdown: **bold text**
        formatted = formatted.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Format italic markdown: *italic text*
        formatted = formatted.replace(/\*(.*?)\*/g, '<em>$1</em>');

        // Format bullets: * item or - item
        formatted = formatted.replace(/^\s*[\*\-]\s+(.*$)/gim, '<li style="margin-left: 15px; margin-bottom: 3px;">$1</li>');

        // Convert double returns to paragraphs
        formatted = formatted.replace(/\n\n/g, '<br><br>');
        
        // Convert single returns to line breaks
        formatted = formatted.replace(/\n/g, '<br>');

        return formatted;
    }

    // --- Helper to get Cookie ---
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
