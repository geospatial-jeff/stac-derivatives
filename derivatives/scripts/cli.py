import os
import shutil

from derivatives import StacIndices

import click
import yaml

sls_template_path = os.path.join(os.path.dirname(__file__), '..', '..', 'serverless_template.yml')
sls_config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'serverless.yml')

@click.group()
def stac_derivatives():
    pass

@stac_derivatives.command(name='new-service', short_help="Start a new service.")
def new_service():
    shutil.copyfile(sls_template_path, sls_config_path)

@stac_derivatives.command(name='indices', short_help="Add a specific indice (ex. NDVI) to the service.")
@click.option('--name', '-n', type=str, multiple=True, help="Name of indice.")
def indices(name):
    with open(sls_config_path, 'r+') as f:
        config = yaml.unsafe_load(f)

        for indice in name:
            indice = indice.lower()
            lambda_func = {
                "handler": "lambda.ndvi",
                "environment": {
                    "INDICE_NAME": indice
                }
            }

            if not hasattr(StacIndices, indice):
                raise AttributeError(f"'{indice}' is not a supported indice.")

            if not config['functions']:
                config['functions'] = {
                    f'stacDerivatives_{indice}': lambda_func
                }
            else:
                config['functions'].update({
                    f'stacDerivatives_{indice}': lambda_func
                })

        # https://github.com/vincentsarago/lambda-pyskel/blob/master/lambda_pyskel/scripts/cli.py
        f.seek(0)
        f.write(yaml.dump(config, default_flow_style=False))

