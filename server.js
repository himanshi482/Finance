const express = require('express');
const cors = require('cors');
const nodemailer = require('nodemailer');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));

// Create Nodemailer Transporter
const createTransporter = () => {
    if (process.env.EMAIL_USER && process.env.EMAIL_PASS) {
        return nodemailer.createTransport({
            service: 'gmail',
            auth: {
                user: process.env.EMAIL_USER,
                pass: process.env.EMAIL_PASS
            }
        });
    }
    return null;
};

// API Endpoint to Send OTP to User's Real Gmail
app.post('/api/send-otp', async (req, res) => {
    const { email, otp, action } = req.body;

    if (!email || !otp) {
        return res.status(400).json({ success: false, message: 'Email and OTP code are required.' });
    }

    const actionText = action === 'REGISTER' 
        ? 'Account Registration Verification' 
        : action === 'RESET_PASSWORD' 
        ? 'Password Reset Request' 
        : 'Two-Factor Authentication Sign-In';

    const htmlContent = `
        <div style="font-family: Arial, sans-serif; max-width: 520px; margin: 0 auto; padding: 24px; background-color: #0f172a; color: #f8fafc; border-radius: 12px; border: 1px solid #1e293b;">
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="color: #00f2fe; margin: 0; font-size: 24px; letter-spacing: 1px;">BANK MANAGEMENT SYSTEM</h1>
                <p style="color: #94a3b8; font-size: 13px; margin-top: 4px;">SECURE FINANCIAL VAULT PORTAL</p>
            </div>
            <hr style="border: 0; border-top: 1px solid #334155; margin: 20px 0;" />
            <div style="background: rgba(30, 41, 59, 0.7); padding: 20px; border-radius: 8px; border-left: 4px solid #00f2fe;">
                <h3 style="margin-top: 0; color: #ffffff;">${actionText}</h3>
                <p style="color: #cbd5e1; font-size: 14px; line-height: 1.5;">You have requested a verification code for your bank account. Use the 6-digit OTP below to proceed:</p>
                <div style="text-align: center; margin: 24px 0;">
                    <span style="font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #00f2fe; background: #070a12; padding: 12px 28px; border-radius: 8px; display: inline-block; border: 1px solid #00f2fe;">${otp}</span>
                </div>
                <p style="color: #94a3b8; font-size: 12px; margin-bottom: 0;">⏱️ This OTP code is valid for <strong>2 minutes</strong>. Do not share this code with anyone.</p>
            </div>
            <div style="margin-top: 24px; text-align: center; color: #64748b; font-size: 12px;">
                <p>If you did not initiate this request, please contact Bank Security immediately.</p>
                <p>&copy; 2026 Bank Management System. All rights reserved.</p>
            </div>
        </div>
    `;

    try {
        const transporter = createTransporter();

        if (transporter) {
            await transporter.sendMail({
                from: `"Bank Security Vault" <${process.env.EMAIL_USER}>`,
                to: email,
                subject: `Your Security OTP Code: ${otp}`,
                html: htmlContent
            });
            console.log(`[SMTP] REAL Email OTP sent successfully to Gmail: ${email}`);
            return res.json({ success: true, method: 'SMTP', message: `OTP code sent directly to your Gmail (${email}).` });
        } else {
            // Unconfigured SMTP fallback notice
            console.log(`[NOTICE] Server running without EMAIL_USER/EMAIL_PASS configured in .env.`);
            console.log(`[SECURITY OTP LOG FOR ${email}]: ${otp}`);
            return res.json({ 
                success: true, 
                method: 'DIRECT_DISPATCH', 
                message: `OTP dispatched to ${email}.`,
                requiresFrontendApiFallback: true
            });
        }
    } catch (err) {
        console.error('Error sending email via Nodemailer:', err.message);
        return res.status(500).json({ 
            success: false, 
            message: 'Failed to deliver email via backend SMTP: ' + err.message,
            requiresFrontendApiFallback: true 
        });
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`===================================================`);
    console.log(` Bank Management System API running on port ${PORT}`);
    console.log(` URL: http://0.0.0.0:${PORT}`);
    console.log(`===================================================`);
});
