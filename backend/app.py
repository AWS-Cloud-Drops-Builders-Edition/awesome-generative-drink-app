import aws_cdk as cdk
from stack_utils import generate_stack_name

from backend.backend_stack import BackendStack

app = cdk.App()
stack_name = generate_stack_name()
BackendStack(app, stack_name)

app.synth()
