from utils.yaml_loader import load_yaml
import os
import dotenv
dotenv.load_dotenv()

CONFIG = load_yaml("config/workstation_config.yaml")
logger.info(f"[CONFIG] Loaded configuration: {CONFIG}")

broker_ip_os = os.getenv("BROKER_IP", CONFIG["mqtt"].get("broker_ip", "localhost"))
CONFIG["mqtt"]["broker_ip"] = broker_ip_os
logger.info(f"[CONFIG] Broker IP set to: {broker_ip_os}")
logger.info(CONFIG)



