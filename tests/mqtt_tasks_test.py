
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



# simulated data
tasks1 = {'produtoA': ['T1C', 'T1C', 'T1C', 'T1D', 'T2A'], 'produtoB': ['T1C', 'T1C', 'T1C', 'T1C', 'T1D', 'T1D', 'T2A'], 'produtoC': ['T1C', 'T1D', 'T1D', 'T1D', 'T2A']}
tasks2 = {'produtoA': ['T3A', 'T3B', 'T3C'], 'produtoB': ['T3A', 'T3B', 'T3C'], 'produtoC': ['T3A', 'T3B', 'T3C']}
tasks3 = {'produtoA': ['T1A', 'T1A', 'T1B'], 'produtoB': ['T1A', 'T1B', 'T1B'], 'produtoC': ['T1A', 'T1A', 'T1A', 'T1B', 'T1B']}

tasks = [tasks1, tasks2, tasks3]
for i in range(0,3):


    # final message structure
    message = json.dumps(tasks[i])

    # send via MQTT
    try:
        
        publish.single("v1/devices/me/attributes", payload=message, hostname="localhost", port=1883, auth={'username': 'admin', 'password': 'admin'})
        print("[MQTT] Message published successfully")
        print(message)
    except Exception as e:
        print(f"[Erro MQTT] {e}")

    time.sleep(15)  # simulate delay between message
