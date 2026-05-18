from Data import WorkOrderGraph, WorkOrder, Dependency, BOM

class Frame:
    def __init__(self, bom, parent_last_id):
        self.bom = bom
        self.parent_last_id = parent_last_id

        self.op_index = 0
        self.child_index = 0

        self.previous_id = parent_last_id
        self.first_id = None

        self.last_id = None    

class BOMFlattener:

    def flatten(self, root_bom: BOM) -> WorkOrderGraph:

        graph = WorkOrderGraph()

        stack = []
        stack.append(Frame(root_bom, parent_last_id=None))

        while stack:
            frame = stack[-1]

            # --- STEP 1: process children first (depth-first) ---
            if frame.child_index < len(frame.bom.children):

                child = frame.bom.children[frame.child_index]
                frame.child_index += 1

                # push child frame
                stack.append(Frame(child, frame.previous_id))

                continue

            # --- STEP 2: process operations ---
            if frame.op_index < len(frame.bom.operations):

                op = frame.bom.operations[frame.op_index]
                frame.op_index += 1

                wo = WorkOrder(
                    id=self.generate_unique_id(op),
                    operation=op
                )

                graph.workOrders[wo.id] = wo

                if frame.first_id is None:
                    frame.first_id = wo.id

                if frame.previous_id is not None:
                    graph.dependencies.append(Dependency(frame.previous_id, wo.id))
                    wo.dependencies.append(frame.previous_id)

                frame.previous_id = wo.id

                continue  # stay on same frame

            # --- STEP 3: finalize frame (equivalent to return) ---
            frame.last_id = frame.previous_id

            stack.pop()

            # if there is a parent frame, connect results
            if stack:
                parent = stack[-1]

                # connect parent → child start
                if frame.first_id is not None and parent.previous_id is not None:
                    graph.dependencies.append(
                        Dependency(parent.previous_id, frame.first_id)
                    )

                # update parent's previous pointer
                parent.previous_id = frame.last_id

        return graph

    def generate_unique_id(self, op: str) -> str:
        # In a real implementation, you would want to ensure uniqueness across the entire graph.
        # For simplicity, we can use a combination of the operation name and a random number or a counter.
        import uuid
        return f"{op}_{uuid.uuid4().hex[:8]}"