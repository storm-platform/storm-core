.pipeline_definitions <- list(
  start_date      = "2018-09-14",
  end_date        = "2019-07-28",
  collection      = "CB4_64_16D_STK-1",
  sample_file     = "data/raw_data/training-samples.csv",
  bands       = c(
    "BAND15", "BAND14", "BAND13", "BAND16", "NDVI", "EVI"
  ),
  tiles      =  "022024",
  output_base = "data/derived_data",
  memsize  = 12,
  multicores = 8
)
