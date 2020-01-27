A FEderated query is a query who involve several SPARQL endpoints. AskOmics have his dedicated endpoint for the integrated data, but it is also possible to query external resources.


# Define an external endpoint

The first step is to define an external endpoint. External endpoint have their own description. To Display external entities, AskOmics need the *Abstraction* of the distant endpoint. This external abstraction can be build [automatically](#auto-generate-external-abstraction-with-abstractor) or [manually](abstraction.md).

## Auto-generate external abstraction with abstractor

[Abstractor](https://github.com/askomics/abstractor) is a command line tool that auto-generate an abstraction from a distant endpoint.

```bash
pip install abstractor
abstractor -e <endpoint_url> -p <entity_prefix> -o <output_file>
```

## Integrate external abstraction into AskOmics

Once external endpoint's abstraction is generated, its time to add it into AskOmis. Upload it and integrate it. During integration, use `advanced options` and specify the external endpoint.

![integrate_external](img/integrate_external.png)

# Query external endpoint

## Simple query

External startpoint are not displayed by default on the start page. Use the `Source` dropdown button to display external entities.

![external_startpoint](img/external_startpoint.png)


## Federated query

**Work in progress**