# github-reader

This repository contains the following custom components for deepset Cloud pipelines:

  - `GitHubRepositoryReader`: A component that retrieves files from a GitHub repository returning them as [Haystack](https://haystack.deepset.ai) documents. You can use it in query pipelines.
  - `GitHubUnsafeRepositoryReader`: Implements the same feature as `GitHubRepositoryReader` but allows you to pass your GitHub access token as a string.

## Documentation
For more information about custom components, see [Custom Components](https://docs.deepset.ai/docs/custom-components). 

## 1. Setting up your local dev environment

### Prerequisites

- Python v3.10 or v3.11
- `hatch` package manager

### Hatch: A Python Package Manager

We use `hatch` to manage our Python packages. Install it with pip:

Linux and macOS:
```bash
pip install hatch
```

Windows:
Follow the instructions under https://hatch.pypa.io/1.12/install/#windows

Once installed, create a virtual environment by running:

```bash
hatch shell
```

This creates a virtual environment with all the project dependencies. You can reference this virtual environment in your IDE.

For more information on `hatch`, please refer to the official [Hatch documentation](https://hatch.pypa.io/).

## 2. Development

You can contribute your changes to any of the existing components or add new ones directly in the `src/dc_custom_component/components` directory.

Note that the location of the custom component within the project determines the component's `type` to be used in pipeline YAML. For example, to use the components in a YAML file you use the following names respectively:
  - `dc_custom_component.components.fetchers.github.GitHubRepositoryReader`
  - `dc_custom_component.components.fetchers.github.GitHubUnsafeRepositoryReader`

Here is how you would add them to a pipeline:
```yaml
components:
  github_reader:
    type: dc_custom_component.components.fetchers.github.GitHubRepositoryReader
    init_parameters:
      repository: owner/repo
      file_extensions:
        - .py
      file_encoding: utf-8
      ref: "main"
      access_token:
        env_var: GITHUB_TOKEN
  ...
    
```
### Formatting
We defined a suite of formatting tools. To format your code, run:

```bash
hatch run code-quality:all
```

### Testing

It's crucial to thoroughly test the components before uploading it to deepset Cloud. Consider adding unit and integration tests to ensure that the components function correctly within a pipeline.
- `pytest` is ready to be used with `hatch`
- implement tests under `/test`
- run `hatch run tests`

## 3. Uploading the components

1. Update the components' version in `/src/__about__.py`.
2. Format the code using the `hatch run code-quality:all` command. (Note that hatch commands work from the project root directory only.)
3. Set your [deepset Cloud API key](https://docs.cloud.deepset.ai/v2.0/docs/generate-api-key).
   - On Linux and macOS: `export API_KEY=<TOKEN>`
   - On Windows: `set API_KEY=<TOKEN>`
4. Upload the project by running the following command from inside of this project:
   - On Linux and macOS: `hatch run dc:build-and-push`
   - On Windows: `hatch run dc:build-windows` and `hatch run dc:push-windows`
   This creates a zip file called `custom_component.zip` in the `dist` directory and uploads it to deepset Cloud.

For detailed instructions, refer to our documentation on [Creating a Custom Component](https://docs.deepset.ai/docs/create-a-custom-component).
