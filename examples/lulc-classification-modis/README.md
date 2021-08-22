
<!-- README.md is generated from README.Rmd. Please edit that file -->

## Land Use and Land Cover Classification (MOD13Q1)

In this example, `bdcrrm-api` is used for the reproducible production of
**L**and **U**se and **L**and **C**over (LULC) maps using the R
programming language and the [SITS analytical
package](github.com/e-sensing/sits).

> The data used in this example is retrieved from the STAC service of
> the Brazil Data Cube (BDC) project, which requires an access key to
> use the data. If you do not have an access key, create one via [BDC
> Explorer](https://brazildatacube.dpi.inpe.br/portal/explore).

In this example, the classification methodology presented in the article
[Land use and cover maps for Mato Grosso State in Brazil from 2001 to
2017](https://www.nature.com/articles/s41597-020-0371-4) is applied.
This is done by classifying 16 years of data (2000-2016) MOD13Q1 from
the state of Mato Grosso.

The processing flow implemented in this example is illustrated in the
Figure below:

<div align="center">

<img src="./figures/example-modis-workflow.png" width="60%" style="display: block; margin: auto;" />

</div>

As illustrated in the flowchart above, initially, the time series
extraction is performed. Next, the training of the Machine Learning
model, Support Vector Machine, is performed. Finally, after training the
model, it is applied to 16 years of data individually.

> In the individual mode, multiple data cubes are created, and then the
> data from each cube is used to create the classification map. In each
> cube, you have only one year of data.

To run this example, make the settings in the `pipeline.sh` script. In
this case, set the variable `BDC_ACCESS_KEY`, with your token to access
the BDC services.

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
> **Adding secrets**

``` shell
bdcrrm project settings secrets add BDC_ACCESS_KEY
```

After the secret definition, the scripts can be run through
`bdcrrm-api`:

**Running the pipeline**

``` shell
./pipeline.sh
```

> **Note**: The script can take quite a while to execute. Be sure to
> check the computational resource configuration in the file
> `analysis/.pipeline.R`.

After the script runs, the generated data will be in the following
structure:

    ├── derived_data
    │   └── MOD13Q1-6
    │       └── classification
    │           ├── temporal_group_2000-09-13
    │           ├── temporal_group_2001-09-14
    ...         ...                       ...
    │           ├── temporal_group_2013-09-14
    │           ├── temporal_group_2014-09-14
    │           └── temporal_group_2015-09-14
    └── raw_data