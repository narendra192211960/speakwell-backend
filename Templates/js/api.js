// Use the provided desktop IP address for the backend
const BASE_URL = 'http://180.235.121.253:8071';
window.BASE_URL = BASE_URL;

const API = {
    async post(endpoint, data = {}) {
        try {
            const response = await fetch(`${BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data),
            });
            if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`API Post Error (${endpoint}):`, error);
            throw error;
        }
    },

    getHeaders() {
        return {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        };
    },

    async get(endpoint) {
        try {
            const response = await fetch(`${BASE_URL}${endpoint}`, {
                method: 'GET',
                headers: this.getHeaders(),
                cache: 'no-cache'
            });
            if (!response.ok) throw new Error(`HTTP Error: ${response.status}`);
            return await response.json();
        } catch (error) {
            console.error(`API GET Error (${endpoint}):`, error);
            throw error;
        }
    },

    // Auth Endpoints
    login: (email, password) => API.post('login', { email, password }),
    signup: (name, email, phone, age, password) => API.post('signup', { name, email, phone_number: phone, age, password }),
    sendOtp: (email, purpose = 'signup') => API.post('send_otp', { email, purpose }),
    verifyOtp: (email, otp) => API.post('verify_otp', { email, otp }),
    forgotPassword: (email, newPassword) => API.post('forgot_password', { email, newPassword }),
    changePassword: (userId, oldPassword, newPassword) => API.post('change_password', { user_id: userId, old_password: oldPassword, new_password: newPassword }),

    // Profile Endpoints
    updateProfile: (userId, name, email, phone, age) => API.post('update_profile', { user_id: userId, name, email, phone_number: phone, age }),
    getProfile: (userId) => API.get(`get_profile/${userId}`),
    updatePhone: (userId, newPhone) => API.post('update_phone', { user_id: userId, new_phone: newPhone }),
    getNotificationPreferences: (userId) => API.get(`get_notification_preferences/${userId}`),
    updateNotificationPreferences: (userId, prefs) => API.post('update_notification_preferences', { user_id: userId, ...prefs }),

    // Practice & Progress
    getExercises: () => API.get('get_exercises'),
    getExerciseStats: (userId) => API.get(`get_exercise_stats/${userId}`),
    saveAttempt: (userId, sessionId, exerciseName, expected, actual, score, feedback) =>
        API.post('save_attempt', {
            user_id: userId,
            session_id: sessionId,
            exercise_name: exerciseName,
            expected_sentence: expected,
            recognized_text: actual,
            accuracy: score,
            feedback: feedback
        }),
    getProgress: (userId) => API.get(`get_progress/${userId}`),
    getAchievements: (userId) => API.get(`get_achievements/${userId}`),
    getSessionSummary: (sessionId) => API.get(`get_session_summary/${sessionId}`),

    // Scheduling
    getSchedules: (userId) => API.get(`get_schedules/${userId}`),
    saveSchedule: (userId, dateStr, timeStr) => {
        // Backend expects: date: "Feb 25, 2026", time: "11:00 AM"
        // Input: date: "YYYY-MM-DD", time: "HH:MM"
        const dt = new Date(`${dateStr}T${timeStr}`);
        const formattedDate = dt.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
        const formattedTime = dt.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: true });

        return API.post('save_schedule', {
            user_id: userId,
            scheduled_date: formattedDate,
            scheduled_time: formattedTime
        });
    },
    deleteSchedule: (scheduleId, userId) => API.post('delete_schedule', { id: scheduleId, user_id: userId }),

    // AI Chatbot
    chatWithGemini: (model, data) => {
        const url = `v1beta/models/${model}:generateContent`;
        return API.post(url, data);
    },

    // Profile Picture (Multipart handling)
    async uploadProfilePicture(userId, file) {
        const formData = new FormData();
        formData.append('user_id', userId);
        formData.append('image', file);

        try {
            const response = await fetch(`${BASE_URL}upload_profile_picture`, {
                method: 'POST',
                body: formData,
            });
            return await response.json();
        } catch (error) {
            console.error('API Upload Error:', error);
            throw error;
        }
    },

    async removeProfilePicture(userId) {
        return API.post('remove_profile_picture', { user_id: userId });
    }
};

window.API = API; // Make it globally accessible
