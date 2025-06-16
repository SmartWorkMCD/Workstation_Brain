#!/usr/bin/env python3
"""
Test Event Generator for Workstation Brain
Generates various MQTT test events for debugging purposes
"""

import json
import time
import random
import argparse
import paho.mqtt.publish as publish
from typing import Dict, List, Tuple
from datetime import datetime


class WorkstationTestEventGenerator:
    def __init__(self, broker_host="localhost", broker_port=1883, username="admin", password="admin"):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.auth = {'username': username, 'password': password}

        # Topics from config - Workstation Brain format
        self.topics = {
            'candy': 'objdet/results',
            'hand': 'hands/position',
            'task_assignment': 'v1/devices/me/attributes',
            'management': 'management/interface',
            'projector': 'projector/control',
            'task_division': 'v1/devices/me/telemetry'
        }

        # Topics for Task Division integration
        self.task_division_topics = {
            'task_publish': 'tasks/publish',          # Task Division -> Workstation
            'task_subscribe': 'tasks/subscribe/brain'  # Workstation -> Task Division
        }

        # Topics for Neighbors integration
        self.neighbors_topics = {
            'neighbors_update': 'neighbors/update',
            'station_neighbors': 'station/{id}/neighbors',
            'station_version': 'station/{id}/version',
            'station_is_master': 'station/{id}/is_master',
            'topology_positions': 'topology/positions',
            'topology_graph': 'topology/graph',
            'update_command': 'station/{id}/update'
        }

        # Color classes for candy detection
        self.candy_colors = ['red', 'green', 'blue', 'yellow']

        # Grid configuration (from workstation_config.yaml)
        self.grid_config = {
            'rows': 5,
            'cols': 5,
            'image_width': 640,
            'image_height': 480
        }

    def publish_message(self, topic: str, payload: dict, verbose: bool = True):
        """Publish a message to MQTT broker"""
        try:
            message = json.dumps(payload)
            publish.single(
                topic,
                payload=message,
                hostname=self.broker_host,
                port=self.broker_port,
                auth=self.auth
            )
            if verbose:
                print(f"✅ Published to '{topic}': {message}")
            return True
        except Exception as e:
            print(f"❌ Error publishing to '{topic}': {e}")
            return False

    def generate_candy_detection_event(self, num_candies: int = None, colors: List[str] = None,
                                     in_validation_area: bool = True) -> dict:
        """Generate YOLO-style candy detection event"""
        if num_candies is None:
            num_candies = random.randint(1, 6)

        if colors is None:
            colors = random.choices(self.candy_colors, k=num_candies)

        payload = {}

        for i in range(num_candies):
            color = colors[i] if i < len(colors) else random.choice(self.candy_colors)

            if in_validation_area:
                # Generate coordinates within validation area (30-70% of image)
                x1 = random.randint(int(0.3 * 960), int(0.6 * 960))
                y1 = random.randint(int(0.3 * 720), int(0.6 * 720))
                x2 = x1 + random.randint(30, 80)
                y2 = y1 + random.randint(30, 80)
            else:
                # Generate coordinates outside validation area
                x1 = random.randint(0, int(0.25 * 960))
                y1 = random.randint(0, int(0.25 * 720))
                x2 = x1 + random.randint(30, 80)
                y2 = y1 + random.randint(30, 80)

            payload.update({
                f'yolo_{i}_class': color,
                f'yolo_{i}_x1': x1,
                f'yolo_{i}_y1': y1,
                f'yolo_{i}_x2': x2,
                f'yolo_{i}_y2': y2,
                f'yolo_{i}_score': random.uniform(0.7, 0.99)
            })

        return payload

    def generate_hand_tracking_event(self, left_hand: Tuple[float, float] = None,
                                   right_hand: Tuple[float, float] = None) -> dict:
        """Generate hand tracking event with normalized coordinates"""
        payload = {}

        if left_hand:
            payload.update({
                'handL_Wrist_x': left_hand[0],
                'handL_Wrist_y': left_hand[1]
            })

        if right_hand:
            payload.update({
                'handR_Wrist_x': right_hand[0],
                'handR_Wrist_y': right_hand[1]
            })

        return payload

    def generate_task_assignment_event(self, product_tasks: Dict[str, List[str]] = None) -> dict:
        """Generate task assignment event (Workstation Brain format)"""
        if product_tasks is None:
            # Default task assignments
            product_tasks = {
                'produtoA': ['T1A', 'T1B'],
                'produtoB': ['T1A', 'T1C'],
                'produtoC': ['T1B', 'T1C', 'T2A']
            }

        return product_tasks

    def generate_task_division_assignment(self, product_id: str = "produtoA") -> dict:
        """Generate task assignment in Task Division format"""
        # Map product to tasks like Task Division does
        product_configs = {
            'produtoA': {'Blue': 1, 'Green': 3, 'Red': 1},
            'produtoB': {'Blue': 2, 'Green': 4, 'Red': 2},
            'produtoC': {'Blue': 2, 'Green': 1, 'Red': 3}
        }

        config = product_configs.get(product_id, {'Red': 1})

        # Convert to tasks like Task Division does
        tasks = []
        color_to_task = {'Red': 'T1A', 'Green': 'T1B', 'Blue': 'T1C'}

        for color, quantity in config.items():
            task_id = color_to_task.get(color)
            if task_id:
                tasks.extend([task_id] * quantity)

        # Add assembly and packaging tasks
        tasks.extend(['T2A', 'T3A'])

        return {
            "tasks": {product_id: tasks},
            "products": {product_id: {"name": f"Produto {product_id[-1].upper()}", "config": config}}
        }

    def generate_task_completion_event(self, task_id: str, duration: float, product_id: str = None) -> dict:
        """Generate task completion event for Task Division"""
        payload = {task_id: duration}
        if product_id and task_id == "T2A":
            payload["produto_id"] = product_id
        return payload

    def generate_neighbors_update(self, station_id: str = None, left_neighbor: str = None,
                                 right_neighbor: str = None) -> dict:
        """Generate neighbors update for BLE network"""
        if station_id is None:
            station_id = f"WS{random.randint(1, 10)}"

        # Generate random MAC addresses if not provided
        if left_neighbor is None and random.random() > 0.3:  # 70% chance of having left neighbor
            left_neighbor = f"{random.randint(10,99)}:{random.randint(10,99)}:{random.randint(10,99)}:{random.randint(10,99)}:{random.randint(10,99)}:{random.randint(10,99)}"
        if right_neighbor is None and random.random() > 0.3:  # 70% chance of having right neighbor
            right_neighbor = f"{random.randint(10,99)}:{random.randint(10,99)}:{random.randint(10,99)}:{random.randint(10,99)}:{random.randint(10,99)}:{random.randint(10,99)}"

        return {
            "station": station_id,
            "left_neighbor": left_neighbor,
            "right_neighbor": right_neighbor,
            "timestamp": time.time()
        }

    def generate_neighbors_data(self, from_station: str, neighbor_stations: List[str] = None) -> dict:
        """Generate neighbor distance data for topology reconstruction"""
        if neighbor_stations is None:
            neighbor_stations = [f"N{i}" for i in range(1, 4)]

        data = []
        for neighbor in neighbor_stations:
            if neighbor != from_station:
                distance = random.uniform(1.0, 10.0)  # Distance in meters
                variance = random.uniform(0.01, 0.2)   # Measurement variance
                data.append({
                    "id": neighbor,
                    "dist": round(distance, 2),
                    "var": round(variance, 3)
                })

        return {
            "from": from_station,
            "data": data
        }

    def send_candy_detection(self, **kwargs):
        """Send candy detection test event"""
        payload = self.generate_candy_detection_event(**kwargs)
        return self.publish_message(self.topics['candy'], payload)

    def send_hand_tracking(self, **kwargs):
        """Send hand tracking test event"""
        payload = self.generate_hand_tracking_event(**kwargs)
        return self.publish_message(self.topics['hand'], payload)

    def send_task_assignment(self, **kwargs):
        """Send task assignment test event (Workstation Brain format)"""
        payload = self.generate_task_assignment_event(**kwargs)
        return self.publish_message(self.topics['task_assignment'], payload)

    def send_task_division_assignment(self, product_id: str = "produtoA"):
        """Send task assignment in Task Division format"""
        payload = self.generate_task_division_assignment(product_id)
        return self.publish_message(self.task_division_topics['task_publish'], payload)

    def send_task_completion(self, task_id: str, duration: float = None, product_id: str = None):
        """Send task completion to Task Division"""
        if duration is None:
            duration = random.uniform(15.0, 25.0)  # Random completion time

        payload = self.generate_task_completion_event(task_id, duration, product_id)
        return self.publish_message(self.task_division_topics['task_subscribe'], payload)

    def send_workstation_telemetry(self, subtask_id: str, start_time: float = None, end_time: float = None):
        """Send telemetry data (Workstation Brain format)"""
        if start_time is None:
            start_time = time.time() - 20
        if end_time is None:
            end_time = time.time()

        payload = {
            "subtask_id": subtask_id,
            "start_time": start_time,
            "end_time": end_time,
            "duration": end_time - start_time
        }
        return self.publish_message(self.topics['task_division'], payload)

    def send_neighbors_update(self, **kwargs):
        """Send neighbors update (BLE scanning result)"""
        payload = self.generate_neighbors_update(**kwargs)
        return self.publish_message(self.neighbors_topics['neighbors_update'], payload)

    def send_neighbor_distances(self, from_station: str, master_station: str = "N1", **kwargs):
        """Send neighbor distance data to master for topology reconstruction"""
        payload = self.generate_neighbors_data(from_station, **kwargs)
        topic = self.neighbors_topics['station_neighbors'].format(id=master_station)
        return self.publish_message(topic, payload)

    def send_station_version(self, station_id: str, version: str = "1.0.0"):
        """Send station version information"""
        payload = {"id": station_id, "version": version}
        topic = self.neighbors_topics['station_version'].format(id=station_id)
        return self.publish_message(topic, payload)

    def send_master_declaration(self, station_id: str, is_master: bool = True):
        """Send master declaration"""
        payload = {"id": station_id, "is_master": is_master}
        topic = self.neighbors_topics['station_is_master'].format(id=station_id)
        return self.publish_message(topic, payload)

    def simulate_hand_movement_sequence(self, duration: int = 10, grid_cell: Tuple[int, int] = None):
        """Simulate hand movement to a specific grid cell over time"""
        print(f"🎭 Simulating hand movement sequence for {duration} seconds...")

        if grid_cell is None:
            target_row, target_col = 2, 2  # Center of 5x5 grid
        else:
            target_row, target_col = grid_cell

        # Convert grid cell to normalized coordinates
        target_x = (target_col + 0.5) / self.grid_config['cols']
        target_y = (target_row + 0.5) / self.grid_config['rows']

        start_time = time.time()
        while time.time() - start_time < duration:
            # Add some random movement around target
            noise_x = random.uniform(-0.02, 0.02)
            noise_y = random.uniform(-0.02, 0.02)

            current_x = max(0, min(1, target_x + noise_x))
            current_y = max(0, min(1, target_y + noise_y))

            self.send_hand_tracking(right_hand=(current_x, current_y))
            time.sleep(0.5)

        print(f"✅ Hand movement simulation completed")

    def simulate_candy_detection_sequence(self, expected_config: Dict[str, int], duration: int = 5):
        """Simulate gradual candy detection matching expected configuration"""
        print(f"🍬 Simulating candy detection sequence for config: {expected_config}")

        colors_needed = []
        for color, count in expected_config.items():
            colors_needed.extend([color.lower()] * count)

        start_time = time.time()
        detected_so_far = []

        while time.time() - start_time < duration:
            if len(detected_so_far) < len(colors_needed):
                # Gradually add candies
                detected_so_far.append(colors_needed[len(detected_so_far)])

            self.send_candy_detection(
                num_candies=len(detected_so_far),
                colors=detected_so_far.copy(),
                in_validation_area=True
            )
            time.sleep(1)

        print(f"✅ Candy detection sequence completed")

    def simulate_complete_task_workflow(self):
        """Simulate a complete task workflow"""
        print("🔄 Starting complete task workflow simulation...")

        # Step 1: Send task assignment
        print("\n📋 Step 1: Sending task assignment...")
        self.send_task_assignment(product_tasks={'produtoA': ['T1A']})
        time.sleep(2)

        # Step 2: Simulate candy detection for T1A (Red: 1)
        print("\n🍬 Step 2: Simulating candy detection...")
        self.simulate_candy_detection_sequence({'Red': 1}, duration=3)
        time.sleep(1)

        # Step 3: Simulate hand movement to confirmation cell (bottom-right)
        print("\n✋ Step 3: Simulating hand confirmation...")
        confirmation_cell = (self.grid_config['rows'] - 3, self.grid_config['cols'] - 1)  # Last cell
        self.simulate_hand_movement_sequence(duration=3, grid_cell=confirmation_cell)

        print("\n✅ Complete workflow simulation finished!")

    def simulate_task_division_workflow(self):
        """Simulate Task Division integration workflow"""
        print("🔄 Starting Task Division integration workflow...")

        # Step 1: Send Task Division format assignment
        print("\n📋 Step 1: Sending Task Division format assignment...")
        self.send_task_division_assignment('produtoA')
        time.sleep(2)

        # Step 2: Simulate task completion messages to Task Division
        print("\n⏱️ Step 2: Simulating task completions...")
        tasks = ['T1A', 'T1B', 'T1C', 'T2A', 'T3A']
        for i, task in enumerate(tasks):
            duration = random.uniform(15.0, 25.0)
            product_id = 'produtoA' if task == 'T2A' else None
            self.send_task_completion(task, duration, product_id)
            print(f"   ✅ Completed {task} in {duration:.1f}s")
            time.sleep(1)

        print("\n✅ Task Division workflow simulation finished!")

    def simulate_integrated_system_test(self):
        """Simulate complete integrated system test"""
        print("🌐 Starting integrated system test...")

        # Test both message formats
        print("\n🔧 Testing Workstation Brain format...")
        self.send_task_assignment(product_tasks={'produtoA': ['T1A']})
        time.sleep(1)

        print("\n🔧 Testing Task Division format...")
        self.send_task_division_assignment('produtoA')
        time.sleep(1)

        # Test candy detection and hand tracking
        print("\n🍬 Testing candy detection...")
        self.send_candy_detection(colors=['red'], num_candies=1)
        time.sleep(1)

        print("\n✋ Testing hand confirmation...")
        confirmation_x = (4 + 0.5) / 5  # Cell (2,4)
        confirmation_y = (2 + 0.5) / 5
        self.send_hand_tracking(right_hand=(confirmation_x, confirmation_y))
        time.sleep(1)

        # Test task completion formats
        print("\n📊 Testing task completion formats...")
        self.send_task_completion('T1A', 18.5)
        self.send_workstation_telemetry('T1A')

        print("\n✅ Integrated system test completed!")

    def simulate_neighbors_workflow(self):
        """Simulate Neighbors network topology workflow"""
        print("🗺️ Starting Neighbors workflow simulation...")

        # Step 1: Master declaration
        print("\n👑 Step 1: Master node declaration...")
        master_station = "N1"
        self.send_master_declaration(master_station, is_master=True)
        time.sleep(1)

        # Step 2: Station version reporting
        print("\n📋 Step 2: Station version reporting...")
        stations = ["N1", "N2", "N3", "N4"]
        for station in stations:
            version = "1.0.0" if station != "N2" else "0.9.0"  # N2 has old version
            self.send_station_version(station, version)
            time.sleep(0.5)

        # Step 3: BLE neighbor discovery simulation
        print("\n📡 Step 3: BLE neighbor discovery...")
        self.send_neighbors_update("WS1", left_neighbor="AA:BB:CC:DD:EE:01", right_neighbor="AA:BB:CC:DD:EE:02")
        self.send_neighbors_update("WS2", left_neighbor="AA:BB:CC:DD:EE:01", right_neighbor="AA:BB:CC:DD:EE:03")
        self.send_neighbors_update("WS3", left_neighbor="AA:BB:CC:DD:EE:02", right_neighbor=None)
        time.sleep(1)

        # Step 4: Distance measurements for topology
        print("\n📏 Step 4: Distance measurements...")
        self.send_neighbor_distances("N2", master_station, neighbor_stations=["N1", "N3"])
        self.send_neighbor_distances("N3", master_station, neighbor_stations=["N2", "N4"])
        self.send_neighbor_distances("N4", master_station, neighbor_stations=["N3"])

        print("\n✅ Neighbors workflow simulation completed!")

    def simulate_complete_ecosystem_test(self):
        """Simulate complete SmartWorkMCD ecosystem test"""
        print("🌟 Starting Complete Ecosystem Test...")

        # Step 1: Initialize neighbors network
        print("\n🗺️ Phase 1: Network Topology Setup...")
        master_station = "N1"
        self.send_master_declaration(master_station, is_master=True)
        self.send_neighbor_distances("N2", master_station, neighbor_stations=["N1", "N3"])
        time.sleep(1)

        # Step 2: Task assignment and execution
        print("\n📋 Phase 2: Task Assignment & Execution...")
        self.send_task_assignment(product_tasks={'produtoA': ['T1A']})
        time.sleep(1)

        # Simulate candy detection and hand confirmation
        self.send_candy_detection(colors=['red'], num_candies=1)
        time.sleep(1)
        confirmation_x, confirmation_y = (4 + 0.5) / 5, (2 + 0.5) / 5
        self.send_hand_tracking(right_hand=(confirmation_x, confirmation_y))
        time.sleep(1)

        # Step 3: Task completion and telemetry
        print("\n📊 Phase 3: Task Completion & Telemetry...")
        self.send_task_completion('T1A', 18.5)
        self.send_workstation_telemetry('T1A')
        time.sleep(1)

        print("\n🎉 Complete Ecosystem Test finished!")

    def run_interactive_mode(self):
        """Run interactive test event generator"""
        print("🎮 Interactive Test Event Generator")
        print("=" * 50)

        while True:
            print("\nAvailable commands:")
            print("1. Send candy detection")
            print("2. Send hand tracking")
            print("3. Send task assignment (Workstation Brain)")
            print("4. Simulate hand movement")
            print("5. Simulate candy sequence")
            print("6. Complete workflow")
            print("7. Custom event")
            print("8. Send Task Division assignment")
            print("9. Send task completion (to Task Division)")
            print("10. Task Division workflow")
            print("11. Integrated system test")
            print("0. Exit")

            choice = input("\nEnter choice (0-11): ").strip()

            if choice == '0':
                print("👋 Goodbye!")
                break
            elif choice == '1':
                num = input("Number of candies (default: random): ") or None
                num = int(num) if num else None
                self.send_candy_detection(num_candies=num)
            elif choice == '2':
                x = input("Hand X position (0-1, default: 0.5): ") or "0.5"
                y = input("Hand Y position (0-1, default: 0.5): ") or "0.5"
                self.send_hand_tracking(right_hand=(float(x), float(y)))
            elif choice == '3':
                self.send_task_assignment()
            elif choice == '4':
                row = input("Target grid row (0-4, default: 2): ") or "2"
                col = input("Target grid col (0-4, default: 2): ") or "2"
                self.simulate_hand_movement_sequence(grid_cell=(int(row), int(col)))
            elif choice == '5':
                config = input("Expected config (e.g., Red:1,Blue:2) or press enter for Red:1: ") or "Red:1"
                expected = {}
                for item in config.split(','):
                    color, count = item.split(':')
                    expected[color.strip().title()] = int(count.strip())
                self.simulate_candy_detection_sequence(expected)
            elif choice == '6':
                self.simulate_complete_task_workflow()
            elif choice == '7':
                topic = input("Enter topic: ")
                payload_str = input("Enter JSON payload: ")
                try:
                    payload = json.loads(payload_str)
                    self.publish_message(topic, payload)
                except json.JSONDecodeError:
                    print("❌ Invalid JSON format")
            elif choice == '8':
                product_id = input("Product ID (default: produtoA): ") or "produtoA"
                self.send_task_division_assignment(product_id)
            elif choice == '9':
                task_id = input("Task ID (default: T1A): ") or "T1A"
                duration = input("Duration in seconds (default: random): ")
                duration = float(duration) if duration else None
                product_id = input("Product ID (for T2A only, optional): ") or None
                self.send_task_completion(task_id, duration, product_id)
            elif choice == '10':
                self.simulate_task_division_workflow()
            elif choice == '11':
                self.simulate_integrated_system_test()
            else:
                print("❌ Invalid choice")


