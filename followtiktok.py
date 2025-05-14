import requests
import time
import sys # Import sys for exiting the script gracefully

banner = """
████████╗██╗  ██╗ ██████╗ ███╗   ██╗ ██████╗ 
╚══██╔══╝██║  ██║██╔═══██╗████╗  ██║██╔════╝ 
   ██║   ███████║██║   ██║██╔██╗ ██║██║  ███╗
   ██║   ██╔══██║██║   ██║██║╚██╗██║██║   ██║
   ██║   ██║  ██║╚██████╔╝██║ ╚████║╚██████╔╝
 ╚═╝   ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝                                                              
"""
print(banner)

username = input('Nhập Username Tik Tok ( Không Nhập @ ): ')

# Define headers outside the loop as they are mostly constant
headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'vi,fr-FR;q=0.9,fr;q=0.8,en-US;q=0.7,en;q=0.6',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="125", "Chromium";v="125", "Not.A/Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'cross-site',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36',
}

while True:
    session = None
    token = None

    print("\nĐang lấy session và token...")
    try:
        # Fetch the initial page to get session cookie and token
        access_response = requests.get('https://tikfollowers.com/free-tiktok-followers', headers=headers, timeout=10) # Added timeout
        access_response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        if 'ci_session' in access_response.cookies:
            session = access_response.cookies['ci_session']
            headers.update({'cookie': f'ci_session={session}'})
            print(f"Đã lấy được session: {session}")
        else:
            print("Lỗi: Không tìm thấy cookie ci_session.")
            # Consider waiting or exiting if essential data is missing
            time.sleep(5)
            continue

        # Use regex or more robust parsing if split is too fragile
        try:
            token = access_response.text.split("csrf_token = '")[1].split("'")[0]
            print(f"Đã lấy được token: {token}")
        except IndexError:
            print("Lỗi: Không tìm thấy csrf_token trong nội dung trang.")
            # Consider waiting or exiting if essential data is missing
            time.sleep(5)
            continue

    except requests.exceptions.RequestException as e:
        print(f"Lỗi khi truy cập trang: {e}")
        print("Vui lòng kiểm tra kết nối mạng hoặc URL.")
        time.sleep(10) # Wait before retrying after a request error
        continue
    except Exception as e:
        print(f"Lỗi không xác định khi lấy session/token: {e}")
        time.sleep(10)
        continue

    # Proceed only if session and token were successfully obtained
    if session and token:
        print("Đang tìm kiếm người dùng...")
        data_search = f'{{"type":"follow","q":"@{username}","google_token":"t","token":"{token}"}}'
        try:
            search_response = requests.post('https://tikfollowers.com/api/free', headers=headers, data=data_search, timeout=10) # Added timeout
            search_response.raise_for_status() # Raise an HTTPError for bad responses
            search_result = search_response.json()

            if search_result.get('success') == True:
                data_follow = search_result.get('data')
                if data_follow:
                    print("Tìm kiếm người dùng thành công. Đang gửi yêu cầu follow...")
                    data_send = f'{{"google_token":"t","token":"{token}","data":"{data_follow}","type":"follow"}}'
                    try:
                        send_follow_response = requests.post('https://tikfollowers.com/api/free/send', headers=headers, data=data_send, timeout=10) # Added timeout
                        send_follow_response.raise_for_status() # Raise an HTTPError
                        send_follow_result = send_follow_response.json()

                        if send_follow_result.get('o') == 'Success!' and send_follow_result.get('success') == True and send_follow_result.get('type') == 'success':
                            print('Tăng Follow Tik Tok Thành Công')
                            # Wait for a short period before trying again after success
                            time.sleep(60) # Wait for 60 seconds before the next attempt cycle
                            continue
                        elif send_follow_result.get('o') == 'Oops...' and send_follow_result.get('success') == False and send_follow_result.get('type') == 'info':
                            message = send_follow_result.get('message', '')
                            print(f"Thông báo từ server: {message}")
                            try:
                                # Improved parsing for wait time
                                if 'You need to wait for a new transaction. : ' in message:
                                    parts = message.split('You need to wait for a new transaction. : ')[1].split('.')
                                    if parts:
                                        thoigian_str = parts[0]
                                        if 'Minutes' in thoigian_str:
                                            phut_str = thoigian_str.split(' Minutes')[0]
                                            try:
                                                phut = int(phut_str)
                                                giay = phut * 60
                                                for i in range(giay, 0, -1):
                                                    print(f'Vui Lòng Chờ {i} Giây...', end='\r')
                                                    time.sleep(1)
                                                print("Đã hết thời gian chờ. Đang thử lại...")
                                                continue # Continue to the next iteration to try again
                                            except ValueError:
                                                print("Lỗi: Không thể chuyển đổi thời gian chờ sang số nguyên.")
                                                print("Tiếp tục sau 60 giây...")
                                                time.sleep(60)
                                                continue
                                        else:
                                            print("Lỗi: Định dạng thời gian chờ không như mong đợi.")
                                            print("Tiếp tục sau 60 giây...")
                                            time.sleep(60)
                                            continue
                                    else:
                                         print("Lỗi: Không thể phân tích thời gian chờ từ thông báo.")
                                         print("Tiếp tục sau 60 giây...")
                                         time.sleep(60)
                                         continue
                                else:
                                    print("Thông báo lỗi không rõ định dạng thời gian chờ.")
                                    print("Tiếp tục sau 60 giây...")
                                    time.sleep(60)
                                    continue # Continue to the next iteration

                            except Exception as e:
                                print(f"Lỗi khi xử lý thời gian chờ: {e}")
                                print("Tiếp tục sau 60 giây...")
                                time.sleep(60)
                                continue
                        else:
                            print(f"Phản hồi gửi follow không thành công hoặc không mong đợi: {send_follow_result}")
                            print("Tiếp tục sau 60 giây...")
                            time.sleep(60)
                            continue

                    except requests.exceptions.RequestException as e:
                        print(f"Lỗi khi gửi yêu cầu follow: {e}")
                        print("Tiếp tục sau 60 giây...")
                        time.sleep(60)
                        continue
                    except ValueError:
                        print("Lỗi: Không thể phân tích phản hồi JSON từ yêu cầu gửi follow.")
                        print("Tiếp tục sau 60 giây...")
                        time.sleep(60)
                        continue
                    except Exception as e:
                        print(f"Lỗi không xác định khi gửi yêu cầu follow: {e}")
                        print("Tiếp tục sau 60 giây...")
                        time.sleep(60)
                        continue
                else:
                    print("Lỗi: Không tìm thấy dữ liệu follow trong phản hồi tìm kiếm.")
                    print("Tiếp tục sau 60 giây...")
                    time.sleep(60)
                    continue
            elif search_result.get('success') == False:
                 message = search_result.get('message', 'Không có thông báo lỗi cụ thể.')
                 print(f"Tìm kiếm người dùng không thành công: {message}")
                 # Handle specific search errors if necessary, e.g., user not found
                 print("Tiếp tục sau 60 giây...")
                 time.sleep(60)
                 continue
            else:
                print(f"Phản hồi tìm kiếm không thành công hoặc không mong đợi: {search_result}")
                print("Tiếp tục sau 60 giây...")
                time.sleep(60)
                continue


        except requests.exceptions.RequestException as e:
            print(f"Lỗi khi gửi yêu cầu tìm kiếm: {e}")
            print("Tiếp tục sau 60 giây...")
            time.sleep(60)
            continue
        except ValueError:
            print("Lỗi: Không thể phân tích phản hồi JSON từ yêu cầu tìm kiếm.")
            print("Tiếp tục sau 60 giây...")
            time.sleep(60)
            continue
        except Exception as e:
            print(f"Lỗi không xác định khi tìm kiếm người dùng: {e}")
            print("Tiếp tục sau 60 giây...")
            time.sleep(60)
            continue
    else:
        print("Không thể tiếp tục do không lấy được session hoặc token.")
        print("Thử lại sau 60 giây...")
        time.sleep(60)
        continue

