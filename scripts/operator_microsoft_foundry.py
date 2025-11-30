import logging
from os import getenv
from typing import Annotated

import typer
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ResponseStreamEventType
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from template_microsoft_foundry.loggers import get_logger

app = typer.Typer(
    add_completion=False,
    help="template-microsoft-foundry CLI",
)

logger = get_logger(__name__)


def set_verbose_logging(
    verbose: bool,
):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
        logger.setLevel(logging.DEBUG)


@app.command(
    help="https://learn.microsoft.com/ja-jp/agent-framework/tutorials/agents/run-agent?pivots=programming-language-python",
)
def workflow(
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="Name of the workflow",
        ),
    ] = "workflow",
    version: Annotated[
        str,
        typer.Option(
            "--version",
            "-s",
            help="Version of the workflow",
        ),
    ] = "1",
    input: Annotated[
        str,
        typer.Option(
            "--input",
            "-i",
            help="Input to the workflow",
        ),
    ] = "Hello, how are you?",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
):
    set_verbose_logging(verbose)
    logger.info(f"Starting workflow for agent: {name}, version: {version}")

    project_client = AIProjectClient(
        endpoint=getenv("MICROSOFT_FOUNDARY_PROJECT_ENDPOINT"),
        credential=DefaultAzureCredential(),
    )

    with project_client:
        workflow = {
            "name": name,
            "version": version,
        }

        openai_client = project_client.get_openai_client()

        conversation = openai_client.conversations.create()
        logger.info(f"Created conversation (id: {conversation.id})")

        stream = openai_client.responses.create(
            conversation=conversation.id,
            extra_body={
                "agent": {
                    "name": workflow["name"],
                    "type": "agent_reference",
                },
            },
            input=input,
            stream=True,
            metadata={
                "x-ms-debug-mode-enabled": "1",
            },
        )

        for event in stream:
            if event.type == ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_DONE:
                print("\t", event.text)
            elif (
                event.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED
                and event.item.type == "workflow_action"
            ):
                logger.info(f"********************************\nActor - '{event.item.action_id}' :")
            elif (
                event.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_ADDED
                and event.item.type == "workflow_action"
            ):
                logger.info(
                    f"Workflow Item '{event.item.action_id}' is '{event.item.status}' - (previous item was : '{event.item.previous_action_id}')"  # noqa: E501
                )
            elif (
                event.type == ResponseStreamEventType.RESPONSE_OUTPUT_ITEM_DONE and event.item.type == "workflow_action"
            ):
                logger.info(
                    f"Workflow Item '{event.item.action_id}' is '{event.item.status}' - (previous item was: '{event.item.previous_action_id}')"  # noqa: E501
                )
            elif event.type == ResponseStreamEventType.RESPONSE_OUTPUT_TEXT_DELTA:
                logger.info(event.delta)
            else:
                logger.info(f"Unknown event: {event}")

        openai_client.conversations.delete(conversation_id=conversation.id)
        logger.info("Conversation deleted")


@app.command(
    help="https://learn.microsoft.com/ja-jp/python/api/overview/azure/ai-projects-readme?view=azure-python-preview&preserve-view=true",
)
def agent(
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="Name of the agent",
        ),
    ] = "agent",
    input: Annotated[
        str,
        typer.Option(
            "--input",
            "-i",
            help="Input to the agent",
        ),
    ] = "Hello, how are you?",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
):
    set_verbose_logging(verbose)
    logger.info(f"Starting agent: {name}")

    project_client = AIProjectClient(
        endpoint=getenv("MICROSOFT_FOUNDARY_PROJECT_ENDPOINT"),
        credential=DefaultAzureCredential(),
    )

    agent = project_client.agents.get(agent_name=name)
    print(f"Retrieved agent: {agent.name}")

    openai_client = project_client.get_openai_client()

    # Reference the agent to get a response
    response = openai_client.responses.create(
        input=[
            {
                "role": "user",
                "content": input,
            },
        ],
        extra_body={
            "agent": {
                "name": agent.name,
                "type": "agent_reference",
            }
        },
    )

    print(f"Response output: {response.output_text}")


if __name__ == "__main__":
    assert load_dotenv(
        override=True,
        verbose=True,
    ), "Failed to load environment variables"
    app()
