import json
from cloudify import ctx
from cloudify.state import ctx_parameters as inputs

def add_backend(data_path='/var/www/data.json'):
    with open(data_path) as data_file:
        data = json.load(data_file)

    name = ctx.source.instance.id
    data['client'].append({"nom": name})

    with open(data_path, 'w') as outfile:
        json.dump(data, outfile)

def remove_backend(data_path='/var/www/data.json'):
    with open(data_path) as data_file:
        data = json.load(data_file)

    name = ctx.source.instance.id
    data['client'].remove({"nom": name})

    with open(data_path, 'w') as outfile:
        json.dump(data, outfile)

def _main():
    invocation = inputs['invocation']
    function = invocation['function']
    args = invocation.get('args', [])
    kwargs = invocation.get('kwargs', {})
    globals()[function](*args, **kwargs)


if __name__ == '__main__':
    _main()
