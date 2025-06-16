#!/usr/bin/env python3
"""
Quick Test Events for Workstation Brain - Simple debugging script
Enhanced with Task Division and Neighbors integration (MQTT only)
"""

import json
import time
import paho.mqtt.publish as publish


def send_test_message(topic, payload, description=""):
    """Send a test message to MQTT broker"""
    try:
        message = json.dumps(payload)
        publish.single(
            topic,
            payload=message,
            hostname="localhost",
            port=1883,
            auth={'username': 'admin', 'password': 'admin'}
        )
        print(f"✅ {description}")
        print(f"   Topic: {topic}")
        print(f"   Payload: {message}")
        print()
        return True
    except Exception as e:
        print(f"❌ Failed to send {description}: {e}")
        return False


def main():
    print("🚀 Quick Test Events for Workstation Brain")
    print("=" * 50)

    # Test 1: Send task assignment (Workstation Brain format)
    print("📋 Test 1: Task Assignment (Workstation Brain)")
    task_payload = {
        'produtoA': ['T1A'],  # Red candy wrapping task
    }
    send_test_message(
        "v1/devices/me/attributes",
        task_payload,
        "Task assignment sent (T1A - Red candy)"
    )

    time.sleep(2)

    # Test 1b: Send task assignment (Task Division format)
    print("📋 Test 1b: Task Assignment (Task Division format)")
    task_division_payload = {
        "tasks": {"produtoA": ["T1A"]},
        "products": {"produtoA": {"name": "Produto A", "config": {"Red": 1}}}
    }
    send_test_message(
        "tasks/publish",
        task_division_payload,
        "Task Division format assignment"
    )

    time.sleep(2)

    # Test 2: Send candy detection (matching expected config)
    print("🍬 Test 2: Candy Detection (Matching)")
    candy_payload = {
        'yolo_0_class': 'red',
        'yolo_0_x1': 400,  # In validation area (30-70%)
        'yolo_0_y1': 300,
        'yolo_0_x2': 480,
        'yolo_0_y2': 380,
        'yolo_0_score': 0.95
    }
    send_test_message(
        "objdet/results",
        candy_payload,
        "Red candy detected in validation area"
    )

    time.sleep(2)

    # Test 3: Send hand tracking (outside confirmation area)
    print("✋ Test 3: Hand Tracking (Normal position)")
    hand_payload = {
        'handR_Wrist_x': 0.5,  # Center of image
        'handR_Wrist_y': 0.5
    }
    send_test_message(
        "hands/position",
        hand_payload,
        "Right hand at center position"
    )

    time.sleep(3)

    # Test 4: Send hand to confirmation area (bottom-right corner)
    print("✅ Test 4: Hand Confirmation")
    confirmation_payload = {
        'handR_Wrist_x': 0.9,  # Bottom-right area (cell 2,4)
        'handR_Wrist_y': 0.5   # Row 2, Col 4 in 5x5 grid
    }
    send_test_message(
        "hands/position",
        confirmation_payload,
        "Right hand moved to confirmation area"
    )

    time.sleep(2)

    # Test 5: Send task completion (Task Division format)
    print("⏱️ Test 5: Task Completion (Task Division format)")
    completion_payload = {
        "T1A": 18.5  # Task completed in 18.5 seconds
    }
    send_test_message(
        "tasks/subscribe/brain",
        completion_payload,
        "Task completion sent to Task Division"
    )

    time.sleep(2)

    # Test 6: Send task completion (Workstation Brain format)
    print("📊 Test 6: Task Completion (Workstation Brain format)")
    telemetry_payload = {
        "subtask_id": "T1A",
        "start_time": time.time() - 20,
        "end_time": time.time(),
        "duration": 20.0
    }
    send_test_message(
        "v1/devices/me/telemetry",
        telemetry_payload,
        "Workstation Brain telemetry"
    )

    # Test 7: Neighbors update
    print("🗺️ Test 7: Neighbors Update")
    neighbors_payload = {
        "station": "WS1",
        "left_neighbor": "AA:BB:CC:DD:EE:01",
        "right_neighbor": "AA:BB:CC:DD:EE:02",
        "timestamp": time.time()
    }
    send_test_message(
        "neighbors/update",
        neighbors_payload,
        "BLE neighbors discovered"
    )

    time.sleep(1)

    # Test 8: Station distance measurements
    print("📏 Test 8: Distance Measurements")
    distance_payload = {
        "from": "N2",
        "data": [
            {"id": "N1", "dist": 5.2, "var": 0.1},
            {"id": "N3", "dist": 3.8, "var": 0.05}
        ]
    }
    send_test_message(
        "station/N1/neighbors",
        distance_payload,
        "Distance measurements for topology"
    )

    time.sleep(1)

    # Test 9: Clear hands (no hands present)
    print("🚫 Test 9: No Hands Present")
    empty_hand_payload = {}
    send_test_message(
        "hands/position",
        empty_hand_payload,
        "No hands detected (empty payload)"
    )

    print("🎯 Quick test sequence completed!")
    print("\nNext steps:")
    print("- Check your Workstation Brain logs")
    print("- Monitor state transitions")
    print("- Check Task Division integration")
    print("- Check Neighbors topology reconstruction")
    print("- Use the full test generator for more complex scenarios")


if __name__ == "__main__":
    main()