def main():
    parser = argparse.ArgumentParser(description='Workstation Brain Test Event Generator')
    parser.add_argument('--host', default='localhost', help='MQTT broker host')
    parser.add_argument('--port', type=int, default=1883, help='MQTT broker port')
    parser.add_argument('--username', default='admin', help='MQTT username')
    parser.add_argument('--password', default='admin', help='MQTT password')
    parser.add_argument('--mode', choices=['interactive', 'workflow', 'candy', 'hand', 'task', 'task_division', 'integrated'],
                       default='interactive', help='Test mode')

    args = parser.parse_args()

    # Create test generator
    generator = WorkstationTestEventGenerator(
        broker_host=args.host,
        broker_port=args.port,
        username=args.username,
        password=args.password
    )

    print(f"🔧 Workstation Brain Test Event Generator")
    print(f"📡 Connecting to {args.host}:{args.port}")
    print("=" * 50)

    if args.mode == 'interactive':
        generator.run_interactive_mode()
    elif args.mode == 'workflow':
        generator.simulate_complete_task_workflow()
    elif args.mode == 'candy':
        generator.send_candy_detection()
    elif args.mode == 'hand':
        generator.send_hand_tracking(right_hand=(0.5, 0.5))
    elif args.mode == 'task':
        generator.send_task_assignment()
    elif args.mode == 'task_division':
        generator.simulate_task_division_workflow()
    elif args.mode == 'integrated':
        generator.simulate_integrated_system_test()
    elif args.mode == 'neighbors':
        generator.simulate_neighbors_workflow()
    elif args.mode == 'ecosystem':
        generator.simulate_complete_ecosystem_test()


if __name__ == "__main__":
    main()
