# SHACL to SQL Experiment Repository

This repository contains all information related to the experiments performed for the paper "Compiling SHACL into SQL".

## Paper and ISWC 2024 Slides

- You can find the paper in the pre-print [here](https://drive.google.com/file/d/1P0OXnCLzpSk442kumc1_lTHdkVZhifLg/view).
- The slides can be found [here](https://www.mjakubowski.info/files/slides/iswc2024.pdf).

## Information on shapes
Generally, folders that end on `_shapes` contain the SHACL shapes used to perform experiments;
- `benchmark_shapes` contains all the Tyrolian KG benchmark shapes
- `benchmark_shapes_selection` contains the 10 selected shapes used for our experiments
- `benchmark_shapes_dummy` is a copy of the previous, but where all shapes now target subjects of `rdf:type`
- `synthetic_shapes` contains all shapes related to our synthetic experiments
- `synthetic_shapes_travshacl` is a subset of the synthetic shapes that could be executed with TravSHACL
- `dblp_shapes` contains our three shapes used for the DBLP experiment

## Information on data
The data can be downloaded from https://zenodo.org/doi/10.5281/zenodo.10980025 and should be put in the respective folders.

Generally, folders that end on `_data` contains RDF data related to the experiments. To use the data with DuckDB, it first needs to be converted to a DuckDB database. Code to do this can for example be found in `sqltools/synthetic_experiments.py`, but the databases can also be found in the `sqltools/wd_*` directories.
To use the data with Jena SHACL using TDB, you should load the data into a TDB database first, using the Jena tool `tdbloader`. Generally, the data should be stored in `sqltools/wd_*`.

### Benchmark experiments
The `benchmark_data` folder (which can be found after unpacking, see above) contains files of 10, 15 and 20 million triple (random) subsets of the 30 million triple knowledge graph from the SHACL benchmark paper.

### Synthetic experiments
The `synthetic_data` folder (which can be found after unpacking, see above) contains directories for every shape number. In these directories, you can find datasets of sizes 1 to 5 million, 10 million, 15 million and 20 millions triples. This is generated for each shape, using our data generators. We give a detailed description of these data generators. The specific parameters can be found in the files `sqltools/synthetic_parallel_data_generatorX.sh`.
- Shape 1: generate `H` humans, `P` phone numbers and `E` email addresses. Give every human between `P1` and `P2` phone numbers with probability `Pp`, and between `E1` and `E2` email addresses with probability `Pe`.
- Shape 2: generate `H` humans, and `M` managers. The number of managers for every human is between `M1` and `M2`.
- Shape 3: generate `H` humans, `F` friends and `C` companies. Every human has a number of friends (within some range). Every friend is the CEO of a number of companies within some range. 
- Shape 4: we will simplify our description from now. There are two disjoint sets of humans and “others” which serve as friends or colleagues. Every human gets (uniformly random, within some range) a number of friend properties to “others”. Similarly with a number of colleague properties.
- Shape 5: there is a set of humans, objects and properties. Every human gets assigned a certain number of properties to a range of objects.
- Shape 6: there is a set of humans, phone numbers and emails. Every human gets a number of phone numbers and a number of emails, based on some probability
for each.
- Shape 7: same data as previous
- Shape 8: there is a set of humans and a set of objects. With some probability, for every human, property1 and property2 reach exactly the same objects.
- Shape 9: there is a set of humans, objects (the firstnames), and languages. Each human gets a range of firstnames which all have random language tag.
- Shape 10: there is a set of humans which all get a number of start and end dates which all fall within a range. There “dates” are simply integers.

### DBLP experiments
The data can be found in the `sqltools/dblp_data` folder (which can be found after unpacking, see above). Specifically for the year 2023, but also for 2022 and 2023 combined. The subsets were generated from the full DBLP database. We loaded it into Jena TDB and using SPARQL CONSTRUCT queries, obtained the desired subsets. These queries can be found in the `sqltool/sparql` folder. The scripts in those folders represent the workflow to obtain the datasets.

## Running the experiments
Make sure you are within a python virtual environment with all packages mentioned in `requirements.txt` installed there. It is also necessary to install all Apache Jena command line tools, like `tdbloader`, `shacl`, etc. Also, we used Apache Jena Fuseki as our SPARQL endpoint.

The main experiment scripts: `*_experiments.py` and `*_experiments.sh` often have a `root` variable that should be set to the full path to the `sqltools` folder. Similarly, the fuseki config files (like `fuseki-config5.ttl`) should point to the full path of the TDB location.

All experiments were run using a combinations of the scripts in this repository. The experiments for the paper were run using the scripts `sqltools/batch_*.sh`. The idea is that it is specific to a specific experiment: `bench`, `synth` or `dblp`, and specific to a validation engine `jena`, `travshacl` or `shuq` (for the translation approach). Generally, they output CSV files to the `sqltools/results` directory.

For the TravSHACL results relating to the synthetic experiments, you need to make sure there is a SPARQL endpoint running on localhost. We used Apache Jena Fuseki for this, with the config file `fuseki-config5.ttl` to start a SPARQL endpoint for the 5 synthetic shapes with their corresponding datasets of size 5 milllion triples. There are also config files for 10 and 20 million triples.

The core test suite can be run using the `sqltools/core_test_suite_experiment.py` file. 

## Information on the modules

### JSTimer
The folder `JSTimer` contains the source code for the java program used to measure Apache Jena SHACL and TopQuadrant SHACL. It supports many experiment related features. A compiled jar file can be found in the folder `sqltools/jstimer/jstimer3.jar`. An example of running this program to obtain the validation time in milliseconds is:
    
    java -jar jstimer/jstimer3.jar -v -j -t SHAPEFILE DATALOC

where you can ignore the `-v` parameter, `-j` means "validate with Jena" (`-t` here for TopQuadrant), `-t` means to use a TDB database at location `DATALOC`. Alternatively `-m` means to use a file, for example a turtle file.

### Translation package: `shuq`
The python package `shuq` located in the `sqltools` folder contains all code relating translating shape expressions into SQL over the relational schema defined in the paper. The module `querylib` contains all SQL templates for translating shape expressions. The module `unaryquery` contains the central function `translate_node` which translates a parse tree node representing a shape expression, into a SQL query. The function `translate_conformance_shape` translates a shape definition into a query retrieving (by default) all violations for that shape: all targets that do not conform to the shape expression. If `target_all = True`, then it simply retrieves all nodes conforming to the shape expression (ignoring the targets). 

To get an idea of the output of `shuq`, the `sqltools/shuq_cli.py` program is a simple program that prints the parse tree of your shape, together with the translated SQL query. Usage:

    python shuq_cli.py SHAPENAME

### Database loader package: `converter`
The python package `converter` contains functionality to turn turtle files into a DuckDB database. For data that does not fit in memory, it uses the `rdflib` BerkeleyDB Store plugin to first load the data into an intermediate representation. This significantly increases the duration of graph operations. 

## Information on synthetic shape 7
We reused the dataset for shape 6 to also test shape 7. In retrospect
that was careless, as this dataset has a lot of subjects but very few
objects, so there are very few targets. SQL retrieves all persons and
subtracts these from the small list of emails. It still does this in 1
second, but Jena just looks at the very few targets. We already noted
in the Tyrol experiments that small target sizes skew the
comparison. 

In the folder `extra_shape7/` you can find a more balanced dataset
(and an ad-hoc data generator) to rerun the synthetic experiments and
see that the quirk disappears.
