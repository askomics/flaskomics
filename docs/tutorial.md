In this tutorial, we will learn the basics of AskOmics by analyses RNA-seq results. The data comes from a differential expression analysis and are provided for you. 4 files will be used in this tutorial :

- [Differentially expressed results file](https://zenodo.org/record/2529117/files/limma-voom_luminalpregnant-luminallactate): genes in rows, and 4 required columns: identifier (ENTREZID), gene symbol (SYMBOL), log fold change (logFC) and adjusted P values (adj.P.Val)
- [Reference genome annotation file](https://zenodo.org/record/3601076/files/Mus_musculus.GRCm38.98.subset.gff3) in GFF format
- [Correspondence file between gene symbol and Ensembl id](https://zenodo.org/record/3601076/files/symbol-ensembl.tsv): TSV of two columns: symbol and the corresponding Ensembl id
- [QTL file](https://zenodo.org/record/3601076/files/MGIBatchReport_Qtl_Subset.txt): QTL in row, with 5 required columns: identifier, chromosome, start, end and name

Throughout the guide, you will find <badge class="hands-on">Hands-on</badge> containing tutorial instruction to perform in order to get started with AskOmics.

To complete the tutorial, you will need an Askomics instance. You can [install your own](production-deployment.md) or use this [public instance](https://askomics.genouest.org).


# Account creation and management

## Login or signup into AskOmics

AskOmics is a mutli-user plateform. To use it, you will need an account on the instance. Use the <navbar><i class="fa fa-sign-in"></i> Login</navbar> button on the navbar, and log in using your AskOmics credentials. If you don't have already an account, fill the signup form by clicking on <askolink>signup</askolink> below the login form.

!!! Hands-on
    Create your AskOmics account (or login with your existing one)


Once your are logged, you can use all the functionalities of AskOmics.

## Manage your account

To manage your account, use the <navbar><i class="fa fa-cog"></i> Account management</navbar> tab by clicking on <navbar><i class="fa fa-user"></i> Your Name &#9662;</navbar> on the navigation bar.


Uses the forms to change your personal information.

# Data integration

AskOmics convert project specific data into RDF triples automatically. It can convert CSV/TSV, GFF and BED files. It can also integrate RDF data.

!!! Hands-on
    Download the files for the tutorial using the following links:<br />
    - [Differentially expressed results file](https://zenodo.org/record/2529117/files/limma-voom_luminalpregnant-luminallactate)<br />
    - [Reference genome annotation file](https://zenodo.org/record/3601076/files/Mus_musculus.GRCm38.98.subset.gff3)<br />
    - [Correspondence file between gene symbol and Ensembl id](https://zenodo.org/record/3601076/files/symbol-ensembl.tsv)<br />
    - [QTL file](https://zenodo.org/record/3601076/files/MGIBatchReport_Qtl_Subset.txt)

## Data upload

The first step is to upload the input files into AskOmics. Go on the *Files* page by clicking on <navbar><i class="fa fa-file"></i> Files</navbar>.


You can upload files from your computer, or distant files using an URL.

!!! Hands-on
    Upload the files `limma-voom_luminalpregnant-luminallactate`, `Mus_musculus.GRCm38.98.subset.gff3`, `symbol-ensembl.tsv` and `MGIBatchReport_Qtl_Subset.txt` from your computer into AskOmics


Uploaded files are displayed into the files table. Filenames can be change by clicking on it.

![files_table](img/files_table.png "files_table")

Next step is to convert this files into RDF triples. This step is called *Integration*. Integration will produce a RDF description of your data: the *Abstraction*.

!!! Hands-on
    Select the four files and click on <btn><i class="fa fa-database"></i> Integrate</btn>


## Integration

The *integration* convert input files into RDF triples, and load them into an RDF triplestore. AskOmics can convert CSV/TSV, GFF3 and BED files.

### GFF

GFF files contain genetic coordinate of entities. Each entities contained in the GFF file are displayed on the preview page. Select the entities you want to integrate.

!!! Hands-on
    1. Search for `Mus_musculus.GRCm38.98.subset.gff3 (preview)`
    2. Select `gene` and `mRNA`
    3. **Integrate (private dataset)**


### CSV/TSV

The TSV preview show an HTML table representing the TSV file. During integration, AskOmics will convert the file using the header.

<!-- First col: entity, then, attribute -->
The first column of a TSV file will be the *entity* name. Other columns of the file will be *attributes* of the *entity*. *Labels* of the *entity* and *attributes* will be set by the header. This *labels* can be edited by clicking on it.  

<!-- Attribute types -->
Entity and attributes can have special types. The types are defined with the select below the header. An *entity* can be a *start entity* or an *entity*. A *start entity* mean that the entity may be used to start a query.

Attributes can take the following types:
- Numeric: if all the values are numeric
- Text: if all the values are strings
- Category: if there is a limited number of repeated values

If the entity describe a locatable element on a genome:
- Reference: chromosome
- Strand: strand
- Start: start position
- End: end position

<!-- Relation -->
A columns can also be a relation between the *entity* to another. In this case, the header have to be `relationName@TargetedEntity` and the type *Directed* or *Symmetric* relation. a *Directed* relation is a relation from this entity to the targeted one. A *Symetric relation* is a relation on both directions.

!!! Hands-on
    1. Search for `limma-voom_luminalpregnant-luminallactate (preview)`
    2. Edit attribute names and types:
        - change `ENTREZ ID` to `Differential Expression` and set type to *start entity*
        - change `SYMBOL` to `linkedTo@GeneLink` and set type to *Symmetric relation*
        - change `GENENAME` to `name` and set type to *text*
        - Keep the other column names and set their types to *numeric*
    3. **Integrate (private dataset)**

    ![De results preview](img/de_results_preview.png)

!!! Hands-on
    1. Search for `symbol-ensembl.tsv (preview)`
    2. Edit attribute names and types:
        - change `symbol` to `GeneLink` and set type to *entity*
        - change `ensembl` to `linkedTo@gene` and set type to *Symmetric relation*
    3. **Integrate (private dataset)**

    ![Symbol to Ensembl preview](img/symbol_to_ensembl_preview.png)

!!! Hands-on
    1. Search for `MGIBatchReport_Qtl_Subset.txt (preview)`
    2. Edit attribute names and types:
        - change `Input` to `QTL` and set type to *start entity*
        - set `Chr` type to *Reference*
        - set `Start` type to *Start*
        - set `End` type to *End*
    3. **Integrate (private dataset)**

    ![QTL preview](img/qtl_preview.png)


### Manage integrated datasets


Integration can take some times depending on the file size. The **Datasets** page show the progress.

!!! Hands-on
    1. Go to **Dataset** page
    2. Wait for all datasets to be *success*

    ![dataset](img/datasets.png "Datasets table")



The table show all integrated datasets. The *status* column show if the datasets is fully integrated or in the process of being integrated. You can delete datasets independently.



# Query

Once all the data of interest is integrated (converted to RDF graphs), its time to query them. Querying RDF data is done by using the SPARQL language. Fortunately, AskOmics provides a user-friendly interface to build SPARQL queries without having to learn the SPARQL language.

## Query builder overview

### Simple query

The first step to build a query is to choose a start point for the query.

![ask](img/startpoint.png)


!!! Hands-on
    1. Go to **Ask!** page
    2. Select the *Differential Expression* entity
    3. **Start!**


Once the start entity is chosen, the query builder is displayed.


The query builder is composed of a graph. Nodes represents *entities* and links represents *relations* between entities. The selected entity is surrounded by a red circle. links and other entities are dotted and lighter because there are not instantiated.

![query builder](img/query_builder.png "Query builder, Differential Expression is the selected entity, GeneLink is a suggested entity")

On the right, attributes of the selected entity are displayed as attribute boxes. Each boxes have an eye icon. Open eye mean the attribute will be displayed on the results.

!!! Hands-on
    1. Display `logFC` and `adj.P.val` by clicking on the eye icon
    2. **Run & preview**

![preview results](img/preview_results.png "Results preview")

**Run & preview** launch the query with a limit of 30 rows returned. We use this button to get an idea of the results returned.


### Filter on attributes

Next query will search for all over-expressed genes. Genes are considered over-expressed if the log fold change is > 2. We are oly interested by  significant results (Adj P value ≤ 0.05)

Back to the query builder,

!!! Hands-on
    1. Filter `logFC` with `> 2`
    2. Filter `adj.P.val` with `≤ 0.05`
    2. **Run & preview**

The preview show only significantly over-expressed genes.


### Filter on relations

now that we have our genes if interest, we will link these genes to the reference genome to get information about location.

To constraint on relation, we have to click on suggested nodes, linked to our entity of interest.

!!! Hands-on
    1. First, hide `Label`, `logFC` and `adj.P.val` of `Differential Expression`
    2. Instantiate `GeneLink`, and hide `Label`
    3. Instantiate `gene`
    2. **Run & preview**

Results now show the Ensembl id of our over-expressed genes. We have now access to all the information about the `gene` entity containing on the GFF file. for example, we can filter on chromosome and display chromosome and strand to get information about gene location.

!!! Hands-on
    1. Show `reference` and `strand` using the eye icon
    2. Filter `reference` to select `X` and `Y` chromosomes (use `ctrl`+`click` to multiple selection)
    2. **Run & preview**

### Use FALDO ontology to query on the position of elements on the genome.

The [FALDO](https://bioportal.bioontology.org/ontologies/FALDO) ontology describe sequence feature positions and regions. AskOmics use FALDO ontology to represent entity positions. GFF are using FALDO, as well as TSV entities with chromosome, strand, start and end.

The FALDO ontology are used in AskOmics to perform special queries between 2 FALDO entities. These queries are:

- Entity included in another entity
- Entity overlapping another one

On the query builder interface, FALDO entities are represented with a green circle and FALDO relations have a green arrow.

!!! Hands-on
    1. First, remove the reference filter (unselect `X` and `Y` using `ctrl`+`click`)
    2. Hide `strand` using the eye
    3. Instantiate `QTL`
    4. Click on the link between `gene` and `QTL` to edit the relation
    5. check that the relation is `gene` `included in` `QTL` `on the same reference` with `strict` ticked
    7. **Run & preview**


To go further, we can filter on `QTL` to refine the results.


!!! Hands-on
    1. got back to the `QTL` node
    2. Show the `Name` attribute using the eye icon
    3. Filter the name with a `regexp` with `growth`
    4. **Run & preview**

From now, our query is "All Genes that are over-expressed (logFC > 2 and FDR ≤ 0.05) and located on a QTL that are related to growth" This is the results that we are looking for. So we can save it.

!!! Hands-on
    1. **Run & save**
    2. Got to the **Results** page


## Results management

The results page store the saved queries. A table show some useful information about the queries. Query name can be edited by clicking on it.

![results table](img/results_table.png)

!!! Hands-on
    1. Click on the name and enter `Over-expressed genes on a growth QTL`
    2. press `enter` key

The **Action** column contain button to perform certain action:

- Preview: show a results preview on the bottom of the table
- Download: Download the results (TSV file)
- Edit: Edit the query with the query builder
- SPARQL: edit the query with a SPARQL editor for advanced users


