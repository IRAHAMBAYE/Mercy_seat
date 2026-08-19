import datetime
import base64
import requests
from django.conf import settings


class MpesaDarajaClient:
    def __init__(self):
        # Fetch configurations securely from Django settings production deck
        self.consumer_key = getattr(settings, 'MPESA_CONSUMER_KEY', 'your_key')
        self.consumer_secret = getattr(settings, 'MPESA_CONSUMER_SECRET', 'your_secret')
        self.short_code = getattr(settings, 'MPESA_SHORTCODE', '174379')  # Test sandbox default
        self.passkey = getattr(settings, 'MPESA_PASSKEY',
                               'bfb279f9aa9bdbcf158e97dd71a467cd2e0c893059b10f78e6b72ada1ed2c919')

        self.env = getattr(settings, 'MPESA_ENVIRONMENT', 'sandbox')
        self.base_url = "https://safaricom.co.ke" if self.env == 'sandbox' else "https://safaricom.co.ke"

    def get_access_token(self):
        """Generates the mandatory bearer authorization header credentials token"""
        api_url = f"{self.base_url}/oauth/v1/generate?grant_type=client_credentials"
        try:
            response = requests.get(api_url, auth=(self.consumer_key, self.consumer_secret), timeout=10)
            if response.status_code == 200:
                return response.json().get('access_token')
            raise Exception(f"Token generation failed with status code {response.status_code}")
        except Exception as e:
            return None

    def send_stk_push(self, phone_number, amount, callback_url, account_reference="Tithe",
                      transaction_desc="Church Giving"):
        """Triggers the secure STK Pin popup directly to a congregation member's phone screen"""
        access_token = self.get_access_token()
        if not access_token:
            return {"status": "error", "message": "Failed authorization generation step"}

        api_url = f"{self.base_url}/mpesa/stkpush/v1/processrequest"
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        password_source = f"{self.short_code}{self.passkey}{timestamp}"
        password = base64.b64encode(password_source.encode()).decode('utf-8')

        payload = {
            "BusinessShortCode": self.short_code,
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": int(amount),
            "PartyA": phone_number,  # Format must strictly be 2547XXXXXXXX
            "PartyB": self.short_code,
            "PhoneNumber": phone_number,
            "CallBackURL": callback_url,
            "AccountReference": account_reference,
            "TransactionDesc": transaction_desc
        }

        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
        return response.json()

    def initiate_b2c_disbursement(self, phone_number, amount, result_url, queue_url, remarks="Welfare Support"):
        """Pushes church financial payouts from the Paybill utility directly to individuals"""
        access_token = self.get_access_token()
        if not access_token:
            return {"status": "error", "message": "Failed authorization generation step"}

        api_url = f"{self.base_url}/mpesa/b2c/v1/paymentrequest"
        headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

        payload = {
            "InitiatorName": getattr(settings, 'MPESA_INITIATOR_NAME', 'testapi'),
            "SecurityCredential": getattr(settings, 'MPESA_SECURITY_CREDENTIAL', 'encrypted_password'),
            "CommandID": "SalaryPayment" if amount > 5000 else "BusinessPayment",
            "Amount": int(amount),
            "PartyA": self.short_code,
            "PartyB": phone_number,
            "Remarks": remarks,
            "QueueTimeOutURL": queue_url,
            "ResultURL": result_url,
            "Occasion": "Church Disbursement"
        }

        response = requests.post(api_url, json=payload, headers=headers, timeout=15)
        return response.json()
