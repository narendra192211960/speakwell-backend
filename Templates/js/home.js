// Set Profile Picture immediately (script is at bottom, so elements exist)
applyHomeProfilePic();

document.addEventListener('DOMContentLoaded', async () => {
    const userId = Auth.getUserId();
    const userName = Auth.getUserName();

    if (!userId) return;

    // Set Dynamic Greeting
    const greetingEl = document.getElementById('greetingMessage');
    if (greetingEl) greetingEl.textContent = getGreeting();

    // Set Welcome Name
    const nameEl = document.getElementById('welcomeUserName');
    if (nameEl && userName) nameEl.textContent = userName;
});

function applyHomeProfilePic() {
    const picUrl = localStorage.getItem('user_profile_picture');
    const imgEl = document.getElementById('home-user-profile-img');
    const defEl = document.getElementById('home-default-avatar');
    if (!imgEl || !defEl) return;

    if (picUrl && picUrl !== 'null' && picUrl !== 'undefined') {
        const BASE = (typeof window.BASE_URL !== 'undefined') ? window.BASE_URL : 'http://180.235.121.253:8071';
        const fullUrl = picUrl.startsWith('http') ? picUrl : (BASE + (picUrl.startsWith('/') ? picUrl.slice(1) : picUrl));

        imgEl.onerror = () => {
            imgEl.style.display = 'none';
            defEl.style.display = 'flex';
        };

        imgEl.src = fullUrl;
        imgEl.style.display = 'block';
        defEl.style.display = 'none';
    } else {
        imgEl.style.display = 'none';
        imgEl.src = '';
        defEl.style.display = 'flex';
    }
}

// Live sync when profile is updated from settings page
window.addEventListener('statsUpdated', applyHomeProfilePic);

function getGreeting() {
    const hour = new Date().getHours();
    if (hour < 12) return "Good Morning!";
    if (hour < 17) return "Good Afternoon!";
    if (hour < 21) return "Good Evening!";
    return "Good Night!";
}
