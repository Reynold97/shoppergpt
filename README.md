# ShopperGPT Deployment Guide

This guide explains how to deploy the ShopperGPT WhatsApp assistant on a Linux VM.

## Prerequisites

- Linux VM with Python 3.10+
- Git installed
- Access to the following services:
  - OpenAI API
  - SerpAPI
  - Twilio WhatsApp

## Step 1: Initial Setup

1. Connect to your VM:
```bash
ssh username@your_vm_ip
```

2. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install -y python3-pip python3-venv ffmpeg
```

3. Clone the repository:
```bash
git clone https://github.com/Reynold97/shoppergpt.git
cd shoppergpt
```

## Step 2: Python Environment Setup

1. Create and activate a virtual environment:
```bash
python3 -m venv env
source env/bin/activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Step 3: Environment Configuration

1. Create the .env file:
```bash
nano .env
```

2. Add your environment variables:
```
OPENAI_API_KEY=your_openai_key
SERPAPI_API_KEY=your_serpapi_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_NUMBER=your_twilio_number
```

## Step 4: Service Setup

1. Create a systemd service file:
```bash
sudo nano /etc/systemd/system/shoppergpt.service
```

2. Add the following content (replace paths and user as needed):
```ini
[Unit]
Description=shoppergpt WhatsApp Assistant
After=network.target

[Service]
User=root
Group=root
WorkingDirectory=/root/shoppergpt
Environment="PATH=/root/shoppergpt/env/bin"
EnvironmentFile=/root/shoppergpt/.env
ExecStart=/root/shoppergpt/env/bin/uvicorn src.main:app --host 0.0.0.0 --port 8781

Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

## Step 5: Starting the Service

1. Reload systemd:
```bash
sudo systemctl daemon-reload
```

2. Enable the service to start on boot:
```bash
sudo systemctl enable shoppergpt
```

3. Start the service:
```bash
sudo systemctl start shoppergpt
```

4. Check service status:
```bash
sudo systemctl status shoppergpt
```

## Common Commands

- Stop the service:
```bash
sudo systemctl stop shoppergpt
```

- Restart the service:
```bash
sudo systemctl restart shoppergpt
```

- View logs:
```bash
sudo journalctl -u shoppergpt -f
```

## Twilio Configuration

1. In your Twilio WhatsApp Sandbox settings, set the webhook URL to:
```
http://your_vm_ip:8000/message
```

2. Ensure the webhook method is set to POST

## Security Notes

- The service runs on port 8000 by default
- Make sure your VM's firewall allows traffic on port 8000
- Consider implementing SSL if exposed to the internet
- Keep your .env file secure and with restricted permissions:
```bash
chmod 600 .env
```

## Troubleshooting

If the service fails to start:

1. Check the logs:
```bash
sudo journalctl -u shoppergpt -n 50
```

2. Verify permissions:
```bash
ls -la /root/shoppergpt
ls -la /root/shoppergpt/.env
```

3. Test the application manually:
```bash
source env/bin/activate
uvicorn src.main:app --reload
```

4. Common issues:
   - Environment variables not loaded
   - Python dependencies missing
   - File permissions incorrect
   - Port already in use

## Support

For any issues:
- Check the application logs
- Review the Twilio console for webhook errors
- Ensure all API keys are valid and not expired