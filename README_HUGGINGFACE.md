# OGRag2 - General Ontology Question Answering

This is a Streamlit application that allows you to upload any ontology (OWL/OBO format) and ask questions about it using AI-powered retrieval.

## Features

- Upload any ontology file (OWL/OBO format)
- Automatic parsing and hypergraph construction
- Ask questions in natural language
- Get answers based on ontology content with source references

## How to Use

1. Upload your ontology file using the file uploader
2. Wait for the ontology to be processed (parsing + building hypergraph)
3. Ask questions about the ontology in the chat interface
4. View answers with source context

## Examples

Try uploading ontologies from:
- [OBO Foundry](http://www.obofoundry.org/)
- [BioPortal](https://bioportal.bioontology.org/)

Sample questions:
- "What is [term name]?"
- "What are the main categories in this ontology?"
- "Explain the relationship between [term A] and [term B]"
