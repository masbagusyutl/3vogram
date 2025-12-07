import requests
import time
import json
from datetime import datetime, timedelta
from colorama import Fore, Style, init
import random
import urllib.parse

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

def load_interaction_config():
    """Load konfigurasi interaksi dari file interaksi.txt"""
    config = {
        'follow_enabled': False,
        'follow_user_ids': [],
        'comment_words': ["Hi", "GM", "Hello", "GN", "Like", "Nice", "Great", "Amazing"]
    }
    
    try:
        with open('interaksi.txt', 'r', encoding='utf-8') as file:
            lines = [line.strip() for line in file if line.strip() and not line.strip().startswith('#')]
            
            for line in lines:
                # Parse FOLLOW
                if line.upper().startswith('FOLLOW='):
                    value = line.split('=', 1)[1].strip().upper()
                    config['follow_enabled'] = value == 'ON'
                
                # Parse FOLLOW_USER_ID
                elif line.upper().startswith('FOLLOW_USER_ID='):
                    ids_str = line.split('=', 1)[1].strip()
                    if ids_str:
                        # Support multiple IDs separated by comma
                        ids = [id.strip() for id in ids_str.split(',') if id.strip()]
                        try:
                            config['follow_user_ids'] = [int(id) for id in ids]
                        except ValueError:
                            print(Fore.YELLOW + "⚠ Format FOLLOW_USER_ID tidak valid, menggunakan default")
                
                # Parse COMMENT_WORDS
                elif line.upper().startswith('COMMENT_WORDS='):
                    words_str = line.split('=', 1)[1].strip()
                    if words_str:
                        # Support multiple words separated by comma
                        words = [word.strip() for word in words_str.split(',') if word.strip()]
                        if words:
                            config['comment_words'] = words
        
        # Display loaded config
        print(Fore.BLUE + "✓ Konfigurasi Interaksi:")
        print(Fore.WHITE + f"  • Follow: {Fore.GREEN + 'ON' if config['follow_enabled'] else Fore.RED + 'OFF'}")
        if config['follow_enabled'] and config['follow_user_ids']:
            print(Fore.WHITE + f"  • Follow User IDs: {', '.join(map(str, config['follow_user_ids']))}")
        print(Fore.WHITE + f"  • Comment Words: {', '.join(config['comment_words'][:5])}" + 
              (f" (+{len(config['comment_words'])-5} lainnya)" if len(config['comment_words']) > 5 else ""))
        print()
        
        return config
        
    except FileNotFoundError:
        print(Fore.YELLOW + "⚠ File interaksi.txt tidak ditemukan, membuat file default...\n")
        
        # Buat file default
        default_content = """# Konfigurasi Interaksi Bot 3VOgram
# Gunakan # untuk komentar

# Follow User (ON/OFF)
FOLLOW=ON

# ID User yang akan di-follow (pisahkan dengan koma jika lebih dari 1)
FOLLOW_USER_ID=66242

# Kata-kata untuk komentar (pisahkan dengan koma)
COMMENT_WORDS=Hi,GM,Hello,GN,Like,Nice,Great,Amazing,Cool,Awesome,Thanks,Good
"""
        
        try:
            with open('interaksi.txt', 'w', encoding='utf-8') as file:
                file.write(default_content)
            print(Fore.GREEN + "✓ File interaksi.txt berhasil dibuat dengan konfigurasi default\n")
        except Exception as e:
            print(Fore.RED + f"✗ Gagal membuat file interaksi.txt: {str(e)}\n")
        
        return config
    
    except Exception as e:
        print(Fore.RED + f"✗ Error membaca interaksi.txt: {str(e)}\n")
        return config

def get_proxy(proxies):
    if not proxies:
        return None
    proxy_url = random.choice(proxies)
    return {"http": proxy_url, "https": proxy_url}

def telegram_login(init_data, proxy=None):
    try:
        url = "https://qapi.3vo.me/v1//auth/telegram_login"
        
        # Parse init_data untuk mendapatkan user info
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

def follow_user(token, follow_to_id, proxy=None):
    """Follow user tertentu"""
    try:
        url = "https://api.3vo.me/v1/ups/follow_user"
        payload = {"follow_to_id": follow_to_id}
        
        response = requests.post(url, json=payload, headers=get_headers(token), proxies=proxy, timeout=30)
        
        if response.status_code == 200:
            print(Fore.GREEN + f"  ✓ Berhasil follow user ID: {follow_to_id}")
            return True
        return False
    except Exception as e:
        return False

