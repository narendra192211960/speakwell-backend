const Auth = {
    // Check if user is logged in
    checkLogin: () => {
        const userId = localStorage.getItem('user_id');
        if (!userId && !window.location.pathname.includes('login.html') && 
            !window.location.pathname.includes('signup.html') && 
            !window.location.pathname.includes('index.html')) {
            window.location.href = 'login.html';
        }
        return userId;
    },

    // Global Logout
    logout: () => {
        localStorage.removeItem('user_id');
        localStorage.removeItem('user_name');
        window.location.href = 'login.html';
    },

    // Session helper
    getUserId: () => {
        const id = localStorage.getItem('user_id');
        if (id) return id;
        try {
            const userData = JSON.parse(localStorage.getItem('user_data'));
            return userData ? (userData.id || userData.user_id) : null;
        } catch(e) { return null; }
    },
    getUserName: () => {
        const name = localStorage.getItem('user_name');
        if (name) return name;
        try {
            const userData = JSON.parse(localStorage.getItem('user_data'));
            return userData ? userData.name : null;
        } catch(e) { return null; }
    }
};

// Auto-redirect if trying to access home while logged out
Auth.checkLogin();

window.Auth = Auth;
