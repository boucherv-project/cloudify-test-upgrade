from cloudify.decorators import workflow
from cloudify.workflows import ctx
from cloudify.workflows.tasks_graph import forkjoin
import pprint

@workflow
def run_operation(operation, nodes_type_update, operation_kwargs, **kwargs):
    graph = ctx.graph_mode()

    send_event_starting_tasks = {}
    send_event_done_tasks = {}
    run_it = False
    tasks = {}

    for node_type_update in nodes_type_update:
        for node in ctx.nodes:
            if node.type == node_type_update:
                for instance in node.instances:
                    send_event_starting_tasks[instance.id] = instance.send_event('Starting to run operation')
                    send_event_done_tasks[instance.id] = instance.send_event('Done running operation')


    for node_type_update in nodes_type_update:
        tasks[node_type_update] = []
        for node in ctx.nodes:
            if node.type == node_type_update:
                for instance in node.instances:

                    subgraph = graph.subgraph('some_start_subgraph')
                    subgraph_sequence = subgraph.sequence()

                    #operation_task = instance.execute_operation(operation, kwargs=operation_kwargs)

                    forkjoin_tasks_unlink = []
                    for relationship in instance.relationships:
                        if relationship.relationship.target_id == 'nginx':
                            operation_unlink = 'cloudify.interfaces.relationship_lifecycle.unlink'
                            forkjoin_tasks_unlink.append(relationship.execute_source_operation(operation_unlink))
                            forkjoin_tasks_unlink.append(relationship.execute_target_operation(operation_unlink))
                    operation_task_unlink = forkjoin(*forkjoin_tasks_unlink)

                    forkjoin_tasks_link = []
                    for relationship in instance.relationships:
                        if relationship.relationship.target_id == 'nginx':
                            operation_link = 'cloudify.interfaces.relationship_lifecycle.establish'
                            forkjoin_tasks_link.append(relationship.execute_source_operation(operation_link))
                            forkjoin_tasks_link.append(relationship.execute_target_operation(operation_link))
                    operation_task_link = forkjoin(*forkjoin_tasks_link)

                    subgraph_sequence.add([
                        send_event_starting_tasks[instance.id],
                        operation_task_unlink,
                        instance.send_event('Update task !!'),
                        operation_task_link,
                        send_event_done_tasks[instance.id]])

                    tasks[node_type_update].append(subgraph)

    previous_task = None
    for node_task in tasks:
        for task in tasks[node_task]:
            if previous_task:
                graph.add_dependency(task, previous_task)
            previous_task = task

    return graph.execute()
