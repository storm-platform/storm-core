.pipeline_definitions <- list(
  start_date      = "2018-09-14",
  end_date        = "2019-07-12",
  collection      = "LC8_30_16D_STK-1",
  sample_file     = "data/raw_data/training-samples.csv",
  bands       = c(
    "NDVI",
    "EVI",
    "B2",
    "B3",
    "B4",
    "B5",
    "B6",
    "B7"
  ),
  tiles      =  c("045049", "045048", "044049", "044048"),
  output_base = "data/derived_data",
  memsize  = 12,
  multicores = 8
)
