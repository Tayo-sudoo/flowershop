import qrcode

# Замени на свой IP
ip = "192.168.1.100"
port = "8000"
url = f"http://{ip}:{port}"

qr = qrcode.make(url)
qr.save("site_qr.png")
print(f"QR-код создан для {url}")