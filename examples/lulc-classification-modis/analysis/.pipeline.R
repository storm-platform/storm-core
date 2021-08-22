.pipeline_definitions <- list(
  start_date      = "2000-09-13",
  end_date        = "2016-08-28",
  collection      = "MOD13Q1-6",
  sample_file     = "data/raw_data/training-samples_mt.csv",
  bands       = c(
    "NDVI",
    "EVI",
    "blue_reflectance",
    "red_reflectance",
    "NIR_reflectance",
    "MIR_reflectance"
  ),
  tiles      =  "012010",
  output_base = "data/derived_data",
  memsize  = 7,
  multicores = 4
)
