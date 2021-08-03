The main goal of AskOmics is to provide a simple interface able to create complex queries on linked entities.
The query interface is customized based on available (both personal and public) integrated data.

# Starting point

Any entity integrated with the "starting entity" type can be used to start a query. Other entities can still be queried through a linked entity. The starting entity will start with its label already set to 'visible'

![ask](img/startpoint.png)

# Query interface

Once the start entity is chosen, the query builder is displayed.

The query builder is composed of a graph. Nodes (circles) represent entities and links represent relations between entities. The currently selected entity is surrounded by a red circle. Dotted links and entities are not yet instantiated.

![query builder](img/query_builder.png "Query builder, Differential Expression is the selected entity, GeneLink is a suggested entity")

## Entity attributes

The currently selected entity's attribute are shown as attribute boxes on the right of the graph. By default, every instantiated entity has its **label** attribute set to visible (though it can be toggled off). Various filters are available to further refine the query.

Each attribute type has its own filters :

- Entity URI, entity label, and String attribute type: exact match or regular expression (equal or not equal)
- Numeric attribute type, FALDO start, FALDO end: comparison operators
- Category attribute type, FALDO reference, FALDO strand: Value selection among a list
- Date attribute type: comparison operators with a date picker
- Boolean attribute type: "True" or "False" selector

![attributes](img/attributes.png)

!!! Warning
    Due to the way SPARQL works, any result row with an empty value in **any** of its column will not be shown. You can force the display of these rows by using the <i class="fa fa-question-circle></i> button.

!!! Tip
    For the Category type, you can Ctrl+Click to either deselect a value, or select multiple values.

!!! Tip
    For the Numeric and Date types, you can add filters by clicking on the "+" button.

### Additional customization

In addition to the filter, several customization options are available for each attribute box. Depending on the attribute type, not all options will be available.

![customization](img/attribute_box.png)

From left to right :

- <i class="fa fa-bookmark"></i>: Mark the attribute as a **form** attribute. More information [here](template.md#forms).
- <i class="fa fa-link"></i>: Link this attribute to another (on a different entity or the same one) *(only showing rows where both attributes have the same value)*.
- <i class="fa fa-question-circle"></i>: Show all values for this attribute, including empty values.
- <i class="fa fa-ban"></i>: Exclude one or more categories, instead of including *(Select where the attribute IS NOT)*.
- <i class="fa fa-eye"></i>: Show the value of the attribute in the results.

## Linking entities

To query on a linked entity, simple click on a suggested node. The linked node will be surrounded in a red circle, and the list of attributes on the right-hand side will change to show the new node's attributes.

!!! info
     Linking entity A (after filtering on parameter A1) to entity B (filtering on parameter B1) in the interface create the following query : *List all entities A who match parameter A1 , AND are linked to any entity B matching parameter B1*

### Explicit relations

Explicit relations between entities (defined by the "@" symbol in CSV files, and the "Parents" / "Derives_from" relations from GFF files) will appears between related entities. The label will be the name of the relation. If the relation is a *symetric* relation, it will appear twice between entities.

### FALDO relations

All *FALDO* entities will be linked by an implicit *Included_in* relation. This relation is slightly different than *explicit* relations: it relies on the *FALDO* attributes of both entities for the query, instead of a direct link.

!!! Tip
    You can customize the relation by clicking on the link.
    ![faldo](img/faldo.png)

The default *Included_in* relies on the *Start* and *End* *FALDO* attributes.

!!! info
    Entity A is *Included_in* Entity B means that **Entity A Start > Entity B Start** *AND* **Entity B End < Entity B End**
    By default, the inequalities are **Strict**, but it can be disabled from the interface.

If both entities have a defined *Reference* and/or *Strand* attribute, you will be able to select the **Same reference** and/or **Same strand** options. (Both are selected by default if available)

!!! Tip
    You can **Reverse** the relation (Entity B *Included_in* Entity A instead of the opposite) from the interface.

!!! Warning
    *Included_in* queries are **ressource-intensive**, especially if you have a lot of entities.

### Filtering relations

If there are too many related entities displayed, it can be difficult to select the entity you wish to link to.
It is possible to filter the displayed relations on either the name of the entity, or the name of the link.
Simply type out the name you want to filter in either the "Filter links" or the "Filter nodes" fields on the top of the graph.

![filters](img/filters.png)

### Removing relations

At any point, you can remove an instanciated node (and any node linked to it), by selecting the node you wish to remove, and using the <button type="button" class="btn btn-secondary btn-sm">Remove Node</button> button.

![remove](img/remove_node.png)

## MINUS and UNION nodes

In addition to querying on attributes and relations, it is possible to use both **MINUS** and **UNION** *SPARQL* concepts.

!!! info
    Simply *right-click* to any **non-instanciated** node, and select the type of concept you wish to use.
    ![custom_nodes](img/custom_nodes.png)

### MINUS nodes

The behavior of *MINUS* nodes is the following:

- A sub-query is created for listing the instances of the selected entity (the entity linked to the *MINUS* node with the *minus* relation)
- Any instance of the entity matching this sub-query will be removed from the main query

```turtle
SELECT DISTINCT ?gene1_Label
WHERE {
    ?gene1_uri rdf:type <http://askomics.org/data/gene> .
    ?gene1_uri rdfs:label ?gene1_Label .
    {
        MINUS {
        ?mRNA31_uri <http://askomics.org/data/Parent> ?gene1_uri .
        ?mRNA31_uri rdf:type <http://askomics.org/data/mRNA> .
        }
    }
}
```

For instance:

- I want to list all instances of Entity A with the attribute A1
- But I want to exclude all instances of Entity A that are linked to Entity B with the attribute B1

To create this query:
1) Instantiate Entity A with attribute A1
2) Right-click on Entity B and select "Convert to MINUS node"
3) Select entity B
4) Select attribute B1 for entity B

