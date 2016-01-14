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

    for node_type_update in nodes_type_update:
        for node in ctx.nodes:
            if node.type == node_type_update:
                for instance in node.instances:
                    send_event_starting_tasks[instance.id] = instance.send_event('Starting to run operation')
                    send_event_done_tasks[instance.id] = instance.send_event('Done running operation')


    for node_type_update in nodes_type_update:
        for node in ctx.nodes:
            if node.type == node_type_update:
                for instance in node.instances:

                    sequence = graph.sequence()

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

                    sequence.add(
                        send_event_starting_tasks[instance.id],
                        operation_task_unlink,
                        instance.send_event('Update task !!'),
                        operation_task_link,
                        send_event_done_tasks[instance.id])

    for node in ctx.nodes:
        for instance in node.instances:
            for rel in instance.relationships:

                instance_starting_task = send_event_starting_tasks.get(instance.id)
                target_done_task = send_event_done_tasks.get(rel.target_id)

                if instance_starting_task and target_done_task:
                    graph.add_dependency(instance_starting_task, target_done_task)


    return graph.execute()