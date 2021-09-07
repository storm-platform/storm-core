
<!-- README.md is generated from README.Rmd. Please edit that file -->

## bdcrrm-api - Data Management

Managing research data that is to be published is an important step for
many projects. For example, there may be research projects where the
data cannot be published for ethical reasons. Another example is work
that uses large volumes of data, where sharing the entire dataset may
make the reproducible publication of the research impossible.

To help manage and control the data used during a survey, `bdcrrm-api`
has `Data Management` modules. This module provides features that
facilitate the determination and control of the data that may or may not
be published with the code and the environment used in the research
experiments.

Thus, in this example, we will present the `Data Management` module and
its functionalities. For this presentation, the processing of image
collections as a data cube using the R package
[gdalcubes](https://github.com/appelmar/gdalcubes_R) is used as an
example.

### Code and Data

The code used in this example is taken from the [official gdalcubes page
on GitHub](https://github.com/appelmar/gdalcubes_R). This code processes
a collection of scenes, representing them as a data cube, applying
spatial and temporal aggregations to the data.

For the data, use is made of a collection of Landsat-8/OLI scenes, made
available on [official gdalcubes page on
GitHub](https://github.com/appelmar/gdalcubes_R). This dataset will be
used because it is versatile and provides several files, being a good
example for the presentation of the `Data Management` functionalities in
bdcrrm-api, exposing the necessity of this module’s existence.

### Running

To begin with, the first activity to be performed is to download the set
of Landsat-8/OLI scenes that will be used as input to the processing
script. For this, you can use the `download.sh` script, available in the
`auxiliary` directory:

``` sh
./auxiliary/download.sh
```

Running the script will download and extract the data into the
`lc8_scenes/uncompress/L8_Amazon` directory. To confirm that the data
has been downloaded, list the contents of the directory. The result of
the operation should look like the example shown below:

``` sh
ls lc8_scenes/uncompress/L8_Amazon

#> drwxrwxrwx   2 felipe felipe 4,0K jul 16  2019 LC082260632014071901T1-SC20190715045926
#> drwxrwxrwx   2 felipe felipe 4,0K jul 16  2019 LC082260632014082001T1-SC20190715051515
#> drwxrwxrwx   2 felipe felipe 4,0K jul 16  2019 LC082260632016011401T2-SC20190715045725
#> ...
```

Now, to use this data as input, we will move it to the
`data/raw_data/L8_Amazon` directory, which will be used in the
processing script:

``` sh
mv lc8_scenes/uncompress/L8_Amazon data/raw_data/L8_Amazon
```

Now that the data is ready for use let’s consider that this data should
not be saved in the reproducible package created by bdcrrm-api. To do
this, in bdcrrm-api, we can use `datasources`. These represent the
directories/files on the file system used as input data for the
experiment. Using `datasources`, the user can specify to bdcrrm-api
which data should or should not be considered when creating the
reproducible package.

First, let’s look at the options available for `datasources` management:

``` sh
bdcrrm-cli project settings datasources

#> Usage: bdcrrm-cli project settings datasources [OPTIONS] COMMAND [ARGS]...
#> 
#>   Project settings for datasources.
#> 
#>   As with the `working directories`, `bdcrrm-api`, at the time of creating the
#>   reproducibility package, determines which data files will be saved based on
#>   the project directory.
#> 
#>   Sometimes the data used may be in other directories. In order for these to
#>   be included in the package, it is necessary to add them as `data sources`
#>   for the project.

#>   Note:     Unlike a `working directory`, which is used to determine the
#>   inputs/outputs, the `data sources`     are used to determine which data will
#>   be inserted into the replay package, and do not influence     the definition
#>   of the inputs/outputs of the runtime graph.
#> 
#> Options:
#>   --help  Show this message and exit.
#> 
#> Commands:
#>   add     Add a data sources to the project settings.
#>   list    List project defined data sources.
#>   remove  Remove a given project defined data source by name.
```

As shown in the command result, the following options are available for
managing `datasources`:

-   **add**: Specifie which directories/files should be treated as
    `datasources` of the experiment;
-   **list**: List the data sources of the experiment;
-   **remove**: Remove a data source from the experiment.

In the current project, when listing the registered `datasources` we
have:

``` sh
bdcrrm-cli project settings datasources list

#> bdcrrm-cli: Data Source settings
#> bdcrrm-cli: Listing data sources
#>     Project data-sources    
#> ┏━━━━━━┳━━━━━━━━━┳━━━━━━━━━┓
#> ┃ Name ┃ Pattern ┃ Action  ┃
#> ┡━━━━━━╇━━━━━━━━━╇━━━━━━━━━┩
#> │ foo  │ /foo/*  │ include │
#> └──────┴─────────┴─────────┘
```

In the result presented, we see a table with three columns:

-   **Name**: `datasource` name;
-   **Pattern**: [fnmatch
    pattern](https://docs.python.org/3/library/fnmatch.html) used to
    determine which files/directories belong to this `datasource`. Here,
    you can specify any valid `fnmatch pattern`;
-   **Action**: Action to take with the identified files/directories
    with the Pattern set. This option can have the value `include`,
    which indicates that this data should be added to the reproducible
    package if it is to be used in the experiment. It can also have the
    value `exclude`, which specifies that the data should not be
    inserted into the reproducible package.

> In the current version of bdcrrm-api, all files are added to the
> reproducible package, so the user must specify only the `datasources`
> that should not be added to the package.

Thus, evaluating `datasource` foo, which is added automatically on
project creation, it represents that all files and directories below
`/foo` should be considered part of the experiment.

To add a new `datasource`, you can use the **add** option. Here we must
define the same information as in the table above. So, considering the
case of data in the `data/raw_data/L8_Amazon` directory that we don’t
want added to the bdcrrm-api reproducible package, we can add it as a
`datasource` and then specify that it be removed from the package:

``` sh
bdcrrm-cli project settings datasources add lc8_amazon_datasource \
    --action exclude \
    --pattern *data/raw_data/L8_Amazon/*/*.tif
```

> The `fnmatch pattern` used above indicates that, any `.tif` file,
> which is within a subdirectory of `data/raw_data/L8_Amazon`, should be
> **removed** from the reproducible package.

> If desired, you can get more information on how `fnmatch` works in the
> [official fnmatch
> documentation](https://docs.python.org/3/library/fnmatch.html).

To keep everything organized, let’s remove the `datasource` foo, created
by bdcrrm-api:

``` sh
bdcrrm-cli project settings datasources remove foo
```

Listing `datasources`:

``` sh
bdcrrm-cli project settings datasources list

#> bdcrrm-cli: Data Source settings
#> bdcrrm-cli: Listing data sources
#>                          Project data-sources                         
#> ┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┓
#> ┃         Name          ┃             Pattern              ┃ Action  ┃
#> ┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━┩
#> │ lc8_amazon_datasource │ *data/raw_data/L8_Amazon/*/*.tif │ exclude │
#> └───────────────────────┴──────────────────────────────────┴─────────┘
```

Now, specified that the input data should not be copied into the
reproducible package, let’s run the processing script:

> In this case, the processing script is on a Jupyter Notebook.
> Therefore, for execution via a terminal, we will use the
> [papermill](https://papermill.readthedocs.io/en/latest/) tool.

``` sh
bdcrrm-cli production make papermill analysis/local-cube.ipynb data/derived_data/local-cube-result.ipynb

#> bdcrrm-cli: Reproducible execution
#> Input Notebook:  analysis/local-cube.ipynb
#> Output Notebook: data/derived_data/local-cube-result.ipynb
#> Executing:   0%|                                                                                                                                 | 0/14 [00:00<?, ?cell/s]
#> Executing notebook with kernel: rgeo
#> Executing:  50%|████████████████████████████████████████████████████████████▌                                                            | 7/14 [00:14<00:14,  2.04s/cell]
#> ## Size of the cube in x direction does not align with dx, extent will be enlarged by 240.988589 at both sides.
#> ## Size of the cube in y direction does not align with dy, extent will be enlarged by 321.041455 at both sides.
#> Executing: 100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 14/14 [01:08<00:00,  4.90s/cell]
#> Configuration file written in .bdcrrm/executions/16b683a4-6b8d-4a95-ab31-4583b0c9cdea/config.yml
#> Edit that file then run the packer -- use 'reprozip pack -h' for help
```

Now that the execution has been performed, we can check which files are
not available in the reproducible package:

``` sh
bdcrrm-cli project inputs list

#> bdcrrm-cli: Project inputs
```

<details>
<summary>
Click here to visualize the excluded inputs files from package
</summary>

                   Project required input files                
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃                        Filename                         ┃
    ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
    │  LC08_L1TP_226063_20140719_20170421_01_T1_pixel_qa.tif  │
    │ LC08_L1TP_226063_20140719_20170421_01_T1_radsat_qa.tif  │
    │ LC08_L1TP_226063_20140719_20170421_01_T1_sr_aerosol.tif │
    │  LC08_L1TP_226063_20140719_20170421_01_T1_sr_band1.tif  │
    │  LC08_L1TP_226063_20140719_20170421_01_T1_sr_band2.tif  │
    .
    .
    .

</details>

<br>

There are several files, all used as input to the processing script.
Since they have been removed from the reproducible package, you must
define and specify each of these files at reproduction time. To see how
you can do this, let’s first export the project:

``` sh
bdcrrm-cli project shipment export -o reproduction/export

#> bdcrrm-cli: Project Export
#> bdcrrm-cli: Validating the project...
#> bdcrrm-cli: Exporting the project!
#> bdcrrm-cli: Finished!
```

The export step will create the file
`reproduction/export/local-cube.zip`, which can be shared with others to
reproduce the generated results.

**Reproducing**

Now, to exemplify how bdcrrm-api helps in the reproduction when there is
the need to define input files, we will reproduce the project exported
in the previous steps below. We will **fictitiously consider** that this
example step runs on a second machine, which does not have the
previously downloaded and processed data.

So, to start the reproduction, let’s first import the project:

``` sh
bdcrrm-cli project shipment import -f reproduction/export/local-cube.zip -d reproduction/import/

#> bdcrrm-cli: Project Import
#> bdcrrm-cli: Validating the files and importing the project...
#> bdcrrm-cli: The project was been imported!
#> bdcrrm-cli: The local-cube project is available on: reproduction/import/local-cube
#> bdcrrm-cli: Finished!
```

With the project imported, go to the created directory:

``` sh
cd reproduction/import/local-cube
```

In this directory, all the reproduction elements are available,
including the scripts and the computational environment. However,
especially for this project, the input data is not available. So let’s
take a look at what these files are:

``` sh
bdcrrm-cli project inputs list
#> bdcrrm-cli: Project inputs
```

<details>
<summary>
Click here to visualize the excluded inputs files from package
</summary>

                   Project required input files                
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
    ┃                        Filename                         ┃
    ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
    │  LC08_L1TP_226063_20140719_20170421_01_T1_pixel_qa.tif  │
    │ LC08_L1TP_226063_20140719_20170421_01_T1_radsat_qa.tif  │
    │ LC08_L1TP_226063_20140719_20170421_01_T1_sr_aerosol.tif │
    │  LC08_L1TP_226063_20140719_20170421_01_T1_sr_band1.tif  │
    │  LC08_L1TP_226063_20140719_20170421_01_T1_sr_band2.tif  │
    .
    .
    .

</details>

<br>

Since these files are not in the package, they will need to be inserted
into the package to reproduce the experiment. To do this, the first
thing to do is to create the **inputs specification file**. This file
stores the specification of the files that will be used as input in the
experiment in JSON format.

Let’s create this file with the command below:

``` sh
bdcrrm-cli project inputs template -f files-template.json
```

The specified file, `files-template.json`, has the structure in which
the input data should be defined for use in bdcrrm-api. As you can see
below, when loading the contents of the file, there is a JSON, with the
fields:

-   **files**: List of JSON documents with the `source` and `target`
    fields, which represent, respectively, the name of the file in the
    experiment and the location where this file is stored on the local
    machine. The bdcrrm-api will use these fields to define in the
    experiment reproduction, where each input required data is stored;
-   **checksum** (Opcional): Field to specify the checksum of the data
    being used. In the current version of bdcrrm-api, this field is
    optional.

``` sh
cat files-template.json

#> {
#>     "files": [
#>         {
#>           "source": "LC08_L1TP_229064_20180617_20180703_01_T1_sr_band4.tif",
#>           "target": ""
#>         }
#>         ...
#>     ],
#>     "checksum": []
#> }
```

So, to populate this file, we need the input data available on the
machine where the reproduction will be performed. To do this we will use
the `download.sh` script available in the `auxiliary` directory.

``` sh
./auxiliary/download.sh
```

After downloading, the downloaded data will be available in the
`lc8_scenes/uncompress/L8_Amazon` directory:

``` sh
ls -lha lc8_scenes/uncompress/L8_Amazon

#> drwxrwxrwx   2 felipe felipe 4,0K jul 16  2019 LC082260632014071901T1-SC20190715045926
#> drwxrwxrwx   2 felipe felipe 4,0K jul 16  2019 LC082260632014082001T1-SC20190715051515
#> drwxrwxrwx   2 felipe felipe 4,0K jul 16  2019 LC082260632016011401T2-SC20190715045725
#> ...
```

To populate the `files-template.json` file, bdcrrm-api has no specific
functionality since the manipulation of the input data can vary
depending on the case and the way the data is stored. Therefore, in this
example the `generate-template-files.py` script available in the
`auxiliary` directory is provided, which looks in the
`lc8_scenes/uncompress/L8_Amazon` directory and populates the
`files-template.json` file.

To run this script, use the python command as follows:

``` sh
python3 auxiliary/generate-template-files.py
```

After the script execution, the file `files-template-filled.json` will
be created, with all the fields populated with the data available in the
`lc8_scenes/uncompress/L8_Amazon` directory:

``` sh
cat files-template-filled.json

#> {
#>     "files": [
#>         {
#>           "source": "LC08_L1TP_226064_20160724_20170322_01_T1_sr_band3.tif",
#>           "target": ".../lc8_scenes/uncompress/L8_Amazon/LC082260642016072401T1-SC20190715050229/LC08_L1TP_226064_20160724_20170322_01_T1_sr_band3.tif"
#>         }
#>         ...
#>     ],
#>     "checksum": {
#>        "LC08_L1TP_228064_20130714_20170503_01_T1_sr_band6.tif": "12201fdab43b23e12f6a905b484712c03c0ab5e9edd4ab1ef9ef865202e493065200",
#>         ...
#>      }
#> }
```

Now that this file has been completed, it can be used as input for the
experiment reproduction. In this process, bdcrrm-api will validate all
files to ensure that all required inputs have been defined. If any
required input is not defined, an error will be raised.

So, the experiment reproduction, considering the input data, can be done
as follows:

``` sh
bdcrrm-cli reproduction make -i files-template-filled.json

#> bdcrrm-cli: Project reproduction.
#> bdcrrm-cli: Loading required input files.
#> bdcrrm-cli: Reproducing the project.
#> Reproducing: papermill analysis/local-cube.ipynb data/derived_data/local-cube-result.ipynb
#> Checksum: 1220df718931fce2467010993b914f1ad3b9d00a50a4390d42e8e2138dcbb893514d
```

After execution, the result will be available in the `results`
directory. Note that you can apply this way of working to any type and
format of data.