![minus](img/minus.png)

!!! Warning
    When you instantiate a MINUS node, by default no attributes are selected, meaning the query is *Exclude all instances of entity A which are linked to ANY entity B*

!!! info
    The MINUS sub-query can be as extensive as you want (Excluding instances of entity A linked to entity B linked to entity C)

!!! info
    You can use multiple MINUS nodes on the same entity (Exclude instances of entity A linked to entity B, and instances of entity A linked to entity C)

!!! Warning
    While nested MINUS node are possible, the generated query might not be what you would expect. Make sure to check the generated SPARQL query in the results page if the results appear to be strange.

### UNION node

Creating an UNION node behaves as creating an UNION sub-query. **Any** link to this node will be managed as a sub-sub-query, part of the UNION sub-query.

```turtle
SELECT DISTINCT ?gene1_Label
WHERE {
    ?gene1_uri rdf:type <http://askomics.org/data/gene> .
    ?gene1_uri rdfs:label ?gene1_Label .
    {
        {
        ?mRNA31_uri <http://askomics.org/data/Parent> ?gene1_uri .
        ?mRNA31_uri rdf:type <http://askomics.org/data/mRNA> .
        ?mRNA31_uri faldo:location/faldo:begin/faldo:reference ?mRNA31_referenceCategory .

        VALUES ?mRNA31_referenceCategory { <http://askomics.org/data/GL350249> }
        }
        UNION {
        ?mRNA55_uri <http://askomics.org/data/Parent> ?gene1_uri .
        ?mRNA55_uri rdf:type <http://askomics.org/data/mRNA> .
        ?mRNA55_uri faldo:location/faldo:begin/faldo:reference ?mRNA55_referenceCategory .

        VALUES ?mRNA55_referenceCategory { <http://askomics.org/data/GL350249> }
        }
    }
}
```

For instance:

- I want to list all instances of entity A that are **EITHER**
- Linked to entity B
- OR linked to entity C

To create this query:
1) Instantiate entity A
2) Right-click on entity B and select "Convert to UNION node"
3) Entity B is already linked to the UNION node
4) Instantiate entity C by clicking on it

![union](img/union.png)

!!! Warning
    UNION nodes will only behave as a UNION if there are more than one entity linked to it

!!! info
    Sub-sub-queries (entities linked to the UNION node) can be as complex as you want : *I want instances of entity A either linked to entities B with attribute B1, or linked entities C linked with entity D*

!!! Warning
    Just as MINUS node, nested UNION nodes might not behave as you want. Make sure to check the generated SPARQL query in the results page if the results appear to be strange.

# Launching queries

Once you are satisfied with your query, you can either preview the results with <btn><i class="fa fa-table"></i> Run & Preview</btn> (listing at most 30 results), or send a full query with <btn><i class="fa fa-table"></i> Run & save</btn> .

In the case of a full query, you will be able to access the query results (and more) on the [results page](results.md)