def get_feed(token, limit=20, proxy=None):
    """Ambil feed artikel"""
    try:
        url = "https://api.3vo.me/v1/tas/feed"
        payload = {
            "from_id": 0,
            "limit": limit,
            "content_type": ["text,image,video,audio,short_video"],
            "keywords": [],
            "show_reposts": False
        }
        
        response = requests.post(url, json=payload, headers=get_headers(token), proxies=proxy, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('data', [])
            print(Fore.GREEN + f"  ✓ Berhasil ambil {len(items)} artikel dari feed")
            return items
        return []
    except Exception as e:
        print(Fore.RED + f"  ✗ Gagal ambil feed: {str(e)}")
        return []

def like_article(token, article_id, proxy=None):
    """Like artikel"""
    try:
        url = "https://api.3vo.me/v1/lcs/like"
        payload = {
            "likeable_id": article_id,
            "likeable_type": "article"
        }
        
        response = requests.post(url, json=payload, headers=get_headers(token), proxies=proxy, timeout=30)
        return response.status_code == 200
    except Exception as e:
        return False

def comment_article(token, article_id, content, proxy=None):
    """Komentar pada artikel"""
    try:
        url = "https://api.3vo.me/v1/lcs/comment"
        payload = {
            "commentable_id": article_id,
            "commentable_type": "article",
            "content": content
        }
        
        response = requests.post(url, json=payload, headers=get_headers(token), proxies=proxy, timeout=30)
        return response.status_code == 200
    except Exception as e:
        return False

def process_feed_interactions(token, feed_items, max_count=10, comment_words=None, proxy=None):
    """Like dan komen artikel dari feed"""
    try:
        print(Fore.YELLOW + "\n➤ Memproses like dan komen artikel...")
        
        if comment_words is None:
            comment_words = ["Hi", "GM", "Hello", "GN", "Like", "Nice", "Great", "Amazing"]
        
        processed = 0
        
        for item in feed_items:
            if processed >= max_count:
                break
                
            article_id = item.get('article_id')
            if not article_id:
                continue
            
            # Skip jika komen dinonaktifkan
            if item.get('enable_comment') is False:
                continue
            
            # Like artikel
            if like_article(token, article_id, proxy):
                # Komen artikel
                comment_text = random.choice(comment_words)
                if comment_article(token, article_id, comment_text, proxy):
                    processed += 1
                    print(Fore.GREEN + f"  ✓ Like & komen artikel {article_id}: {comment_text}")
                    time.sleep(0.5)
        
        print(Fore.BLUE + f"  Total artikel diproses: {processed}")
        return True
    except Exception as e:
        print(Fore.RED + f"  ✗ Gagal proses feed: {str(e)}")
        return False

def get_achievements(token, user_id, proxy=None):
    """Ambil daftar achievements"""
    try:
        url = "https://qapi.3vo.me/v1/ads/get_achievements"
        payload = {"user_id": str(user_id)}
        
        response = requests.post(url, json=payload, headers=get_headers(token), proxies=proxy, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                achievements = data.get('achievements', [])
                print(Fore.GREEN + f"  ✓ Berhasil ambil {len(achievements)} achievements")
                return achievements
        return []
    except Exception as e:
        print(Fore.RED + f"  ✗ Gagal ambil achievements: {str(e)}")
        return []

def claim_achievement(token, user_id, achievement_key, stage_index, proxy=None):
    """Klaim achievement tertentu"""
    try:
        url = "https://qapi.3vo.me/v1/ads/claim_achievement"
        payload = {
            "user_id": str(user_id),
            "achievement_key": achievement_key,
            "stage_index": stage_index
        }
        
        response = requests.post(url, json=payload, headers=get_headers(token), proxies=proxy, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                return True
        return False
    except Exception as e:
        return False

def process_achievements(token, user_id, achievements, proxy=None):
    """Proses klaim semua achievements yang tersedia"""
    try:
        print(Fore.YELLOW + "\n➤ Memproses achievements...")
        total_claimed = 0
        
        for achievement in achievements:
            achievement_key = achievement.get('achievementKey')
            if not achievement_key:
                continue
            
            completed_stages = achievement.get('completedStages', {})
            claimed_stages = set(achievement.get('claimedStages', []))
            
            for stage_key in completed_stages.keys():
                try:
                    stage_index = int(stage_key)
                except:
                    continue
                
                # Skip jika sudah diklaim
                if stage_index in claimed_stages:
                    continue
                
                if claim_achievement(token, user_id, achievement_key, stage_index, proxy):
                    total_claimed += 1
                    print(Fore.GREEN + f"  ✓ Klaim achievement: {achievement_key} stage {stage_index}")
                    time.sleep(0.5)
        
        print(Fore.BLUE + f"  Total achievements diklaim: {total_claimed}")
        return True
    except Exception as e:
        print(Fore.RED + f"  ✗ Gagal proses achievements: {str(e)}")
        return False

def claim_task(token, user_id, task_key, proxy=None):
    """Klaim task tertentu"""
    try:
        url = "https://qapi.3vo.me/v1/dts/claim"
        payload = {
            "user_id": str(user_id),
            "task_key": task_key
        }
        
        response = requests.post(url, json=payload, headers=get_headers(token), proxies=proxy, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print(Fore.GREEN + f"  ✓ Klaim task: {task_key}")
                return True
        elif response.status_code == 409:
            print(Fore.YELLOW + f"  ⚠ Task {task_key} sudah diklaim sebelumnya")
        return False
    except Exception as e:
        return False

def process_tasks(token, user_id, proxy=None):
    """Proses klaim tasks"""
    try:
        print(Fore.YELLOW + "\n➤ Memproses tasks...")
        
        # Daftar task yang bisa diklaim
        task_keys = ["spin_wheel", "daily_login", "like_post", "comment_post"]
        
        for task_key in task_keys:
            claim_task(token, user_id, task_key, proxy)
            time.sleep(0.5)
        
        return True
    except Exception as e:
        print(Fore.RED + f"  ✗ Gagal proses tasks: {str(e)}")
        return False

def spin_multiple(token, user_id, max_spins=100, proxy=None):
    """Spin wheel berkali-kali sampai habis"""
    try:
        print(Fore.YELLOW + "\n➤ Mencoba spin wheel maksimal...")
        spin_count = 0
        
        for i in range(max_spins):
            if spin_wheel(token, user_id, proxy):
                spin_count += 1
                time.sleep(0.5)
            else:
                break
        
        if spin_count > 0:
            print(Fore.BLUE + f"  Total spin berhasil: {spin_count}")
        else:
            print(Fore.YELLOW + "  ⚠ Spin tidak tersedia")
        
        return spin_count > 0
    except Exception as e:
        print(Fore.RED + f"  ✗ Gagal spin multiple: {str(e)}")
        return False

def process_account(init_data, account_num, total_accounts, proxies, interaction_config):
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
        
        # Follow user (jika diaktifkan)
        if interaction_config['follow_enabled'] and interaction_config['follow_user_ids']:
            print(Fore.YELLOW + "\n➤ Follow user...")
            for follow_id in interaction_config['follow_user_ids']:
                follow_user(token, follow_id, proxy)
                time.sleep(0.3)
        else:
            print(Fore.YELLOW + "\n⏭ Skip follow user (fitur dimatikan)")
        
        # Ambil feed dan proses like/komen
        print(Fore.YELLOW + "\n➤ Mengambil feed artikel...")
        feed_items = get_feed(token, limit=20, proxy=proxy)
        if feed_items:
            process_feed_interactions(
                token, 
                feed_items, 
                max_count=10, 
                comment_words=interaction_config['comment_words'],
                proxy=proxy
            )
        
        # Daily Login
        print(Fore.YELLOW + "\n➤ Mengecek daily login...")
        daily_login(token, user_id, proxy)
        
        # Claim free diamond (setiap 4 jam sekali)
        print(Fore.YELLOW + "\n➤ Mencoba klaim diamond gratis...")
        claim_free_diamond(token, user_id, telegram_id, proxy)
        
        #Spin multiple times
        spin_multiple(token, user_id, max_spins=100, proxy=proxy)
        
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
                    time.sleep(0.5)
        
        # Process tasks
        process_tasks(token, user_id, proxy)
        
        # Get dan claim achievements
        achievements = get_achievements(token, user_id, proxy)
        if achievements:
            process_achievements(token, user_id, achievements, proxy)
        
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
    
    # Load interaction config
    interaction_config = load_interaction_config()
    
    total_accounts = len(accounts)
    
    while True:
        print(Fore.MAGENTA + f"\n{'='*60}")
        print(Fore.MAGENTA + f"Memulai siklus baru - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(Fore.MAGENTA + f"Total Akun: {total_accounts}")
        print(Fore.MAGENTA + f"{'='*60}\n")
        
        for idx, init_data in enumerate(accounts, 1):
            process_account(init_data, idx, total_accounts, proxies, interaction_config)
            
            # Jeda 5 detik antar akun (kecuali akun terakhir)
            if idx < total_accounts:
                print(Fore.YELLOW + f"\n⏸ Jeda 5 detik sebelum akun berikutnya...")
                time.sleep(5)
        
        print(Fore.MAGENTA + f"\n{'='*60}")
        print(Fore.MAGENTA + "Semua akun telah diproses")
        print(Fore.MAGENTA + f"{'='*60}\n")
        
        # Countdown 4 jam (14400 detik)
        countdown(14400)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(Fore.RED + "\n\n✗ Program dihentikan oleh user")
    except Exception as e:
        print(Fore.RED + f"\n\n✗ Error fatal: {str(e)}")
