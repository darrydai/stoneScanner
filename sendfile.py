import requests

# 要上傳的檔案
my_files = {'file': open('/home/pi/stoneScanner/data/pic/stamp/stamp_result/stamp_1.png', 'rb')}
values = {'folder':'Photos/incoming/'}

# 將檔案加入 POST 請求中
r = requests.post('http://192.168.10.210:8888/Photos/upload.php',files = my_files,data=values)

if r.ok:
    print("Upload completed successfully!")
else:
    print("Something went wrong!")