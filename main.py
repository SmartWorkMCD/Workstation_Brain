from brain import WorkstationBrain

if __name__ == "__main__":
    # Define which product and task this workstation is responsible for
    product_id = "produtoA"   # Change this to produtoB, produtoC, etc.
    task_id = "Task2"         # Change this to Task1 or Task3 as needed

    brain = WorkstationBrain(product_id, task_id)
    brain.run()