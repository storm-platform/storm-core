set.seed(777)
library(sits)

source("analysis/.pipeline.R")

#
# Output directory
#
output_dir <-  paste(
  .pipeline_definitions$output_base, .pipeline_definitions$collection, sep = "/")

dir.create(path         = output_dir,
           showWarnings = FALSE,
           recursive    = TRUE)

#
# Data Cube
#
cube <- sits_cube(
  source      = "BDC",
  name        = "cube_to_extract_sample",
  collection  = .pipeline_definitions$collection,
  start_date  = .pipeline_definitions$start_date,
  end_date    = .pipeline_definitions$end_date,
  bands       = .pipeline_definitions$bands,
  tiles       = .pipeline_definitions$tiles
)

#
# Extracting samples
#
samples_with_ts <- sits_get_data(
  cube       = cube,
  file       = .pipeline_definitions$sample_file,
  multicores = .pipeline_definitions$multicores
)

#
# Saving the extracted time series
#
saveRDS(samples_with_ts, paste(output_dir, "samples_with_ts.rds", sep = "/"))
