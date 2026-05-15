# Demo Data Agent

This project setups a data agent designed to answer user's questions.

"*Disclaimer\
This repository is an experimental playground project on an "as is" basis for demonstration and learning purposes only.\
It is not a supported product and is not intended to warranted for production or commercial use.*"

## Getting started

For package-management the Python library `uv` is used. To setup the development environment, execute the following steps.

1. **Setup the development environment:** There are two options available for this setup. If you have no experience of working with DevContainers, we recommend doing the manual setup (Option 2).
    - **Option 1 (DevContainer):** Re-open the project in the devcontainer, then the vscode extensions and dependencies should be installed automatically.
    - **Option 2 (manual setup):**
        - Install `uv` as described [here](https://docs.astral.sh/uv/getting-started/installation/).
        - Execute `uv sync` to create a venv and install the projects dependencies.
        - (Optional): Check out the vscode extensions listed in `.devcontainer/devcontainer.json` and install them.


2. **Create the file for the environment variables**: Copy and rename the file `settings.env.template` to `settings.env` and fill in the missing information and keys, e.g.,
    - `openai__key`: Access the OpenAI API to send requests and receive the models responses
    - `tavily__key`: Access the Tavily API to send requests and receive the models responses
    - `langfuse__key`: Access the LLM engineering platform "langfuse" used for tracing and prompt engineering

**Note:** If you are missing any keys, you can skip this step for now. Please note that you can run the tests but not the actual agent. In order to initialize the actual data agents, an OpenAI, Tavily, and Langfuse credentials are required. Create the respective accounts and copy the keys from the following websites:
- [OpenAI](https://platform.openai.com/docs/overview)
- [Tavily](https://www.tavily.com/)
- [Langfuse](https://langfuse.com/)

3. **Execute the project's tests:** To check if the setup was successful, let's execute the project's tests.
    - Initiate the project's tests. Here, we rely on `pytest`.
    - Run the tests.

## Data agent approach

The data agent consists of different sub-agents that are chosen and used dependend on the task.

1. **Planner:** Sub-agent to derive the plan, i.e., a sequence of numbered steps; each step includes the action and the sub-agent that is assigned to that action.
2. **Executer:** Sub-agent that executes the plan by identifying the sub-agent that should go next and generating the instructions (or agent query) for the chosen agent. Based on the results of the retrieval step, the executor might decide that the plan needs to be changed. In this case, it goes back to the planner and asks it to generate an updated plan.
3. **Web-researcher:** The sub-agent uses the *Tavily Search tool* to search the web and answer the sub-query assigned to it.
4. **Visualizer:** The sub-agent uses the data provided by the Web-researcher to generate a plot, if this is requested by the user.
5. **Chart-summarizer:** The chart summarizer is called if the Visualizer creates a plot. It summarizes the findings of the plot.
6. **Synthesizer:** The synthesizer sub-agent generates text that summarizes the derieved results.

## Execute the data agent

Run `python src/main.py --query "<Your question>"` in your CLI.

Example:
`python src/main.py --query "List the current market capitalization of the top 5 banks in the US?"`


## How to Contribute

This is a playground repository for training purposes. It's not actively maintained, and external contributions aren't expected or solicited.

That said, if you spot a bug, have an improvement in mind, or want to extend an exercise for your own learning, you're welcome to:

1. **Fork the repository** and experiment freely in your own copy — this is the recommended path for training participants.
2. **Open an issue** if you find something broken or unclear in the existing material.
3. **Submit a pull request** if you'd like to suggest a fix or addition. No guarantees it'll be merged, but it may help future learners.

### If you do open a PR

- Keep changes focused — one logical change per PR.
- Follow the existing code style (`ruff format`, `ruff check`).
- Add or update tests for any behavior change (`pytest`).
- Write a clear PR description: what changed, why, and how to verify.
- Be patient — reviews are best-effort.

### Code of Conduct

Be respectful and constructive. This is a learning space.
