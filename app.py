import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

PORT = int(os.environ.get('PORT', 3000))

def send_smtp_email(to_email, otp_code, action):
    email_user = os.environ.get('EMAIL_USER')
    email_pass = os.environ.get('EMAIL_PASS')
    if not email_user or not email_pass:
        return None

    if action == 'REGISTER':
        action_text = 'Account Registration Verification'
    elif action == 'RESET_PASSWORD':
        action_text = 'Password Reset Request'
    else:
        action_text = 'Two-Factor Authentication Sign-In'

    html_content = f"""
        <div style="font-family: Arial, sans-serif; max-width: 520px; margin: 0 auto; padding: 24px; background-color: #0f172a; color: #f8fafc; border-radius: 12px; border: 1px solid #1e293b;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="color: #00f2fe; margin: 0; font-size: 24px; letter-spacing: 1px;">BANK MANAGEMENT SYSTEM</h1>
                <p style="color: #94a3b8; font-size: 13px; margin-top: 4px;">SECURE FINANCIAL VAULT PORTAL</p>
            </div>
            <hr style="border: 0; border-top: 1px solid #334155; margin: 20px 0;" />
            <div style="background: rgba(30, 41, 59, 0.7); padding: 20px; border-radius: 8px; border-left: 4px solid #00f2fe;">
                <h3 style="margin-top: 0; color: #ffffff;">{action_text}</h3>
                <p style="color: #cbd5e1; font-size: 14px; line-height: 1.5;">You have requested a verification code for your bank account. Use the 6-digit OTP below to proceed:</p>
                <div style="text-align: center; margin: 24px 0;">
                    <span style="font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #00f2fe; background: #070a12; padding: 12px 28px; border-radius: 8px; display: inline-block; border: 1px solid #00f2fe;">{otp_code}</span>
                </div>
                <p style="color: #94a3b8; font-size: 12px; margin-bottom: 0;">⏱️ This OTP code is valid for <strong>2 minutes</strong>. Do not share this code with anyone.</p>
            </div>
            <div style="margin-top: 24px; text-align: center; color: #64748b; font-size: 12px;">
                <p>If you did not initiate this request, please contact Bank Security immediately.</p>
                <p>&copy; 2026 Bank Management System. All rights reserved.</p>
            </div>
        </div>
    """

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Your Security OTP Code: {otp_code}"
    msg['From'] = f'"Bank Security Vault" <{email_user}>'
    msg['To'] = to_email
    msg.attach(MIMEText(html_content, 'html'))

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(email_user, email_pass)
        server.sendmail(email_user, to_email, msg.as_string())

    return True

@app.route('/api/send-otp', methods=['POST'])
def send_otp():
    data = request.get_json() or {}
    email = data.get('email')
    otp = data.get('otp')
    action = data.get('action')

    if not email or not otp:
        return jsonify({'success': False, 'message': 'Email and OTP code are required.'}), 400

    email_user = os.environ.get('EMAIL_USER')
    email_pass = os.environ.get('EMAIL_PASS')

    try:
        if email_user and email_pass:
            send_smtp_email(email, otp, action)
            print(f"[SMTP] REAL Email OTP sent successfully to Gmail: {email}")
            return jsonify({
                'success': True,
                'method': 'SMTP',
                'message': f'OTP code sent directly to your Gmail ({email}).'
            })
        else:
            print("[NOTICE] Server running without EMAIL_USER/EMAIL_PASS configured in .env.")
            print(f"[SECURITY OTP LOG FOR {email}]: {otp}")
            return jsonify({
                'success': True,
                'method': 'DIRECT_DISPATCH',
                'message': f'OTP dispatched to {email}.',
                'requiresFrontendApiFallback': True
            })
    except Exception as err:
        print(f"Error sending email via SMTP: {err}")
        return jsonify({
            'success': False,
            'message': f'Failed to deliver email via backend SMTP: {str(err)}',
            'requiresFrontendApiFallback': True
        }), 500

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve_static(path):
    if path != "" and os.path.exists(os.path.join(app.static_folder, path)):
        return send_from_directory(app.static_folder, path)
    else:
        return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    print("===================================================")
    print(f" Bank Management System API (Flask) running on port {PORT}")
    print(f" URL: http://0.0.0.0:{PORT}")
    print("===================================================")
    app.run(host='0.0.0.0', port=PORT, debug=False)
