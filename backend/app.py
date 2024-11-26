import aws_cdk as cdk
from infrastructure.drink.stack import AwesomeGenerativeDrinkStack
from infrastructure.drink.stack_utils import generate_stack_name

app = cdk.App()
stack_name = generate_stack_name()
AwesomeGenerativeDrinkStack(app, stack_name)

app.synth()
