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
    - `openai__key`: Access the OpenAI API
    - `tavily__key`: Access the Tavily API
    - `langfuse__public_key`: Public key for your Langfuse project
    - `langfuse__secret_key`: Secret key for your Langfuse project
    - `langfuse__base_url`: Langfuse base URL (e.g. `https://cloud.langfuse.com`)

   When working in the workshop, there are two options:

   - **Option A – use provided credentials (simplest):** We will give you `openai__key`, `tavily__key`, and shared Langfuse keys. You can run the agent end-to-end, but you cannot log in to Langfuse Cloud to view traces or prompts. With this option you can **skip step 3** (prompts are pre-registered in the shared project), and you will **not** be able to do Exercise 3 (observability).

   - **Option B – use your own Langfuse project:** Create your own Langfuse account and project at [Langfuse](https://langfuse.com/), generate a public/secret key pair, and set `langfuse__public_key`, `langfuse__secret_key`, and `langfuse__base_url` in `settings.env`. This lets you log into the Langfuse UI to inspect traces and prompts and is required to complete **Exercise 3**.

3. **Register prompts in Langfuse (run once per own Langfuse project):**
   In the workshop, this step is **only needed for Option B** (your own Langfuse project). Before using the agents the first time in that project, register the prompts in the Langfuse Prompt Management UI.

   1. Make sure your `settings.env` is configured with your Langfuse project (public/secret key and base URL).
   2. Open the notebook `src/prompt_management/register_prompt.ipynb` in your editor (VS Code, Jupyter, etc.).
   3. Run all cells in the notebook. This will create the following prompts in your Langfuse project:
      - `planner_prompt`
      - `executor_prompt`
      - `web_researcher_prompt`
      - `synthesizer_prompt`
      - `visualizer_prompt`
      - `chart_summarizer_prompt`

   You only need to do this once per Langfuse project or whenever you intentionally change the prompt templates under `src/prompt_management/`.

4. **Execute the project's tests:** To check if the setup was successful, run the project's tests.
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

## Observability with Langfuse

This project is instrumented for tracing with [Langfuse](https://langfuse.com) following the official integration best practices:

- **Environment-based configuration:** Langfuse credentials and host are configured via environment variables (see `settings.env.template`), which are exported in `core.settings.AgentSettings.model_post_init`:
  - `LANGFUSE_PUBLIC_KEY`
  - `LANGFUSE_SECRET_KEY`
  - `LANGFUSE_BASE_URL` (e.g. `https://cloud.langfuse.com`, `https://us.cloud.langfuse.com`, etc.)
- **Pydantic AI instrumentation:** All Pydantic AI agents are created with `instrument=True` and `Agent.instrument_all()` is called at startup (see `src/agents/planner/planner.py`). This uses Pydantic AI's OpenTelemetry support so all model calls and tools emit spans.
- **Top-level trace per query:** The CLI entrypoint (`src/main.py`) wraps each multi-agent run in a Langfuse observation using `langfuse.get_client().start_as_current_observation(...)` and `propagate_attributes(...)` to attach:
  - a `session_id` for the query
  - tags such as `"data-agent"` and `"cli"`
  - metadata including the original user query
- **Flushing in short-lived runs:** After the CLI completes, `langfuse_client.flush()` is called to ensure all observations are exported before the process exits.

These patterns follow the recommendations from:
- Langfuse + Pydantic AI integration guide: https://langfuse.com/integrations/frameworks/pydantic-ai
- Langfuse skill for AI coding agents (best-practices skill used for this setup): https://github.com/langfuse/skills/tree/main/skills/langfuse

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
