from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import json
import mysql.connector
from config import Config
import datetime
import requests
import urllib.parse
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import threading
import random

app = Flask(__name__)
CORS(app) # Enable CORS for all routes

# Ensure upload folder exists
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def get_db_connection():
    return mysql.connector.connect(
        host=Config.DB_HOST,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )

def is_valid_email(email):
    # Standard regex that strictly requires the .com extension
    general_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.com$'
    return re.match(general_regex, email) is not None


def is_valid_phone(phone):
    phone_regex = r'^[6-9]\d{9}$'
    return re.match(phone_regex, str(phone)) is not None

# In-memory OTP store. Format: { email: { 'otp': '123456', 'expiry': datetime_obj } }
otp_store = {}

@app.route('/send_otp', methods=['POST'])
def send_otp():
    try:
        data = request.get_json()
        email = data.get('email')
        purpose = data.get('purpose', 'signup')

        if not email:
            return jsonify({"status": "error", "message": "Email is required"}), 400

        if not is_valid_email(email):
            return jsonify({"status": "error", "message": "Invalid email format"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)
        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        user_exists = cursor.fetchone() is not None
        cursor.close()
        conn.close()

        if purpose == "forgot_password":
            if not user_exists:
                return jsonify({"status": "error", "message": "Email is not registered. Please sign up first."}), 200
        else: # signup
            if user_exists:
                return jsonify({"status": "error", "message": "Email already registered"}), 200

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        if purpose == "forgot_password":
            expiry_time = datetime.datetime.now() + datetime.timedelta(seconds=60)
            subject = "Reset Password OTP Verification"
            body = f"Your OTP for Reset Password is: {otp}\nThis OTP is valid for 60 seconds. Do not share this OTP with anyone.\n\n– AI Speech Rehabilitation Assistant"
        else: # signup
            expiry_time = datetime.datetime.now() + datetime.timedelta(minutes=5)
            subject = "Signup OTP Verification"
            body = f"Your OTP for Sign Up is: {otp}\nThis OTP is valid for 5 minutes. Do not share this OTP with anyone.\n\n– AI Speech Rehabilitation Assistant"
        
        otp_store[email] = {
            'otp': otp,
            'expiry': expiry_time
        }
        
        # Send email
        email_sent = send_email_notification(email, subject, body)
        if not email_sent:
             return jsonify({"status": "error", "message": "Failed to send OTP via email. Please check SMTP configuration."}), 500

        return jsonify({"status": "success", "message": "OTP sent successfully"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/verify_otp', methods=['POST'])
def verify_otp():
    try:
        data = request.get_json()
        email = data.get('email')
        otp = data.get('otp')

        if not all([email, otp]):
            return jsonify({"status": "error", "message": "Email and OTP are required"}), 400

        record = otp_store.get(email)
        if not record:
            return jsonify({"status": "error", "message": "No OTP found for this email. Please generate a new one."}), 400

        if datetime.datetime.now() > record['expiry']:
            # Clean up expired OTP
            del otp_store[email]
            return jsonify({"status": "error", "message": "OTP expired. Please request a new OTP."}), 400

        if record['otp'] == str(otp):
            # OTP verified successfully
            # Clean up OTP after use to prevent reuse
            del otp_store[email]
            return jsonify({"status": "success", "message": "OTP verified successfully"}), 200
        else:
            return jsonify({"status": "error", "message": "Incorrect OTP. Please try again."}), 400

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/signup', methods=['POST'])
def signup():
    try:
        data = request.get_json()

        name = data.get('name')
        email = data.get('email')
        phone = data.get('phone_number')
        age = data.get('age')
        password = data.get('password')

        if not all([name, email, phone, age, password]):
            return jsonify({
                "status": "error",
                "message": "All fields are required"
            }), 400

        if not is_valid_email(email):
            return jsonify({
                "status": "error",
                "message": "Invalid email format. Please enter a valid email address"
            }), 400

        if not is_valid_phone(phone):
            return jsonify({
                "status": "error",
                "message": "Invalid phone number. Must be 10 digits starting with 6-9"
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)

        # ✅ check duplicate email
        cursor.execute("SELECT id FROM users WHERE email=%s", (email,))
        if cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "Email already registered"
            }), 409

        # ✅ check duplicate phone
        cursor.execute("SELECT id FROM users WHERE phone_number=%s", (phone,))
        if cursor.fetchone():
            return jsonify({
                "status": "error",
                "message": "The phone number already registered, use a new phone number"
            }), 409

        # Hashing password before storage
        hashed_password = generate_password_hash(password)

        query = """
        INSERT INTO users (name, email, phone_number, age, password)
        VALUES (%s, %s, %s, %s, %s)
        """
        values = (name, email, phone, age, hashed_password)

        cursor.execute(query, values)
        conn.commit()

        # Get the new user's ID and create default notification preferences (all OFF for new users)
        new_user_id = cursor.lastrowid
        try:
            cursor.execute("""
                INSERT IGNORE INTO notification_preferences
                    (user_id, daily_practice_reminder, streak_milestone, weekly_progress)
                VALUES (%s, FALSE, FALSE, FALSE)
            """, (new_user_id,))
            conn.commit()
        except Exception as pref_err:
            print(f"Warning: Could not create default notification preferences: {pref_err}")

        cursor.close()
        conn.close()

        # Send welcome email
        try:
            subject = "Welcome to SpeakWell!"
            body = f"Hello {name},\n\nWelcome to SpeakWell! Your account has been successfully created.\n\n– AI Speech Rehabilitation Assistant"
            send_email_notification(email, subject, body)
        except Exception as email_err:
            print(f"Failed to send welcome email: {email_err}")

        return jsonify({
            "status": "success",
            "message": "Signup successful",
            "user": {
                "name": name,
                "email": email,
                "phone": phone,
                "age": age
            }
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

@app.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()

        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({
                "status": "error",
                "message": "Email and password required"
            }), 200

        if not is_valid_email(email):
             return jsonify({
                "status": "error",
                "message": "Invalid email format. Please enter a valid email address"
            }), 200

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT id, name, email, phone_number, age, password, profile_picture
            FROM users
            WHERE email=%s
        """, (email,))

        user = cursor.fetchone()

        cursor.close()
        conn.close()

        # ✅ user not found
        if not user:
            return jsonify({
                "status": "error",
                "message": "User not found"
            }), 200

        # ✅ verify hash
        # Handle both hashed (different algorithms) and legacy plaintext
        stored_password = user["password"]
        is_correct = False
        
        try:
            # check_password_hash handles algorithm identification automatically
            is_correct = check_password_hash(stored_password, password)
        except Exception:
            # If stored_password is not a valid hash, check_password_hash might throw
            is_correct = False

        if not is_correct:
            # Fallback for legacy plain text accounts
            is_correct = (stored_password == password)

        if not is_correct:
            return jsonify({
                "status": "error",
                "message": "Invalid password"
            }), 200

        # ✅ success
        return jsonify({
            "status": "success",
            "message": "Login successful",
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "phone": user["phone_number"],
                "age": user["age"],
                "profile_picture": user["profile_picture"]
            }
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 200

@app.route('/uploads/<path:filename>')
def custom_static(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)

@app.route('/upload_profile_picture', methods=['POST'])
def upload_profile_picture():
    try:
        if 'image' not in request.files:
            return jsonify({"status": "error", "message": "No file part"}), 400
        file = request.files['image']
        user_id = request.form.get('user_id')
        if file.filename == '' or not user_id:
            return jsonify({"status": "error", "message": "No selected file or missing user_id"}), 400
            
        filename = secure_filename(f"user_{user_id}_{file.filename}")
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # update database
        server_ip = Config.FLASK_HOST if Config.FLASK_HOST != "0.0.0.0" else "10.73.250.173"
        image_url = f"http://{server_ip}:{Config.FLASK_PORT}/uploads/{filename}"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET profile_picture=%s WHERE id=%s", (image_url, user_id))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"status": "success", "profile_picture_url": image_url}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/remove_profile_picture', methods=['POST'])
def remove_profile_picture():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        
        if not user_id:
            return jsonify({"status": "error", "message": "Missing user_id"}), 400
            
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET profile_picture=NULL WHERE id=%s", (user_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({"status": "success", "message": "Profile picture removed successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_profile/<int:user_id>', methods=['GET'])
def get_profile(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, name, email, phone_number, age, profile_picture FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            return jsonify({"status": "success", "user": user}), 200
        else:
            return jsonify({"status": "error", "message": "User not found"}), 404
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/update_profile', methods=['POST'])
def update_profile():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        if user_id is not None:
            try:
                user_id = int(user_id)
            except (ValueError, TypeError):
                pass
        email = data.get('email')
        name = data.get('name')
        phone = data.get('phone_number')
        age = data.get('age')

        if not any([user_id, email]):
            return jsonify({"status": "error", "message": "User identifier required"}), 400

        if email and not is_valid_email(email):
             return jsonify({"status": "error", "message": "Invalid email format. Please enter a valid email address"}), 400
        
        if phone and not is_valid_phone(phone):
             return jsonify({"status": "error", "message": "Invalid phone number"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True, buffered=True)
        
        # 1. Check phone uniqueness if phone is provided
        if phone:
            phone = phone.strip()
            # Check across ALL users to ensure true uniqueness
            cursor.execute("SELECT id FROM users WHERE phone_number=%s", (phone,))
            
            existing_user = cursor.fetchone()
            if existing_user and (not user_id or existing_user['id'] != user_id):
                cursor.close()
                conn.close()
                return jsonify({"status": "error", "message": "Phone number already registered. Please use a different phone number."}), 400

        # 2. Update profile
        if user_id:
            query = "UPDATE users SET name=%s, phone_number=%s, age=%s WHERE id=%s"
            cursor.execute(query, (name, phone, age, user_id))
        else:
            query = "UPDATE users SET name=%s, phone_number=%s, age=%s WHERE email=%s"
            cursor.execute(query, (name, phone, age, email))
            
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"status": "success", "message": "Profile updated successfully"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/change_password', methods=['POST'])
def change_password():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        old_password = data.get('old_password')
        new_password = data.get('new_password')

        if not all([user_id, old_password, new_password]):
            return jsonify({"status": "error", "message": "Missing required fields"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT password FROM users WHERE id=%s", (user_id,))
        user = cursor.fetchone()

        if not user:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "User not found"}), 404

        stored_password = user["password"]
        
        # Verify old password (handle hash and legacy plain)
        try:
            is_valid = check_password_hash(stored_password, old_password)
        except Exception:
            is_valid = False

        if not is_valid:
            # Fallback for legacy plain text
            is_valid = (stored_password == old_password)

        if not is_valid:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "Incorrect old password"}), 200

        if old_password == new_password:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "New password cannot be same as old"}), 200

        hashed_new_password = generate_password_hash(new_password)
        cursor.execute("UPDATE users SET password=%s WHERE id=%s", (hashed_new_password, user_id))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"status": "success", "message": "Password updated successfully"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/update_phone', methods=['POST'])
def update_phone():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        new_phone = data.get('new_phone')

        if not all([user_id, new_phone]):
            return jsonify({"status": "error", "message": "Missing user_id or phone"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)

        # Check if phone already used by someone else
        new_phone = new_phone.strip()
        cursor.execute("SELECT id FROM users WHERE phone_number=%s", (new_phone,))
        existing_user = cursor.fetchone()
        
        if existing_user:
            # If it exists, check if it belongs to someone ELSE
            if existing_user[0] != user_id:
                cursor.close()
                conn.close()
                return jsonify({"status": "error", "message": "Phone number already registered. Please use a different phone number."}), 400
            else:
                # User is submitting their OWN number. 
                # According to requirement, if it exists in DB (even if it's theirs), we should return error?
                # User said: "Even if a phone number is already stored in the database, when the user enters the same phone number, the system shows 'Phone number updated successfully'. This is incorrect."
                # So if they enter their OWN current number, it should also say "Phone number already registered"? 
                # Actually, the user requirement says: "The system must first check the database to see if that phone number already exists for another user."
                # Wait, reread: "Even if a phone number is already stored in the database, when the user enters the same phone number, the system shows 'Phone number updated successfully'. This is incorrect."
                # And: "If the phone number already exists in the database: Do NOT update the phone number. Show an error message: 'Phone number already registered. Please use a different phone number.'"
                # So even if it's THEIR number, if they hit update, we show the error.
                cursor.close()
                conn.close()
                return jsonify({"status": "error", "message": "Phone number already registered. Please use a different phone number."}), 400

        cursor.execute("UPDATE users SET phone_number=%s WHERE id=%s", (new_phone, user_id))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({"status": "success", "message": "Phone number updated successfully"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/forgot_password', methods=['POST'])
def forgot_password():
    try:
        data = request.get_json()

        email = data.get('email')
        new_password = data.get('newPassword')

        if not email or not new_password:
            return jsonify({
                "status": "error",
                "message": "Email and new password required"
            }), 200

        if not is_valid_email(email):
             return jsonify({
                "status": "error",
                "message": "Invalid email format. Please enter a valid email address"
            }), 200

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT password FROM users WHERE email=%s", (email,))
        user = cursor.fetchone()

        if not user:
            cursor.close()
            conn.close()
            return jsonify({
                "status": "error",
                "message": "Email is not registered"
            }), 200

        stored_password = user["password"]
        
        # Check against existing hash or plain
        is_already_same = False
        try:
            is_already_same = check_password_hash(stored_password, new_password)
        except Exception:
            is_already_same = False
            
        if not is_already_same:
            is_already_same = (stored_password == new_password)

        if is_already_same:
            cursor.close()
            conn.close()
            return jsonify({"status": "error", "message": "Please create a different password"}), 200

        hashed_new_password = generate_password_hash(new_password)
        cursor.execute("UPDATE users SET password=%s WHERE email=%s", (hashed_new_password, email))
        conn.commit()

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "message": "Password updated successfully"
        }), 200

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500

def send_email_notification(to_email, subject, body):
    """
    Sends an email notification using SMTP.
    Returns True if successful, False otherwise.
    """
    try:
        if Config.SMTP_USER == "your_email@gmail.com":
            print("Email Notification skipped: SMTP credentials not configured.")
            return False

        msg = MIMEMultipart()
        msg['From'] = Config.SMTP_USER
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(Config.SMTP_HOST, Config.SMTP_PORT)
        server.starttls()
        server.login(Config.SMTP_USER, Config.SMTP_APP_PASSWORD)
        text = msg.as_string()
        server.sendmail(Config.SMTP_USER, to_email, text)
        server.quit()

        print(f"Email sent successfully to: {to_email}")
        return True
            
    except Exception as e:
        print(f"Email sending failed (SMTP Exception): {str(e)}")
        return False


@app.route('/save_schedule', methods=['POST'])
def save_schedule():
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "Invalid JSON data."
            }), 400

        user_id = data.get('user_id')
        date_str = data.get('scheduled_date')   # Format: "Feb 25, 2026"
        time_str = data.get('scheduled_time')   # Format: "11:00 AM"

        # ✅ Validate required fields
        if not user_id or not date_str or not time_str:
            return jsonify({
                "status": "error",
                "message": "Please provide user_id, scheduled_date and scheduled_time."
            }), 400

        # ✅ Parse and validate datetime
        try:
            scheduled_dt = datetime.datetime.strptime(
                f"{date_str} {time_str}",
                "%b %d, %Y %I:%M %p"
            )
        except ValueError:
            return jsonify({
                "status": "error",
                "message": "Invalid date or time format. Use 'Feb 25, 2026' and '11:00 AM'."
            }), 400

        # ✅ Check past date/time
        if scheduled_dt <= datetime.datetime.now():
            return jsonify({
                "status": "error",
                "message": "You cannot schedule a session in the past."
            }), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # ✅ Check if user exists
        cursor.execute(
            "SELECT id, name, phone_number, email FROM users WHERE id = %s",
            (user_id,)
        )
        user = cursor.fetchone()

        if not user:
            cursor.close()
            conn.close()
            return jsonify({
                "status": "error",
                "message": "User not found."
            }), 404

        # ✅ Check duplicate schedule
        cursor.execute("""
            SELECT id FROM schedules
            WHERE user_id = %s
            AND scheduled_date = %s
            AND scheduled_time = %s
        """, (user_id, date_str, time_str))

        if cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({
                "status": "error",
                "message": "This session is already scheduled please select different session"
            }), 409

        # ✅ Insert schedule
        insert_query = """
            INSERT INTO schedules (user_id, scheduled_date, scheduled_time)
            VALUES (%s, %s, %s)
        """
        cursor.execute(insert_query, (user_id, date_str, time_str))
        conn.commit()

        cursor.close()
        conn.close()

        # ✅ Send Email (instead of SMS)
        email_success = False
        try:
            if user and user['email']:
                to_email = user['email']
                subject = "Practice Session Scheduled"
                body = f"Hello {user['name']},\n\nYour practice session has been scheduled for {date_str} at {time_str}. Please be ready for your rehabilitation session.\n\n– AI Speech Rehabilitation Assistant"
                
                print(f"DEBUG [save_schedule]: Attempting to send schedule email to {to_email}...")
                email_success = send_email_notification(to_email, subject, body)
                print(f"DEBUG [save_schedule]: Email notification result: {email_success}")
            else:
                print(f"DEBUG [save_schedule]: No email found for user {user_id}.")
        except Exception as email_error:
            print(f"ERROR [save_schedule] Email Exception: {email_error}")

        # ✅ Final Response
        return jsonify({
            "status": "success",
            "message": "Your practice session has been scheduled successfully.",
            "email_sent": email_success,
            "scheduled_datetime": scheduled_dt.strftime("%Y-%m-%d %H:%M:%S")
        }), 201

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": "Something went wrong.",
            "details": str(e)
        }), 500

@app.route('/get_schedules/<int:user_id>', methods=['GET'])
def get_schedules(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Clean up expired schedules
        cursor.execute("SELECT id, scheduled_date, scheduled_time FROM schedules WHERE user_id = %s", (user_id,))
        all_schedules = cursor.fetchall()
        
        now = datetime.datetime.now()
        ids_to_delete = []
        
        for s in all_schedules:
            try:
                date_str = s['scheduled_date']
                time_str = s['scheduled_time']
                # Correct format: "Feb 25, 2026 11:00 AM"
                scheduled_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%b %d, %Y %I:%M %p")
                
                if scheduled_dt < now:
                    ids_to_delete.append(s['id'])
            except Exception as parse_error:
                print(f"Cleanup Parse Error for ID {s['id']}: {parse_error}")
                continue
                
        if ids_to_delete:
            format_strings = ','.join(['%s'] * len(ids_to_delete))
            cursor.execute(f"DELETE FROM schedules WHERE id IN ({format_strings})", tuple(ids_to_delete))
            conn.commit()
            print(f"Automatically deleted {len(ids_to_delete)} expired schedules for user {user_id}")

        # 2. Fetch remaining future schedules
        cursor.execute("""
            SELECT id, scheduled_date as date, scheduled_time as time, created_at
            FROM schedules
            WHERE user_id = %s
            ORDER BY id ASC
        """, (user_id,))
        
        schedules = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "schedules": schedules
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/delete_schedule', methods=['POST'])
def delete_schedule():
    try:
        data = request.get_json()
        schedule_id = data.get('id')
        user_id = data.get('user_id')

        if not schedule_id or not user_id:
            return jsonify({"status": "error", "message": "ID and User ID required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM schedules WHERE id = %s AND user_id = %s", (schedule_id, user_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({"status": "success", "message": "Session cancelled"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_exercise_stats/<int:user_id>', methods=['GET'])
def get_exercise_stats(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Calculate summary for each exercise type
        query = """
        SELECT 
            exercise_name,
            AVG(accuracy) as avg_accuracy, 
            COUNT(DISTINCT expected_sentence) as words_practiced 
        FROM practice_attempts 
        WHERE user_id = %s 
        AND recognized_text NOT LIKE 'No speech detected%%' 
        AND recognized_text != ''
        GROUP BY exercise_name
        """
        cursor.execute(query, (user_id,))
        results = cursor.fetchall()
        
        # Convert to a format easy for the app to consume
        # e.g., a map/object of category_name -> {avg_accuracy, words_practiced}
        stats = {}
        for row in results:
            stats[row['exercise_name']] = {
                "avg_accuracy": int(row['avg_accuracy']) if row['avg_accuracy'] is not None else 0,
                "words_practiced": row['words_practiced']
            }
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "exercise_stats": stats
        }), 200
        
    except Exception as e:
        print(f"ERROR in get_exercise_stats: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/save_attempt', methods=['POST'])
def save_attempt():
    try:
        data = request.get_json()
        print(f"DEBUG: Received save_attempt data: {data}")
        
        user_id = data.get('user_id')
        session_id = data.get('session_id', 'legacy_session')
        exercise_name = data.get('exercise_name', 'General Practice')
        expected_sentence = data.get('expected_sentence')
        recognized_text = data.get('recognized_text')
        accuracy = data.get('accuracy')
        feedback = data.get('feedback', data.get('feedback_tip'))
        
        if user_id is None:
            return jsonify({"status": "error", "message": "User ID is required"}), 400

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Update start_date if it's the user's first session
        cursor.execute("SELECT start_date FROM users WHERE id = %s", (user_id,))
        user_row = cursor.fetchone()
        print(f"DEBUG [save_attempt]: Checking start_date for user {user_id}. Current row: {user_row}")
        
        if user_row and user_row['start_date'] is None:
            today_date = datetime.date.today()
            print(f"DEBUG [save_attempt]: User {user_id} has no start_date. Setting to {today_date}")
            cursor.execute("UPDATE users SET start_date = %s WHERE id = %s", (today_date, user_id))
            conn.commit() # Ensure immediate persistence
            print(f"DEBUG [save_attempt]: COMMIT successful for start_date.")
        else:
            current_sd = user_row['start_date'] if user_row else 'USER_NOT_FOUND'
            print(f"DEBUG [save_attempt]: User {user_id} already has start_date: {current_sd}")

        # 2. Insert the practice attempt
        # Mapping to user requested fields: feedback and date_time
        date_time = data.get('date_time')
        
        if not date_time:
            date_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        query = """
        INSERT INTO practice_attempts (user_id, session_id, exercise_name, expected_sentence, recognized_text, accuracy, feedback, feedback_tip, date_time)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        values = (user_id, session_id, exercise_name, expected_sentence, recognized_text, accuracy, feedback, feedback, date_time)
        
        cursor.execute(query, values)
        conn.commit()
        print(f"DEBUG: Successfully inserted attempt for user {user_id}")
        
        # 3. Calculate overall progress
        cursor.execute("SELECT AVG(accuracy) as avg_accuracy FROM practice_attempts WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        overall_progress = int(result['avg_accuracy']) if result and result['avg_accuracy'] is not None else 0

        # 4. Calculate current streak (consecutive active days up to today)
        streak = _get_current_streak(user_id, cursor)

        # 5. Fetch user data for instant streak email notification
        cursor.execute("""
            SELECT u.email, u.name, np.streak_milestone
            FROM users u
            LEFT JOIN notification_preferences np ON u.id = np.user_id
            WHERE u.id = %s
        """, (user_id,))
        user_info = cursor.fetchone()

        cursor.close()
        conn.close()

        # Instant email notification for streak milestone is removed as it's now handled via Android local notifications
        
        return jsonify({
            "status": "success", 
            "message": "Attempt saved successfully", 
            "overall_progress": overall_progress,
            "current_streak": streak
        }), 201
        
    except Exception as e:
        print(f"ERROR in save_attempt: {str(e)}") 
        return jsonify({"status": "error", "message": str(e)}), 500



@app.route('/get_session_summary/<session_id>', methods=['GET'])
def get_session_summary(session_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # Calculate summary for the session
        # Only count attempts with recognized speech (exclude "No speech detected" or empty)
        query = """
        SELECT 
            AVG(accuracy) as avg_accuracy, 
            COUNT(*) as words_practiced 
        FROM practice_attempts 
        WHERE session_id = %s 
        AND recognized_text NOT LIKE 'No speech detected%%' 
        AND recognized_text != ''
        """
        cursor.execute(query, (session_id,))
        result = cursor.fetchone()
        
        avg_accuracy = float(result['avg_accuracy']) if result and result['avg_accuracy'] is not None else 0.0
        words_practiced = int(result['words_practiced']) if result and result['words_practiced'] else 0
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "avg_accuracy": round(avg_accuracy, 2),
            "words_practiced": words_practiced
        }), 200
        
    except Exception as e:
        print(f"ERROR in get_session_summary: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_progress/<int:user_id>', methods=['GET'])
def get_progress(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        
        # 1. Basic Stats
        cursor.execute("SELECT start_date FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        start_date = user['start_date'] if user else None

        cursor.execute("""
            SELECT 
                COUNT(*) as total_attempts,
                (SELECT COUNT(DISTINCT session_id) FROM practice_attempts WHERE user_id = %s) as completed_sessions,
                (SELECT COUNT(*) FROM practice_attempts 
                 WHERE user_id = %s AND recognized_text NOT LIKE 'No speech detected%' AND recognized_text != '') as total_words_practiced,
                AVG(accuracy) as overall_accuracy
            FROM practice_attempts 
            WHERE user_id = %s
        """, (user_id, user_id, user_id))
        
        stats = cursor.fetchone()
        completed_sessions = stats['completed_sessions'] if stats and stats['completed_sessions'] else 0
        total_words_practiced = stats['total_words_practiced'] if stats and stats['total_words_practiced'] else 0
        overall_accuracy = int(stats['overall_accuracy']) if stats and stats['overall_accuracy'] is not None else 0
        
        # 2. Days Active
        days_active = 0
        if start_date:
            today = datetime.date.today()
            days_active = (today - start_date).days + 1
        
        # 3. Daily Accuracy (Last 7 active days)
        cursor.execute("""
            SELECT 
                DATE(date_time) as practice_date,
                AVG(accuracy) as accuracy,
                DATE_FORMAT(date_time, '%a') as day_name
            FROM practice_attempts
            WHERE user_id = %s
            GROUP BY DATE(date_time)
            ORDER BY practice_date DESC
            LIMIT 7
        """, (user_id,))
        
        daily_accuracy = []
        # Reverse to show most recent days at the end of the history if desired, 
        # but populateDailyHistory in App iterates normally.
        # Let's keep it DESC as it was slightly before but now grouped by date.
        for row in cursor.fetchall():
            daily_accuracy.append({
                "date": str(row['practice_date']),
                "day_name": row['day_name'],
                "accuracy": int(row['accuracy'])
            })
        
        # 4. Fetch true streak
        real_streak = _get_current_streak(user_id, cursor)
        
        cursor.close()
        conn.close()
        
        return jsonify({
            "status": "success",
            "progress_percentage": overall_accuracy,
            "completed_sessions": completed_sessions,
            "total_words_practiced": total_words_practiced,
            "overall_accuracy": overall_accuracy,
            "days_active": days_active,
            "daily_accuracy": daily_accuracy,
            "current_streak": real_streak
        }), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# ============================================================
# SMS NOTIFICATION SYSTEM
# ============================================================

def _format_phone(raw_phone):
    """Normalize phone number to E.164 format for India (+91XXXXXXXXXX)."""
    if not raw_phone:
        return None
    raw_phone = str(raw_phone).strip()
    
    # Remove any non-digit characters except +
    clean_phone = re.sub(r'[^\d+]', '', raw_phone)
    
    if clean_phone.startswith("+"):
        if clean_phone.startswith("+91") and len(clean_phone) == 13:
            return clean_phone
        # If it's + and 10 digits, assume India
        if len(clean_phone) == 11:
            return "+91" + clean_phone[1:]
        return clean_phone
        
    if clean_phone.startswith("91") and len(clean_phone) == 12:
        return "+" + clean_phone
        
    if len(clean_phone) == 10:
        return "+91" + clean_phone
        
    return clean_phone # Fallback


def _already_sent_today(cursor, user_id, notification_type):
    """Returns True if this user already got this notification type today."""
    cursor.execute("""
        SELECT id FROM notification_logs
        WHERE user_id = %s AND type = %s
        AND DATE(sent_at) = CURDATE()
        LIMIT 1
    """, (user_id, notification_type))
    return cursor.fetchone() is not None


def _already_sent_this_week(cursor, user_id, notification_type):
    """Returns True if this user already got this notification type in the last 7 days."""
    cursor.execute("""
        SELECT id FROM notification_logs
        WHERE user_id = %s AND type = %s
        AND sent_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        LIMIT 1
    """, (user_id, notification_type))
    return cursor.fetchone() is not None


def _send_email(to_email, subject, message, user_id, notification_type):
    """
    Send raw email via SMTP and log to notification_logs.
    Returns (success, error_msg).
    """
    if not to_email:
        print(f"[Email] FAILED — No email for user {user_id}")
        return False, "No email address"

    try:
        print(f"[Email] Attempting to send email to {to_email}: '{message}'")
        success = send_email_notification(to_email, subject, message)
        
        if success:
            print(f"[Email] SUCCESS — To: {to_email}")
            # Log success
            _log_notification(user_id, notification_type, message, 'sent')
            return True, "Success"
        else:
            print(f"[Email] FAILED — To: {to_email} | Error: SMTP Sending Failed")
            _log_notification(user_id, notification_type, message, 'failed')
            return False, "SMTP Sending Failed"
    except Exception as e:
        print(f"[Email] FAILED — To: {to_email} | Error: {e}")
        # Log failure
        _log_notification(user_id, notification_type, message, 'failed')
        return False, str(e)


def _log_notification(user_id, notification_type, message, status='sent'):
    """Insert a record into notification_logs with status."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO notification_logs (user_id, type, message, status) VALUES (%s, %s, %s, %s)",
            (user_id, notification_type, message, status)
        )
        conn.commit()
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error logging notification: {e}")





# ------------------------------------------------------------
# SCHEDULED JOB 2: Weekly Progress Summary (daily check at 09:00 AM)
# ------------------------------------------------------------
def job_weekly_progress():
    """Send weekly average accuracy SMS to users who have it enabled and have completed 7-day cycles."""
    print("[Scheduler] Running weekly progress summary job...")
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        today = datetime.date.today()

        # Fetch all users with weekly_progress = TRUE and a valid created_at
        cursor.execute("""
            SELECT np.user_id, u.email, u.created_at
            FROM notification_preferences np
            JOIN users u ON u.id = np.user_id
            WHERE np.weekly_progress = TRUE
              AND u.email IS NOT NULL
        """)
        users = cursor.fetchall()

        for user in users:
            user_id = user['user_id']
            email_address = user['email']
            created_at = user['created_at']

            if not created_at:
                continue

            registration_date = created_at.date() if hasattr(created_at, 'date') else created_at
            days_since_reg = (today - registration_date).days

            # Only send on 7-day multiples (day 7, 14, 21, ...)
            if days_since_reg == 0 or days_since_reg % 7 != 0:
                continue

            # Duplicate check: not sent in the last 7 days
            if _already_sent_this_week(cursor, user_id, 'weekly_progress'):
                print(f"[Scheduler] Weekly summary already sent this week to user {user_id}, skipping.")
                continue

            # Calculate average accuracy from practice_attempts over the last 7 days (average of daily averages)
            cursor.execute("""
                SELECT AVG(daily_avg) as avg_acc, COUNT(*) as practice_days
                FROM (
                    SELECT AVG(accuracy) as daily_avg
                    FROM practice_attempts
                    WHERE user_id = %s
                      AND date_time >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                    GROUP BY DATE(date_time)
                ) as daily_stats
            """, (user_id,))
            result = cursor.fetchone()
            avg_acc = int(result['avg_acc']) if result and result['avg_acc'] else 0
            practice_days = result['practice_days'] if result else 0

            # Skip if user had no activity this week
            if practice_days == 0:
                print(f"[Scheduler] No practice activity this week for user {user_id}, skipping.")
                continue

            subject = "Weekly Progress Summary"
            message = f"you got {avg_acc}% average accuracy in a week so practice consistently"
            _send_email(email_address, subject, message, user_id, 'weekly_progress')

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"[Scheduler] Error in job_weekly_progress: {e}")


# ------------------------------------------------------------
# STREAK LOGIC
# ------------------------------------------------------------
def _get_current_streak(user_id, cursor):
    """Calculates and returns the user's current consecutive practice day streak."""
    cursor.execute("""
        SELECT DISTINCT DATE(date_time) as practice_date
        FROM practice_attempts
        WHERE user_id = %s AND date_time IS NOT NULL
        ORDER BY practice_date DESC
    """, (user_id,))
    dates = [row['practice_date'] for row in cursor.fetchall()]

    streak = 0
    if dates:
        check_date = datetime.date.today()
        for d in dates:
            practice_day = d if isinstance(d, datetime.date) else d.date()
            if practice_day == check_date or practice_day == check_date - datetime.timedelta(days=1):
                streak += 1
                check_date = practice_day - datetime.timedelta(days=1)
            else:
                break
    return streak




# ------------------------------------------------------------
# PREFERENCE ENDPOINTS
# ------------------------------------------------------------

@app.route('/get_notification_preferences/<int:user_id>', methods=['GET'])
def get_notification_preferences(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT * FROM notification_preferences WHERE user_id = %s", (user_id,))
        prefs = cursor.fetchone()

        if not prefs:
            # Create default ALL-FALSE row (new user condition)
            cursor.execute("""
                INSERT INTO notification_preferences
                    (user_id, daily_practice_reminder, streak_milestone, weekly_progress)
                VALUES (%s, FALSE, FALSE, FALSE)
            """, (user_id,))
            conn.commit()
            cursor.execute("SELECT * FROM notification_preferences WHERE user_id = %s", (user_id,))
            prefs = cursor.fetchone()

        cursor.close()
        conn.close()

        # Convert integers (1/0) to JSON-friendly booleans (true/false)
        for field in ['daily_practice_reminder', 'streak_milestone', 'weekly_progress']:
            if field in prefs:
                prefs[field] = bool(prefs[field])

        prefs.pop('id', None)
        prefs.pop('updated_at', None)

        return jsonify({"status": "success", "preferences": prefs}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/get_achievements/<int:user_id>', methods=['GET'])
def get_achievements(user_id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # 1. First Session Date (First Steps)
        cursor.execute("""
            SELECT MIN(date_time) as first_session 
            FROM practice_attempts 
            WHERE user_id = %s
        """, (user_id,))
        first_session = cursor.fetchone()['first_session']
        
        # 2. Current Streak (Dedicated Learner)
        current_streak = _get_current_streak(user_id, cursor)

        # 3. Max Accuracy (Master Pronunciation)
        cursor.execute("""
            SELECT MAX(accuracy) as max_accuracy 
            FROM practice_attempts 
            WHERE user_id = %s
        """, (user_id,))
        max_accuracy = cursor.fetchone()['max_accuracy'] or 0

        # 4. Total Words (Word Champion)
        cursor.execute("""
            SELECT COUNT(*) as total_words 
            FROM practice_attempts 
            WHERE user_id = %s 
            AND recognized_text IS NOT NULL 
            AND recognized_text != '' 
            AND recognized_text NOT LIKE 'No speech detected%'
        """, (user_id,))
        total_words = cursor.fetchone()['total_words'] or 0

        # 5. Total Sessions (Consistency King)
        cursor.execute("""
            SELECT COUNT(DISTINCT session_id) as total_sessions 
            FROM practice_attempts 
            WHERE user_id = %s
        """, (user_id,))
        total_sessions = cursor.fetchone()['total_sessions'] or 0

        # 6. Perfect Score Progress (Perfect Score)
        # Check if user ever got 100%
        cursor.execute("""
            SELECT id FROM practice_attempts 
            WHERE user_id = %s AND accuracy = 100 
            LIMIT 1
        """, (user_id,))
        has_perfect = cursor.fetchone() is not None

        cursor.close()
        conn.close()

        return jsonify({
            "status": "success",
            "achievements": {
                "first_session_date": first_session.strftime("%b %d, %Y") if first_session else None,
                "current_streak": current_streak,
                "max_accuracy": max_accuracy,
                "total_words": total_words,
                "total_sessions": total_sessions,
                "has_perfect_score": has_perfect
            }
        }), 200
    except Exception as e:
        print(f"Error in get_achievements: {e}")
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/update_notification_preferences', methods=['POST'])
def update_notification_preferences():
    try:
        data = request.get_json()
        user_id = data.get('user_id')

        if not user_id:
            return jsonify({"status": "error", "message": "user_id is required"}), 400

        print(f"[Preferences] Received update for user {user_id}: {data}")

        allowed_fields = ['daily_practice_reminder', 'streak_milestone', 'weekly_progress']
        updates = {k: bool(data[k]) for k in allowed_fields if k in data and data[k] is not None}

        if not updates:
            return jsonify({"status": "error", "message": "No valid fields to update"}), 400

        set_clause = ", ".join([f"`{k}` = %s" for k in updates.keys()])
        values = list(updates.values()) + [user_id]

        conn = get_db_connection()
        cursor = conn.cursor()

        # Ensure row exists (new user safe)
        cursor.execute(
            "INSERT IGNORE INTO notification_preferences (user_id) VALUES (%s)", (user_id,)
        )
        cursor.execute(
            f"UPDATE notification_preferences SET {set_clause} WHERE user_id = %s",
            tuple(values)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({"status": "success", "message": "Preferences updated"}), 200
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


@app.route('/log_streak_milestone', methods=['POST'])
def log_streak_milestone():
    try:
        data = request.get_json()
        user_id = data.get('user_id')
        streak_count = data.get('streak_count')

        if not user_id or not streak_count:
            return jsonify({"status": "error", "message": "user_id and streak_count required"}), 400

        # Deduplicate: skip if this exact streak milestone was already logged
        conn = get_db_connection()
        cursor = conn.cursor(buffered=True)
        cursor.execute(
            "SELECT id FROM notification_logs WHERE user_id=%s AND type='streak_milestone' AND message LIKE %s LIMIT 1",
            (user_id, f"%{streak_count}-day%")
        )
        already_logged = cursor.fetchone()
        cursor.close()
        conn.close()

        if already_logged:
            return jsonify({"status": "skipped", "message": "Already logged"}), 200

        # Log the streak milestone notification
        _log_notification(user_id, 'streak_milestone',
                          f"🎉 {streak_count}-day streak reached!", 'sent')

        return jsonify({"status": "success", "message": "Streak milestone logged"}), 201

    except Exception as e:
        print(f"ERROR in log_streak_milestone: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500


def create_tables():

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Create users table if not exists (already exist but for completeness)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            phone_number VARCHAR(20),
            age VARCHAR(10),
            password VARCHAR(255) NOT NULL,
            profile_picture VARCHAR(500) DEFAULT NULL,
            start_date DATE DEFAULT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # Add start_date column if it doesn't exist (for existing users)
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN start_date DATE DEFAULT NULL")
            conn.commit()
        except:
            pass # Column already exists
            
        # Add profile_picture column if it doesn't exist (for existing users)
        try:
            cursor.execute("ALTER TABLE users ADD COLUMN profile_picture VARCHAR(500) DEFAULT NULL")
            conn.commit()
        except:
            pass # Column already exists
        
        # Create practice_attempts table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS practice_attempts (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            session_id VARCHAR(100) DEFAULT 'legacy_session',
            exercise_name VARCHAR(100) DEFAULT 'General Practice',
            expected_sentence TEXT,
            recognized_text TEXT,
            accuracy INT,
            feedback TEXT,
            date_time DATETIME,
            feedback_tip TEXT,
            attempt_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        # Ensure new columns exist for existing installations
        try:
            cursor.execute("ALTER TABLE practice_attempts ADD COLUMN session_id VARCHAR(100) DEFAULT 'legacy_session'")
        except: pass
        try:
            cursor.execute("ALTER TABLE practice_attempts ADD COLUMN exercise_name VARCHAR(100) DEFAULT 'General Practice'")
        except: pass
        try:
            cursor.execute("ALTER TABLE practice_attempts ADD COLUMN feedback TEXT")
        except: pass
        try:
            cursor.execute("ALTER TABLE practice_attempts ADD COLUMN feedback_tip TEXT")
        except: pass
        try:
            cursor.execute("ALTER TABLE practice_attempts ADD COLUMN date_time DATETIME")
        except: pass
        conn.commit()

        # Create schedules table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            scheduled_date VARCHAR(50),
            scheduled_time VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        
        # Create/update notification_preferences table (new spec columns)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notification_preferences (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL UNIQUE,
            daily_practice_reminder BOOLEAN DEFAULT FALSE,
            streak_milestone BOOLEAN DEFAULT FALSE,
            weekly_progress BOOLEAN DEFAULT FALSE,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)

        # Migrate old columns if they exist (idempotent)
        for old_col, new_col in [
            ('daily_reminder', 'daily_practice_reminder'),
            ('streak_alerts', 'streak_milestone'),
            ('weekly_summary', 'weekly_progress')
        ]:
            try:
                cursor.execute(f"ALTER TABLE notification_preferences CHANGE `{old_col}` `{new_col}` BOOLEAN DEFAULT FALSE")
            except: pass
        # Drop old extra columns if they exist
        for drop_col in ['badge_notifications', 'progress_notifications', 'accuracy_notifications']:
            try:
                cursor.execute(f"ALTER TABLE notification_preferences DROP COLUMN `{drop_col}`")
            except: pass

        # Create notification_logs table (aligned with CORE REQUIREMENTS)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notification_logs (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            type VARCHAR(100),
            message TEXT,
            status VARCHAR(20) DEFAULT 'sent',
            sent_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
        """)
        # Ensure 'type' column exists if 'notification_type' was used before
        try:
            cursor.execute("ALTER TABLE notification_logs CHANGE `notification_type` `type` VARCHAR(100)")
        except: pass
        # Add status column if missing
        try:
            cursor.execute("ALTER TABLE notification_logs ADD COLUMN status VARCHAR(20) DEFAULT 'sent'")
        except: pass
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database tables ensured.")
    except Exception as e:
        print(f"Error creating tables: {e}")

@app.route('/<version>/models/<model>:generateContent', methods=['POST'])
def proxy_gemini(version, model):
    try:
        print(f"[Proxy] Incoming request for version: {version}, model: {model}")
        print(f"[Proxy] Config.GEMINI_API_KEYS length: {len(Config.GEMINI_API_KEYS)}")
        
        api_keys = Config.GEMINI_API_KEYS
        if not api_keys or not api_keys[0]:
            print("[Proxy] ERROR: No API keys configured in environment.")
            return jsonify({"status": "error", "message": "Backend API Keys not configured"}), 500
            
        last_error = "Unknown error"
        for api_key in api_keys:
            if not api_key: continue
            
            url = f"https://generativelanguage.googleapis.com/{version}/models/{model}:generateContent?key={api_key}"
            headers = {'Content-Type': 'application/json'}
            
            try:
                print(f"[Proxy] URL: {url.replace(api_key, 'REDACTED')}")
                print(f"[Proxy] Body: {json.dumps(request.json)[:100]}...") # Log first 100 chars
                
                response = requests.post(url, json=request.json, headers=headers, timeout=30)
                
                print(f"[Proxy] Google Response ({response.status_code}): {response.text[:200]}")
                
                if response.status_code == 429:
                    print(f"[Proxy] Rate limit hit for key ending in {api_key[-4:]}.")
                    last_error = response.json()
                    continue
                
                return jsonify(response.json()), response.status_code
            except Exception as e:
                print(f"[Proxy] Request exception: {str(e)}")
                last_error = str(e)
                continue
                
        print("[Proxy] ERROR: All keys exhausted or failed.")
        return jsonify({"status": "error", "message": "All API keys exhausted or failed.", "details": last_error}), 429
        
    except Exception as e:
        print(f"[Proxy] CRITICAL ERROR: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/debug_config', methods=['GET'])
def debug_config():
    """Hidden route to troubleshoot configuration issues."""
    env_keys_raw = os.environ.get("GEMINI_API_KEYS", "NOT_SET")
    config_keys = Config.GEMINI_API_KEYS
    
    debug_info = {
        "config_gemini_keys_count": len(config_keys),
        "env_gemini_keys_raw_length": len(env_keys_raw) if env_keys_raw != "NOT_SET" else 0,
        "env_gemini_keys_present": env_keys_raw != "NOT_SET",
        "working_directory": os.getcwd(),
        "backend_directory": os.path.dirname(os.path.abspath(__file__)),
        "env_file_path": os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'),
        "env_file_exists": os.path.exists(os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')),
        "db_host": Config.DB_HOST,
        "python_version": os.sys.version
    }
    
    # Check for .env file contents (safety check, only size and existence)
    if debug_info["env_file_exists"]:
        debug_info["env_file_size"] = os.path.getsize(debug_info["env_file_path"])
        
    return jsonify(debug_info)

@app.route('/get_exercises', methods=['GET'])
def get_exercises():
    try:
        exercises = {
            "Basic Vowel Sounds": ["eat eat eat", "it it it", "ice ice ice", "at at at", "hot hot hot", "out out out", "boot boot boot", "but but but"],
            "Simple Words - Daily Life": ["hello hello hello", "thank you thank you thank you", "water water water", "food food food", "help help help", "yes yes yes", "no no no", "please please please", "home home home", "sorry sorry sorry", "doctor doctor doctor", "phone phone phone", "money money money", "friend friend friend", "family family family"],
            "Numbers 1-10": ["One One One", "Two Two Two", "Three Three Three", "Four Four Four", "Five Five Five", "Six Six Six", "Seven Seven Seven", "Eight Eight Eight", "Nine Nine Nine", "Ten Ten Ten"],
            "R and L Sounds": ["Red Red Red", "Led Led Led", "Right Right Right", "Light Light Light", "Road Road Road", "Load Load Load", "Pray Pray Pray", "Play Play Play", "Rice Rice Rice", "Lice Lice Lice", "Read Read Read", "Lead Lead Lead"],
            "Short Sentences": [
                "How are you today?",
                "I am feeling well.",
                "The weather is nice.",
                "Thank you very much.",
                "Please open the door.",
                "I will try again.",
                "This is very good.",
                "Can you help me?"
            ],
            "TH Sound Practice": ["the the the", "this this this", "that that that", "three three three", "think think think", "thank thank thank", "mother mother mother", "father father father"],
            "Complex Sentences": [
                "I would like to schedule an appointment.",
                "Could you please help me with this?",
                "The rehabilitation program is very helpful.",
                "I have been practicing every single day.",
                "I am trying to improve my speech step by step.",
                "The doctor advised me to practice slowly and clearly.",
                "Recording my voice helps me understand my mistakes.",
                "Consistent practice will improve my communication skills."
            ],
            "Paragraph Reading": [
                "I wake up early. I drink water and eat breakfast. I start my day with a smile.",
                "I went to the market with my friend. We bought milk and fruits. It was a good day.",
                "I practice my speech every day. I speak clearly and slowly. This helps me improve.",
                "We planned a short trip. The weather was cool and pleasant. We enjoyed a lot.",
                "Helping others is a good habit. I speak kindly. Good words make people happy."
            ],
            "Tongue Twisters": [
                "She sells seashells by the seashore.",
                "Peter Piper picked a peck of pickled peppers.",
                "Red lorry, yellow lorry.",
                "Betty bought butter but the butter was bitter.",
                "Fresh fried fish, fresh fried fish."
            ],
            "Medical Terminology": [
                "rehabilitation",
                "therapy",
                "medication",
                "appointment",
                "diagnosis",
                "treatment",
                "recovery",
                "exercise"
            ]
        }
        return jsonify({"status": "success", "exercises": exercises}), 200
    except Exception as e:
        print(f"Error fetching exercises: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/debug_db', methods=['GET'])
def debug_db():
    try:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM notification_preferences")
        prefs = cursor.fetchall()
        cursor.execute("SELECT * FROM notification_logs ORDER BY sent_at DESC LIMIT 10")
        logs = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({"preferences": prefs, "logs": logs})
    except Exception as e:
        return str(e)

if __name__ == '__main__':
    create_tables()

    # Start background scheduler
    # We use WERKZEUG_RUN_MAIN check to avoid starting the scheduler twice 
    # when Flask's debug reloader is active.
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        scheduler = BackgroundScheduler(daemon=True)

        scheduler.add_job(
            job_weekly_progress,
            CronTrigger(hour=9, minute=0),
            id='weekly_progress',
            replace_existing=True
        )

        scheduler.start()
        print("[Scheduler] ✅ Background scheduler started. Daily=08:30, Weekly=09:00")
    else:
        # This branch runs in the child process when use_reloader=True
        print("[Scheduler] Background scheduler is active.")

    # use_reloader=True is recommended for development to see changes instantly.
    app.run(host=Config.FLASK_HOST, port=Config.FLASK_PORT, debug=Config.DEBUG, use_reloader=True)
