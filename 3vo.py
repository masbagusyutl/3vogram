import requests
import time
import json
from datetime import datetime, timedelta
from colorama import Fore, Style, init
import random

init(autoreset=True)

def get_headers(token=None):
    """Mode copy untuk headers"""
    headers = {
        'accept': 'application/json, text/plain, */*',
        'accept-encoding': 'gzip, deflate',
        'accept-language': 'en-GB,en;q=0.9,en-US;q=0.8',
        'content-type': 'application/json',
        'origin': 'https://3vogram.3vo.me',
        'sec-ch-ua': '"Microsoft Edge";v="142", "Chromium";v="142"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-site',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    if token:
        headers['authorization'] = f'Bearer {token}'
    return headers

def print_welcome_message():
    print(Fore.WHITE + r"""
_  _ _   _ ____ ____ _    ____ _ ____ ___  ____ ____ ___ 
|\ |  \_/  |__| |__/ |    |__| | |__/ |  \ |__/ |  | |__]
| \|   |   |  | |  \ |    |  | | |  \ |__/ |  \ |__| |         
          """)
    print(Fore.GREEN + Style.BRIGHT + "Nyari Airdrop 3VOgram")
    print(Fore.YELLOW + Style.BRIGHT + "Telegram: https://t.me/nyariairdrop\n")

def load_accounts():
    try:
        with open('data.txt', 'r') as file:
            accounts = [line.strip() for line in file if line.strip()]
        print(Fore.BLUE + f"✓ Berhasil memuat {len(accounts)} akun\n")
        return accounts
    except FileNotFoundError:
        print(Fore.RED + "✗ File data.txt tidak ditemukan!")
        return []

def load_proxies():
    try:
        with open('proxy.txt', 'r') as file:
            proxies = []
            for line in file:
                line = line.strip()
                if line:
                    parts = line.split(":")
                    if len(parts) == 4:
                        ip, port, user, password = parts
                        proxy_url = f"http://{user}:{password}@{ip}:{port}"
                    elif len(parts) == 2:
                        ip, port = parts
                        proxy_url = f"http://{ip}:{port}"
                    else:
                        continue
                    proxies.append(proxy_url)
        
        if proxies:
            print(Fore.BLUE + f"✓ Berhasil memuat {len(proxies)} proxy\n")
        return proxies
    except FileNotFoundError:
        print(Fore.YELLOW + "⚠ File proxy.txt tidak ditemukan. Melanjutkan tanpa proxy.\n")
        return []

def get_proxy(proxies):
    if not proxies:
        return None
    proxy_url = random.choice(proxies)
    return {"http": proxy_url, "https": proxy_url}

def telegram_login(init_data, proxy=None):
    try:
        url = "https://qapi.3vo.me/v1//auth/telegram_login"
        
        # Parse init_data untuk mendapatkan user info
        import urllib.parse
        params = dict(urllib.parse.parse_qsl(init_data))
        user_data = json.loads(urllib.parse.unquote(params.get('user', '{}')))
        
        payload = {
            "initData": init_data,
            "user": user_data
        }
        
        response = requests.post(url, json=payload, headers=get_headers(), proxies=proxy, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('accessToken'), user_data
        return None, None
    except Exception as e:
        print(Fore.RED + f"✗ Login gagal: {str(e)}")
        return None, None

def get_user_info(token, proxy=None):
    try:
        url = "https://api.3vo.me/v1/ups/user_info"
        response = requests.post(url, json={}, headers=get_headers(token), proxies=proxy, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        print(Fore.RED + f"✗ Gagal mengambil user info: {str(e)}")
        return None

def get_quest_user(token, user_id, user_data, proxy=None):
    try:
        url = "https://qapi.3vo.me/v1/uds/get_user"
        payload = {
            "user_id": str(user_id),
            "metadata": {
                "name": user_data.get('first_name', ''),
                "username": user_data.get('username', ''),
                "avatar": user_data.get('photo_url', ''),
                "telegram_id": user_data.get('id', 0)
            }
        }
        
        response = requests.post(url, json=payload, headers=get_headers(token), proxies=proxy, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('user')
        return None
    except Exception as e:
        print(Fore.RED + f"✗ Gagal mengambil quest user: {str(e)}")
        return None

def get_inventory(token, user_id, proxy=None):
    try:
        url = "https://qapi.3vo.me/v1/ids/get_inventory"
        payload = {"user_id": str(user_id)}
        
        response = requests.post(url, json=payload, headers=get_headers(token), proxies=proxy, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return data.get('inventory', [])
        return []
    except Exception as e:
        print(Fore.RED + f"✗ Gagal mengambil inventory: {str(e)}")
        return []

def daily_login(token, user_id, proxy=None):
    try:
        # Check login status
        url = "https://qapi.3vo.me/v1/drs/login"
        payload = {"user_id": str(user_id)}
        
        response = requests.post(url, json=payload, headers=get_headers(token), proxies=proxy, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('status') == 'logged_in':
                day = data.get('day', 0)
                
                # Claim reward
                claim_url = "https://qapi.3vo.me/v1/drs/claim"
                claim_response = requests.post(claim_url, json=payload, headers=get_headers(token), proxies=proxy, timeout=30)
                
                if claim_response.status_code == 200:
                    claim_data = claim_response.json()
                    if claim_data.get('success'):
                        reward = claim_data.get('reward', {})
                        print(Fore.GREEN + f"  ✓ Daily Login Hari-{day}: "
                              f"{reward.get('itemKey', 'Unknown')} x{reward.get('finalAmount', 0)}")
                        return True
        return False
    except Exception as e:
        print(Fore.RED + f"  ✗ Daily login gagal: {str(e)}")
        return False

def claim_free_diamond(token, user_id, telegram_id, proxy=None):
    try:
        url = "https://qapi.3vo.me/v1/sds/buy_item"
        payload = {
            "telegram_id": str(telegram_id),
            "user_id": str(user_id),
            "shop_item_id": 1,
            "wallet_type": "TON"
        }
        
        response = requests.post(url, json=payload, headers=get_headers(token), proxies=proxy, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                completed = data.get('completed', [])
                if completed:
                    reward = completed[0].get('reward', {})
                    print(Fore.GREEN + f"  ✓ Klaim Diamond Gratis: "
                          f"{reward.get('itemKey', 'diamonds')} x{reward.get('amount', 0)}")
                    return True
        return False
    except Exception as e:
        # Jika error kemungkinan sudah diklaim atau belum waktunya
        return False

def spin_wheel(token, user_id, proxy=None):
    try:
        url = "https://qapi.3vo.me/v1/ws/spin"
        payload = {
            "user_id": str(user_id),
            "campaign_id": "0"
        }
        
        response = requests.post(url, json=payload, headers=get_headers(token), proxies=proxy, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                results = data.get('results', [])
                if results:
                    winning_reward = results[0].get('winningReward', {})
                    print(Fore.GREEN + f"  ✓ Spin Berhasil: "
                          f"{winning_reward.get('itemKey', 'Unknown')} "
                          f"x{winning_reward.get('finalAmount', 0)}")
                    return True
        return False
    except Exception as e:
        return False

def open_box(token, user_id, item_key, amount, proxy=None):
    try:
        url = "https://qapi.3vo.me/v1/ids/open_box"
        payload = {
            "user_id": str(user_id),
            "item_key": item_key,
            "amount": amount
        }
        
        response = requests.post(url, json=payload, headers=get_headers(token), proxies=proxy, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                rewards = data.get('rewards', [])
                reward_text = ", ".join([f"{r.get('itemKey')} x{r.get('amount')}" for r in rewards])
                print(Fore.GREEN + f"  ✓ Buka {item_key}: {reward_text}")
                return True
        return False
    except Exception as e:
        return False

def process_account(init_data, account_num, total_accounts, proxies):
    try:
        print(Fore.CYAN + f"\n{'='*60}")
        print(Fore.CYAN + f"Memproses Akun {account_num}/{total_accounts}")
        print(Fore.CYAN + f"{'='*60}")
        
        proxy = get_proxy(proxies)
        
        # Login
        print(Fore.YELLOW + "➤ Melakukan login...")
        token, user_data = telegram_login(init_data, proxy)
        
        if not token or not user_data:
            print(Fore.RED + "✗ Login gagal, skip akun ini\n")
            return
        
        # Get user info
        user_info = get_user_info(token, proxy)
        if user_info:
            username = user_info.get('username', 'Unknown')
            nickname = user_info.get('nickname', 'Unknown')
            print(Fore.GREEN + f"✓ Login berhasil: {username} (@{nickname})")
        
        user_id = user_info.get('user_id') if user_info else None
        telegram_id = user_data.get('id')
        
        if not user_id:
            print(Fore.RED + "✗ Gagal mendapatkan user_id\n")
            return
        
        # Get quest user
        quest_user = get_quest_user(token, user_id, user_data, proxy)
        if quest_user:
            points = quest_user.get('points', 0)
            level = quest_user.get('level', 0)
            print(Fore.BLUE + f"  Level: {level} | Points: {points}")
        
        # Daily Login
        print(Fore.YELLOW + "\n➤ Mengecek daily login...")
        daily_login(token, user_id, proxy)
        
        # Claim free diamond (setiap 4 jam sekali)
        print(Fore.YELLOW + "\n➤ Mencoba klaim diamond gratis...")
        claim_free_diamond(token, user_id, telegram_id, proxy)
        
        # Spin wheel
        print(Fore.YELLOW + "\n➤ Mencoba spin wheel...")
        spin_success = spin_wheel(token, user_id, proxy)
        
        if not spin_success:
            print(Fore.YELLOW + "  ⚠ Spin tidak tersedia (mungkin sudah habis)")
        
        # Get inventory and open boxes
        print(Fore.YELLOW + "\n➤ Mengecek inventory...")
        inventory = get_inventory(token, user_id, proxy)
        
        if inventory:
            print(Fore.CYAN + "\n  Inventory:")
            boxes_to_open = []
            
            for item in inventory:
                item_key = item.get('itemKey', '')
                amount = int(item.get('amount', 0))
                display_name = item.get('displayName', '')
                
                if amount > 0:
                    print(Fore.WHITE + f"    • {display_name}: {amount}")
                    
                    # Cek jika box
                    if 'box_' in item_key and amount > 0:
                        boxes_to_open.append((item_key, amount, display_name))
            
            # Buka semua box yang ada
            if boxes_to_open:
                print(Fore.YELLOW + "\n➤ Membuka box...")
                for box_key, box_amount, box_name in boxes_to_open:
                    open_box(token, user_id, box_key, box_amount, proxy)
        
        print(Fore.GREEN + f"\n✓ Akun {account_num} selesai diproses")
        
    except Exception as e:
        print(Fore.RED + f"✗ Error saat memproses akun: {str(e)}")

def countdown(seconds):
    while seconds > 0:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        secs = seconds % 60
        
        print(Fore.CYAN + f"\r⏳ Menunggu {hours:02d}:{minutes:02d}:{secs:02d} "
              f"untuk memulai ulang...", end="", flush=True)
        time.sleep(1)
        seconds -= 1
    
    print(Fore.GREEN + "\r✓ Waktu tunggu selesai, memulai ulang...          \n")

def main():
    print_welcome_message()
    
    # Load accounts
    accounts = load_accounts()
    if not accounts:
        print(Fore.RED + "Tidak ada akun yang ditemukan. Keluar...")
        return
    
    # Load proxies (optional)
    proxies = load_proxies()
    
    total_accounts = len(accounts)
    
    while True:
        print(Fore.MAGENTA + f"\n{'='*60}")
        print(Fore.MAGENTA + f"Memulai siklus baru - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(Fore.MAGENTA + f"Total Akun: {total_accounts}")
        print(Fore.MAGENTA + f"{'='*60}\n")
        
        for idx, init_data in enumerate(accounts, 1):
            process_account(init_data, idx, total_accounts, proxies)
            
            # Jeda 5 detik antar akun (kecuali akun terakhir)
            if idx < total_accounts:
                print(Fore.YELLOW + f"\n⏸ Jeda 5 detik sebelum akun berikutnya...")
                time.sleep(5)
        
        print(Fore.MAGENTA + f"\n{'='*60}")
        print(Fore.MAGENTA + "Semua akun telah diproses")
        print(Fore.MAGENTA + f"{'='*60}\n")
        
        # Countdown 1 hari (24 jam = 86400 detik)
        countdown(14400)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n✗ Program dihentikan oleh user")
    except Exception as e:
        print(Fore.RED + f"\n\n✗ Error fatal: {str(e)}")
