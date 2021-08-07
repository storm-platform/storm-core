set.seed(777)
library(sits)

#
# Auxiliary function
#
extract_ts_by_sample_location <- function(collection, start_date, end_date, bands, tiles, sample_file) {
  cube <- sits_cube(
    source      = "BDC",
    name        = "cube_to_extract_sample",
    collection  = collection,
    start_date  = start_date,
    end_date    = end_date,
    bands       = bands,
    tiles       = tiles
  )

  samples <- sits_get_data(cube = cube, file = sample_file, multicores = 8)
  samples
}

#
# General definitions
#
start_date  <- "2018-09-14"
end_date    <- "2019-07-28"
sample_file <- "data/raw_data/training-samples.csv"

#
# Output directory
#
output_dir <- paste("data", "derived_data", sep = "/")
dir.create(
  path         = output_dir,
  showWarnings = FALSE,
  recursive    = TRUE
)

#
# CBERS-4/AWFI (16 days 'stack')
#
cb4_samples_with_ts <- extract_ts_by_sample_location(
  collection  = "CB4_64_16D_STK-1",
  start_date  = start_date,
  end_date    = end_date,
  bands       = c("BAND15", "BAND14", "BAND13", "BAND16", "NDVI", "EVI"),
  sample_file = sample_file,
  tiles       = "022024"
)
saveRDS(cb4_samples_with_ts, paste0(output_dir, "/CB4_64_16D_STK_1.rds"))
