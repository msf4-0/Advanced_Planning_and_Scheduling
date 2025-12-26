import unittest
from appsmith.aps_backend.service.scheduler import generate_schedule, pick_machine

class TestScheduler(unittest.TestCase):
    def setUp(self):
        self.orders = [
            {
                'order_id': 1,
                'operations': [
                    {'name': 'Cutting', 'duration': 2, 'machine_type': 'cutting'},
                    {'name': 'Welding', 'duration': 3, 'machine_type': 'welding'}
                ]
            },
            {
                'order_id': 2,
                'operations': [
                    {'name': 'Cutting', 'duration': 1, 'machine_type': 'cutting'},
                    {'name': 'Welding', 'duration': 2, 'machine_type': 'welding'}
                ]
            }
        ]
        self.machines = [
            {'name': 'Cutter1', 'type': 'cutting'},
            {'name': 'Cutter2', 'type': 'cutting'},
            {'name': 'Welder1', 'type': 'welding'}
        ]

    def test_generate_schedule_basic(self):
        """
        Test basic schedule generation with valid orders and machines.
        """
        schedule = generate_schedule(self.orders, self.machines)
        self.assertEqual(len(schedule), 4)
        order1_ops = sorted(
            [op for op in schedule if op['order_id'] == 1],
            key=lambda x: x['start']
        )
    
        order2_ops = sorted(
            [op for op in schedule if op['order_id'] == 2],
            key=lambda x: x['start']
        )
        
        # Each operation should have a machine assigned and valid start/end
        for op in schedule:
            self.assertIn(op['machine'], [m['name'] for m in self.machines])
            self.assertIsInstance(op['start'], int)
            self.assertIsInstance(op['end'], int)
            self.assertGreaterEqual(op['end'], op['start'])
        # Operations in each order must be sequential
        for ops in [order1_ops, order2_ops]:
            for i in range(1, len(ops)):
                self.assertGreaterEqual(ops[i]['start'], ops[i-1]['end'])

    def test_pick_machine(self):
        '''
        Test machine selection logic.
        '''
        machine = pick_machine('cutting', self.machines)
        self.assertIn(machine, ['Cutter1', 'Cutter2']) 
        machine = pick_machine('welding', self.machines) 
        self.assertEqual(machine, 'Welder1')
        with self.assertRaises(ValueError):
            pick_machine('painting', self.machines)

    def test_no_machine_for_type(self):
        '''
        Test schedule generation when no machine is available for a required type.
        '''
        bad_orders = [
            {
                'order_id': 3,
                'operations': [
                    {'name': 'Painting', 'duration': 2, 'machine_type': 'painting'}
                ]
            }
        ]
        with self.assertRaises(ValueError):
            generate_schedule(bad_orders, self.machines)

    def test_multiple_orders_and_machine_assignment(self):
        # Add more orders and machines to test assignment spread
        orders = [
            {
                'order_id': 1,
                'operations': [
                    {'name': 'Cutting', 'duration': 2, 'machine_type': 'cutting'},
                    {'name': 'Welding', 'duration': 1, 'machine_type': 'welding'}
                ]
            },
            {
                'order_id': 2,
                'operations': [
                    {'name': 'Cutting', 'duration': 2, 'machine_type': 'cutting'},
                    {'name': 'Welding', 'duration': 1, 'machine_type': 'welding'}
                ]
            },
            {
                'order_id': 3,
                'operations': [
                    {'name': 'Cutting', 'duration': 2, 'machine_type': 'cutting'},
                    {'name': 'Welding', 'duration': 1, 'machine_type': 'welding'}
                ]
            }
        ]
        machines = [
            {'name': 'Cutter1', 'type': 'cutting'},
            {'name': 'Cutter2', 'type': 'cutting'},
            {'name': 'Welder1', 'type': 'welding'},
            {'name': 'Welder2', 'type': 'welding'}
        ]
        schedule = generate_schedule(orders, machines)
        self.assertEqual(len(schedule), 6)
        # Each operation assigned to a valid machine
        for op in schedule:
            self.assertIn(op['machine'], [m['name'] for m in machines])
        # No two operations overlap on the same machine
        for m in [m['name'] for m in machines]:
            ops = sorted([op for op in schedule if op['machine'] == m], key=lambda x: x['start'])
            for i in range(1, len(ops)):
                self.assertGreaterEqual(ops[i]['start'], ops[i-1]['end'])

    def test_zero_duration_operation(self):
        orders = [
            {
                'order_id': 1,
                'operations': [
                    {'name': 'Cutting', 'duration': 0, 'machine_type': 'cutting'},
                    {'name': 'Welding', 'duration': 1, 'machine_type': 'welding'}
                ]
            }
        ]
        schedule = generate_schedule(orders, self.machines)
        self.assertEqual(len(schedule), 2)
        cutting_op = next(op for op in schedule if op['operation'] == 'Cutting')
        self.assertEqual(cutting_op['start'], cutting_op['end'])

    def test_empty_orders(self):
        schedule = generate_schedule([], self.machines)
        self.assertEqual(schedule, [])

    def test_empty_machines(self):
        with self.assertRaises(ValueError):
            generate_schedule(self.orders, [])

    def test_machine_type_with_multiple_machines(self):
        # All cutting operations should be distributed between Cutter1 and Cutter2
        schedule = generate_schedule(self.orders, self.machines)
        cutting_ops = [op for op in schedule if op['operation'] == 'Cutting']
        machine_names = set(op['machine'] for op in cutting_ops)
        self.assertTrue(machine_names.issubset({'Cutter1', 'Cutter2'}))

if __name__ == '__main__':
    unittest.main()