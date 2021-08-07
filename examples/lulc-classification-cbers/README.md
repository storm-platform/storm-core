
<!-- README.md is generated from README.Rmd. Please edit that file -->

## Land Use and Land Cover Classification (CBERS-4/AWFI)

In this example, `bdcrrm-api` is used for the reproducible production of
maps of **L**and **U**se and **L**and **C**over (LULC) using the R
programming language and the [SITS analytical
package](github.com/e-sensing/sits).

> The data used in this example is retrieved from the STAC service of
> the Brazil Data Cube (BDC) project, which requires an access key to
> use the data. If you do not have an access key, create one via [BDC
> Explorer](https://brazildatacube.dpi.inpe.br/portal/explore).

### Running

Before you start running, remember to set the environment variable
`BDC_ACCES_KEY` to the value of your service access key, for example:

``` shell
export BDC_ACCESS_KEY=MY_KEY_VALUE
```

> Since `bdcrrm-api` saves all the operating system information being
> used, environment variables are also saved. To prevent environment
> variables with sensitive information such as the `BDC_ACCESS_KEY`
> variable from being shared improperly, `bdcrrm-api` introduced the
> concept of `secrets`. These filters remove all environment variables
> with the defined nomenclature, allowing the use of databases and web
> services (e.g., STAC, WTSS, and AWS) that depend on a token or
> user/password as environment variables without exposing credentials.

**Adding secrets**

``` shell
bdcrrm project settings secrets add BDC_ACCESS_KEY
```

After the secret definition, the scripts can be run through
`bdcrrm-api`:

**1. Extracting time series**

``` shell
bdcrrm-cli production make 'Rscript analysis/01_extract_ts.R'

#> bdcrrm-cli: Reproducible execution
#> SITS - satellite image time series analysis.
#> Loaded sits v0.12.0.
#>         See ?sits for help, citation("sits") for use in publication.
#>         See demo(package = "sits") for examples.
#> Using configuration file: /home/felipe/R/x86_64-pc-linux-gnu-library/4.0/sits/extdata/config.yml
#> To provide additional configurations, create an yml file and set environment variable SITS_USER_CONFIG_FILE to point to it
#> All points have been retrieved
#> Some files were read and then written. We will only pack the final version of the file; reproducible experiments shouldn't change their input files
#> Configuration file written in .bdcrrm/executions/531366cc-2a0b-4b9e-89f4-8f5f5e3ee975/config.yml
#> Edit that file then run the packer -- use 'reprozip pack -h' for help
```

**2. Classify time-series extracted from the CBERS Data Cube**

``` shell
bdcrrm-cli production make 'Rscript analysis/02_classify.R'

#> SITS - satellite image time series analysis.
#> Loaded sits v0.12.0.
#>         See ?sits for help, citation("sits") for use in publication.
#>         See demo(package = "sits") for examples.
#> Using configuration file: /home/felipe/R/x86_64-pc-linux-gnu-library/4.0/sits/extdata/config.yml
#> To provide additional configurations, create an yml file and set environment variable SITS_USER_CONFIG_FILE to point to it
#> Some files were read and then written. We will only pack the final version of the file; reproducible experiments shouldn't change their input files
#> Configuration file written in .bdcrrm/executions/98eaf6f5-88cb-4a2e-8bec-a8531cf18b66/config.yml
#> Edit that file then run the packer -- use 'reprozip pack -h' for help
```

Now, when viewing the general project information, you have:

``` shell
bdcrrm-cli project info --graph

#> bdcrrm-cli: Project details
#> Name:
#>          lulc-classification
#> Description:
#>          Reproducible Land Use and Land Cover classification using the SITS analytical package.
#> Author:
#>          Felipe Menino
#> Created at:
#>          2021-08-05 00:06:40.747788
#> Execution Graph:
#> * 0 (Rscript analysis/01_extract_ts.R)
#> * 1 (Rscript analysis/02_classify.R)
```

Finally, the project can be exported and shared, which allows others to
reproduce the project and its results.

``` shell
bdcrrm-cli project shipment export --output-dir lulc_classification_project

#> bdcrrm-cli: Project Export
#> bdcrrm-cli: Validating the project...
#> bdcrrm-cli: Exporting the project!
#> bdcrrm-cli: Finished!
```

### Comparing results

To confirm that the reproduced results are the same as those generated
in the original experiments, we will compare the two generated LULC maps
below. So, initially, the saved project (in `.zip` format) is imported
as a new project:

``` shell
bdcrrm-cli project shipment import -f lulc_classification_project/lulc-classification-cbers.zip -d imported_project
```

The imported project and its contents are available in the directory
`imported_project/lulc-classification-cbers`:

``` shell
cd imported_project/lulc-classification-cbers
```

In this directory, you can retrieve the project information as well as
re-execute the project. For the second case, you will need to configure
the \`secrets’ removed from the package. When you look at the project
secrets, you have:

``` shell
bdcrrm-cli project settings secrets list

#> bdcrrm-cli: Secrets settings
#> bdcrrm-cli: Listing secrets
#> Project Secrets              
#> └── BDC_ACCESS_KEY 
```

As expected, the value of the environment variable `BDC_ACCESS_KEY` is
not available in the package and needs to be set before reproducing the
results. Therefore, it is necessary to create a file and then insert the
name of the environment variables and their respective values in each
line. In `bdcrrm-api`, this file is already created at import time in
the root of the imported project with the name **secrets**. In this
file, all the variables needed to re-run the project are listed:

``` shell
cat secrets

#> BDC_ACCESS_KEY
```

In this case, only `BDC_ACCESS_KEY` needs to be set, so go to the
**secrets** file and fill in its value with your access key to the BDC
services.

``` shell
cat secrets

#> BDC_ACCESS_KEY=YOU_BDC_ACCESS_TOKEN
```

After this, the reproduction can be performed:

``` shell
bdcrrm-cli reproduction make -s secrets

#> bdcrrm-cli: Project reproduction.
#> bdcrrm-cli: Loading required secrets.
#> bdcrrm-cli: Reproducing the project.
#> Reproducing: Rscript analysis/01_extract_ts.R
#> Checksum: 122040399b43e8fe2d619a6f6ebaa6e3246a22d918703de494bda93ff44611689871
#> Reproducing: Rscript analysis/02_classify.R
#> Checksum: 122029022e8a97eb22bffab2f503d593d638473bf91da6895cdd423dee81b3ffb349
```

At the end of the processing, the results will be available in the
`results` directory. When comparing the LULC map generated in the
original run and the reproduction run, you have:

<img src="./figures/results_difference.png" width="95%" style="display: block; margin: auto;" />

The results are the same, indicating that even when run in different
environments, the controls offered by `bdcrrm-api` help reproduce the
results.
