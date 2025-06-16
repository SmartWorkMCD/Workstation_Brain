
# import paho.mqtt.publish as publish
# import json

# message = json.dumps({
#     "task": "Assemble",
#     "subtask": "ScrewBolt",
#     "progress": 85,
#     "state": {
#         "CombinationValid": True,
#         "HandGridCell": "C3"
#     }
# })

# publish.single("test", payload=message, hostname="localhost", port=1883)

import json, time
import paho.mqtt.publish as publish

import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# simulated data
tasks1 = {'produtoA': ['T1A', 'T1B', 'T1B'], 'produtoB': ['T1A', 'T1A', 'T1B'], 'produtoC': ['T1A', 'T1A', 'T1A', 'T1B', 'T1C']}
tasks2 = {'produtoA': ['T1B', 'T1C', 'T2A'], 'produtoB': ['T1B', 'T1B', 'T1B', 'T1C', 'T1C', 'T2A'], 'produtoC': ['T1C', 'T2A']}
# tasks3 = {'produtoA': ['T3A', 'T3B', 'T3C'], 'produtoB': ['T3A', 'T3B', 'T3C'], 'produtoC': ['T3A', 'T3B', 'T3C']}

tasks = [tasks1, tasks2]
for i in range(len(tasks)):


    # final message structure
    message = json.dumps(tasks[i])

    # send via MQTT
    try:
        
        publish.single("v1/devices/me/attributes", payload=message, hostname="localhost", port=1883, auth={'username': 'admin', 'password': 'admin'})
        logger.info("[MQTT] Message published successfully")
        logger.info(message)
    except Exception as e:
        logger.info(f"[Erro MQTT] {e}")

    time.sleep(15)  # simulate delay between message
