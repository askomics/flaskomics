The main goal of AskOmics is to provide a simple query interface able to create complex queries on linked entities.
The query interface is customized based on the integrated data.

# Starting point

Any entity integrated with the "starting entity" type can be used to start a query. Other entities can still be queried through a linked entity. The starting entity will start with its label already set to 'visible'

![ask](img/startpoint.png)

# Query interface

Once the start entity is chosen, the query builder is displayed.

The query builder is composed of a graph. Nodes (circles) represents entities and links represents relations between entities. The currently selected entity is surrounded by a red circle. Links and other entities are dotted and lighter because there are not instantiated.

![query builder](img/query_builder.png "Query builder, Differential Expression is the selected entity, GeneLink is a suggested entity")

## Entity attribute

The currently selected entity's parameters are shown as attribute boxes on the right of the graph. By default, every instantiated entity has its **label** attribute set to visible. Various filters are available to further refine the query.

!!! Warning
    Unless specified with the <i class="fa fa-question-circle inactive"></i> button, empty values for attributes will not be shown in the results.

!!! info
    For the Category type, you can ctrl+clic to either deselect or select multiple values.

!!! info
    For the Numeric and Date types, you can add filters by clicking on the "+" button.

### Additional customization

In addition to the filter, several customization options are available for each attribute box. Depending on the attribute type, not all options will be available.

![customization](img/attribute_box.png)

From left to right :

- <i class="fa fa-bookmark inactive"></i>: Mark the attribute as a **form** attribute. More information [here](template.md).
- <i class="fa fa-link inactive"></i>: Link this attribute to another (only showing rows where they have the same value).
- <i class="fa fa-question-circle inactive"></i>: Show all values for this attribute, including empty values.
- <i class="fa fa-ban inactive"></i>: Exclude one or more categories, instead of including.
- <i class="fa fa-eye-slash inactive"></i>: Show the value of the attribute in the results.


## Linking entities

To query on a linked entity, simple click on a suggested node. The linked node will be surrounded in a red circle, and the list of attributes on the right-hand side will change to show the new node's attributes.

!!! info
     Linking entity A (after filtering on parameter A1) to entity B (filtering on parameter B1) in the interface create the following query : *List all entities A who match parameter A1 , AND are linked to any entity B matching parameter B1*
