const Validation = {
    email: (email) => {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(String(email).toLowerCase());
    },

    phone: (phone) => {
        // Simple phone regex for consistency with Android app logic
        const re = /^\+?[1-9]\d{1,14}$/;
        return re.test(String(phone).replace(/\s+/g, ''));
    },

    password: (password) => {
        return password.length >= 6;
    },

    name: (name) => {
        return name.trim().length >= 2;
    },

    age: (age) => {
        const n = parseInt(age);
        return !isNaN(n) && n > 0 && n < 120;
    },

    otp: (otp) => {
        return /^\d{6}$/.test(otp);
    }
};

window.Validation = Validation;
