import urllib.request
import urllib.parse
import http.cookiejar
import re

def run_e2e():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    print("1. Fetching booking form to obtain CSRF token...")
    req = urllib.request.Request('http://127.0.0.1:8000/bookings/new/?tour=sajek-cloud-kingdom-adventure')
    html = opener.open(req).read().decode('utf-8')

    # Extract csrfmiddlewaretoken
    match = re.search(r'name=["\']csrfmiddlewaretoken["\']\s+value=["\']([^"\']+)["\']', html)
    if not match:
        print("Could not find CSRF token!")
        exit(1)
    csrf_token = match.group(1)
    print(f"   CSRF Token found: {csrf_token[:12]}...")

    print("2. Submitting booking POST request...")
    booking_data = {
        'csrfmiddlewaretoken': csrf_token,
        'tour_id': '1',
        'tour_date_id': '',
        'num_travelers': '2',
        'customer_name': 'Zakir Hossain',
        'customer_email': 'zakir@example.com',
        'customer_phone': '01712345678',
        'customer_address': 'Mirpur 10, Dhaka',
        'special_requests': 'First time traveling to Sajek!'
    }
    encoded_data = urllib.parse.urlencode(booking_data).encode('utf-8')
    post_req = urllib.request.Request(
        'http://127.0.0.1:8000/bookings/new/',
        data=encoded_data,
        headers={'Referer': 'http://127.0.0.1:8000/bookings/new/?tour=sajek-cloud-kingdom-adventure'}
    )
    resp = opener.open(post_req)
    checkout_url = resp.geturl()
    print(f"   Redirected to Checkout URL: {checkout_url}")

    # Extract booking reference from URL
    ref_match = re.search(r'checkout/([^/]+)/', checkout_url)
    if not ref_match:
        print("Failed to get booking reference from checkout URL!")
        exit(1)
    ref = ref_match.group(1)
    print(f"   Booking Reference created: {ref}")

    print("3. Submitting payment simulation POST request...")
    # Fetch checkout page to get new CSRF token
    checkout_html = resp.read().decode('utf-8')
    match = re.search(r'name=["\']csrfmiddlewaretoken["\']\s+value=["\']([^"\']+)["\']', checkout_html)
    csrf_token_checkout = match.group(1) if match else csrf_token

    payment_data = {
        'csrfmiddlewaretoken': csrf_token_checkout,
        'payment_method': 'BKASH',
        'sender_account': '01712345678'
    }
    encoded_payment = urllib.parse.urlencode(payment_data).encode('utf-8')
    pay_req = urllib.request.Request(
        f'http://127.0.0.1:8000/payments/simulate/{ref}/',
        data=encoded_payment,
        headers={'Referer': checkout_url}
    )
    success_resp = opener.open(pay_req)
    success_url = success_resp.geturl()
    print(f"   Redirected to Success URL: {success_url}")

    success_html = success_resp.read().decode('utf-8')
    assert ref in success_html, "Booking reference not in voucher!"
    assert "বুকিং কনফার্মড" in success_html or "ভ্রমণঘুড়ি ভাউচার" in success_html, "Voucher confirmation text not found!"

    print("\nSUCCESS: End-to-end booking and payment confirmation verified perfectly!")

if __name__ == '__main__':
    run_e2e()

