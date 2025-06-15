from yaml_loader import load_yaml
import os
import dotenv
# Load environment variables from .env file
dotenv.load_dotenv()

CONFIG = load_yaml("config/workstation_config.yaml")

broker_ip_os = os.getenv("BROKER_IP", CONFIG["broker_ip"])
CONFIG["broker_ip"] = broker_ip_os



