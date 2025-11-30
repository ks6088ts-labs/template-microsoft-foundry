import asyncio
import logging
from os import getenv
from typing import Annotated, cast

import typer
from agent_framework import ChatMessage, Role, TextContent, UriContent, ai_function
from agent_framework.azure import AzureOpenAIChatClient
from dotenv import load_dotenv
from pydantic import BaseModel, Field

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
def chat(
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="Name of the agent",
        ),
    ] = "Joker",
    instructions: Annotated[
        str,
        typer.Option(
            "--instructions",
            "-i",
            help="Instructions for the agent",
        ),
    ] = "You are good at telling jokes.",
    message: Annotated[
        str,
        typer.Option(
            "--message",
            "-m",
            help="Message to send to the agent",
        ),
    ] = "Tell me a joke in Japanese.",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
):
    set_verbose_logging(verbose)

    agent = AzureOpenAIChatClient(
        api_key=getenv("AZURE_OPENAI_API_KEY"),
        deployment_name=getenv("AZURE_OPENAI_MODEL_CHAT"),
        endpoint=getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=getenv("AZURE_OPENAI_API_VERSION"),
    ).create_agent(
        instructions=instructions,
        name=name,
    )

    async def run_agent():
        result = await agent.run(
            messages=message,
        )
        logger.info(f"Agent response: {result}")
        print(result.text)

    asyncio.run(run_agent())


@app.command(
    help="https://learn.microsoft.com/agent-framework/tutorials/agents/images?pivots=programming-language-python",
)
def chat_with_image(
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="Name of the agent",
        ),
    ] = "VisionAgent",
    instructions: Annotated[
        str,
        typer.Option(
            "--instructions",
            "-i",
            help="Instructions for the agent",
        ),
    ] = "You are a helpful agent that can analyze images.",
    message: Annotated[
        str,
        typer.Option(
            "--message",
            "-m",
            help="Message to send to the agent",
        ),
    ] = "What do you see in this image? Please describe it in Japanese.",
    image_url: Annotated[
        str,
        typer.Option(
            "--image-url",
            "-u",
            help="URL of the image to send to the agent",
        ),
    ] = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
):
    set_verbose_logging(verbose)

    agent = AzureOpenAIChatClient(
        api_key=getenv("AZURE_OPENAI_API_KEY"),
        deployment_name=getenv("AZURE_OPENAI_MODEL_CHAT"),
        endpoint=getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=getenv("AZURE_OPENAI_API_VERSION"),
    ).create_agent(
        instructions=instructions,
        name=name,
    )

    async def run_agent():
        result = await agent.run(
            messages=ChatMessage(
                role=Role.USER,
                contents=[
                    TextContent(text=message),
                    UriContent(uri=image_url, media_type="image/jpeg"),
                ],
            ),
        )
        logger.info(f"Agent response: {result}")
        print(result.text)

    asyncio.run(run_agent())


@app.command(
    help="https://learn.microsoft.com/ja-jp/agent-framework/tutorials/agents/function-tools?pivots=programming-language-python",
)
def chat_with_tools(
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="Name of the agent",
        ),
    ] = "ToolsAgent",
    instructions: Annotated[
        str,
        typer.Option(
            "--instructions",
            "-i",
            help="Instructions for the agent",
        ),
    ] = "You are a helpful agent.",
    message: Annotated[
        str,
        typer.Option(
            "--message",
            "-m",
            help="Message to send to the agent",
        ),
    ] = "What's the weather like in Seattle today?",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
):
    set_verbose_logging(verbose)

    @ai_function(name="weather_tool", description="Retrieves weather information for any location")
    def get_weather(
        location: Annotated[str, Field(description="The location to get the weather for.")],
    ) -> str:
        logger.info(f"Calling get_weather with location: {location}")
        return f"The weather in {location} is cloudy with a high of 15°C."

    agent = AzureOpenAIChatClient(
        api_key=getenv("AZURE_OPENAI_API_KEY"),
        deployment_name=getenv("AZURE_OPENAI_MODEL_CHAT"),
        endpoint=getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=getenv("AZURE_OPENAI_API_VERSION"),
    ).create_agent(
        instructions=instructions,
        name=name,
        tools=[
            get_weather,
        ],
    )

    async def run_agent():
        result = await agent.run(
            messages=message,
        )
        logger.info(f"Agent response: {result}")
        print(result.text)

    asyncio.run(run_agent())


@app.command(
    help="https://learn.microsoft.com/ja-jp/agent-framework/tutorials/agents/structured-output?pivots=programming-language-python",
)
def structured_output(
    name: Annotated[
        str,
        typer.Option(
            "--name",
            "-n",
            help="Name of the agent",
        ),
    ] = "HelpfulAssistant",
    instructions: Annotated[
        str,
        typer.Option(
            "--instructions",
            "-i",
            help="Instructions for the agent",
        ),
    ] = "You are a helpful assistant that extracts person information from text.",
    message: Annotated[
        str,
        typer.Option(
            "--message",
            "-m",
            help="Message to send to the agent",
        ),
    ] = "Please provide information about John Smith, who is a 35-year-old software engineer.",
    verbose: Annotated[
        bool,
        typer.Option("--verbose", "-v", help="Enable verbose output"),
    ] = False,
):
    set_verbose_logging(verbose)

    class PersonInfo(BaseModel):
        """Information about a person."""

        name: str | None = None
        age: int | None = None
        occupation: str | None = None

    agent = AzureOpenAIChatClient(
        api_key=getenv("AZURE_OPENAI_API_KEY"),
        deployment_name=getenv("AZURE_OPENAI_MODEL_CHAT"),
        endpoint=getenv("AZURE_OPENAI_ENDPOINT"),
        api_version=getenv("AZURE_OPENAI_API_VERSION"),
    ).create_agent(
        instructions=instructions,
        name=name,
    )

    async def run_agent():
        result = await agent.run(
            messages=message,
            response_format=PersonInfo,
        )
        person_info = cast(PersonInfo, result.value)

        logger.info(
            f"Agent response: {
                person_info.model_dump_json(
                    indent=2,
                )
            }"
        )
        print(f"Name: {person_info.name}, Age: {person_info.age}, Occupation: {person_info.occupation}")

    asyncio.run(run_agent())


if __name__ == "__main__":
    assert load_dotenv(
        override=True,
        verbose=True,
    ), "Failed to load environment variables"
    app()
