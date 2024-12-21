import requests
import random
import sys
from django.http import JsonResponse


# Set environment and credentials
APP_ENVIRONMENT = 'live'  # or 'sandbox'
consumer_key = "3uOP67/JqieNDq7lJzpKgJr0j0AsnHFr"  # Replace with your actual consumer key
consumer_secret = "GwdOVSKze2Mpx1oVYeLH4cbxDRo="  # Replace with your actual consumer secret

# Define the API URLs based on environment
if APP_ENVIRONMENT == 'sandbox':
    api_url = "https://cybqa.pesapal.com/pesapalv3/api/Auth/RequestToken"
    ipn_registration_url = "https://cybqa.pesapal.com/pesapalv3/api/URLSetup/RegisterIPN"
    submit_order_url = "https://cybqa.pesapal.com/pesapalv3/api/Transactions/SubmitOrderRequest"
    get_ipn_list_url = "https://cybqa.pesapal.com/pesapalv3/api/URLSetup/GetIpnList"
elif APP_ENVIRONMENT == 'live':
    api_url = "https://pay.pesapal.com/v3/api/Auth/RequestToken"
    ipn_registration_url = "https://pay.pesapal.com/v3/api/URLSetup/RegisterIPN"
    submit_order_url = "https://pay.pesapal.com/v3/api/Transactions/SubmitOrderRequest"
    get_ipn_list_url = "https://pay.pesapal.com/v3/api/URLSetup/GetIpnList"
else:
    print("Invalid APP_ENVIRONMENT")
    sys.exit()

# Step 1: Request Token from Pesapal
def request_token():
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }
    data = {
        "consumer_key": consumer_key,
        "consumer_secret": consumer_secret
    }
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get('token')
    else:
        print(f"Error requesting token: {response.status_code}")
        sys.exit()

# Step 2: Register IPN (Instant Payment Notification)
def register_ipn(token):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    data = {
        "url": "https://12eb-41-81-142-80.ngrok-free.app/pesapal/pin.php",
        "ipn_notification_type": "POST"
    }
    response = requests.post(ipn_registration_url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get('ipn_id')
    else:
        print(f"Error registering IPN: {response.status_code}")
        sys.exit()

# Step 3: Submit Order Request
def submit_order(token, ipn_id):
    merchant_reference = random.randint(1, 1000000000000000000)
    phone = 'enter_your_number_here'
    amount = 1
    callback_url = "https://45e9-102-0-13-100.ngrok-free.app/pesapal/response-page.php"
    branch = "Nito_industries"
    first_name = "Alvin"
    middle_name = "Odari"
    last_name = "Kiveu"
    email_address = "alvo967@gmail.com"

    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    data = {
        "id": str(merchant_reference),
        "currency": "KES",
        "amount": amount,
        "description": "Payment description goes here",
        "callback_url": callback_url,
        "notification_id": ipn_id,
        "branch": branch,
        "billing_address": {
            "email_address": email_address,
            "phone_number": phone,
            "country_code": "KE",
            "first_name": first_name,
            "middle_name": middle_name,
            "last_name": last_name,
            "line_1": "Pesapal Limited",
            "line_2": "",
            "city": "",
            "state": "",
            "postal_code": "",
            "zip_code": ""
        }
    }

    response = requests.post(submit_order_url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error submitting order: {response.status_code}")
        sys.exit()

# Step 4: Fetch IPN List (Optional, for debugging purposes)
def fetch_ipn_list(token):
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    response = requests.get(get_ipn_list_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching IPN list: {response.status_code}")
        sys.exit()

# Step 5: Get Transaction Status
def get_transaction_status(token, order_tracking_id):
    if APP_ENVIRONMENT == 'sandbox':
        transaction_status_url = f"https://cybqa.pesapal.com/pesapalv3/api/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}"
    elif APP_ENVIRONMENT == 'live':
        transaction_status_url = f"https://pay.pesapal.com/v3/api/Transactions/GetTransactionStatus?orderTrackingId={order_tracking_id}"
    
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(transaction_status_url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching transaction status: {response.status_code}")
        sys.exit()

# Main flow
if __name__ == "__main__":
    # Request token from Pesapal
    token = request_token()

    # Register IPN
    ipn_id = register_ipn(token)

    # Submit order request
    order_response = submit_order(token, ipn_id)
    print("Order response:", order_response)

    # Optionally, fetch IPN list for debugging
    ipn_list = fetch_ipn_list(token)
    print("IPN List:", ipn_list)

    # Example: Get the transaction status for a specific order
    order_tracking_id = "1141a758-1db1-47b0-ae2b-dc699fb0097d"  # Example order tracking ID
    transaction_status = get_transaction_status(token, order_tracking_id)
    print("Transaction Status:", transaction_status)

def make_purchase(request):
    if request.method == "POST":
        # Get the amount and callback URL from the request
        amount = request.POST.get('amount')
        callback_url = request.POST.get('callback_url')

        # Step 1: Get the token
        token = request_token()
        if not token:
            return JsonResponse({"error": "Failed to get token"}, status=500)

        # Step 2: Register IPN
        ipn_id = register_ipn(token)
        if not ipn_id:
            return JsonResponse({"error": "Failed to register IPN"}, status=500)

        # Step 3: Submit the order
        order_response = submit_order(token, ipn_id)
        if order_response and order_response.get('status') == "200":
            return JsonResponse({
                "order_tracking_id": order_response.get('order_tracking_id'),
                "redirect_url": order_response.get('redirect_url'),
                
            })
        else:
            return JsonResponse({"error": "Failed to submit order"}, status=500)

    return JsonResponse({"error": "Invalid request method"}, status=405)

