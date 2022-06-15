import aws_cdk as core
import aws_cdk.assertions as assertions

from python_cdk_example.python_cdk_example_stack import PythonCdkExampleStack

# example tests. To run these tests, uncomment this file along with the example
# resource in python_cdk_example/python_cdk_example_stack.py
def test_sqs_queue_created():
    app = core.App()
    stack = PythonCdkExampleStack(app, "python-cdk-example")
    template = assertions.Template.from_stack(stack)

#     template.has_resource_properties("AWS::SQS::Queue", {
#         "VisibilityTimeout": 300
#     })
