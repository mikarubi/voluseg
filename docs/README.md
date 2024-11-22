# Documentation

This folder contains the documentation for the Voluseg project. The docs are a docusaurus app that is built and deployed to GitHub Pages.


### Automatically generating the API Reference documentation
The API Reference documentation is automatically generated from the docstrings and type annotations in the codebase using [pydoc-markdown](https://github.com/NiklasRosenstein/pydoc-markdown).

1. Install pydoc-markdown:
First install `pydoc-markdown` package following their guide [here](https://niklasrosenstein.github.io/pydoc-markdown/#installation-).

2. In the `docs/` directory, run the following command to generate the API Reference documentation:
```bash
pydoc-markdown
```
This command will generate the API Reference documentation from the project and save it in the `docs/voluseg-docs-app/docs/reference/voluseg` folder.


### Running the documentation app locally
To run the documentation app locally, follow these steps:

1. Install the dependencies: go to the `docs/voluseg-docs-app` directory and run:
```bash
# Be sure using node > 18
yarn
```
2. Start the development server:
```bash
yarn start
```

