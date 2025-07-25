def ipBan(ip: str):
    log_file_path = "/app/logs/custom-ban.log"
    try:
        with open(log_file_path, "r") as log:
            if ip in [line.strip() for line in log]:
                return  # IP already banned, do nothing

        with open(log_file_path, "a") as log:
            log.write(f"{ip}\n")
    except FileNotFoundError:
        with open(log_file_path, "a") as log:
            log.write(f"{ip}\n")
