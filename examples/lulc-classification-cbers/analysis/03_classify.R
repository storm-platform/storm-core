set.seed(777)
library(sits)

source("analysis/.pipeline.R")

#
# Output directory
#
output_dir <-
    paste(.pipeline_definitions$output_base,
          .pipeline_definitions$collection,
          sep = "/")
dir.create(path = output_dir,
           showWarnings = FALSE,
           recursive = TRUE)

#
# Load trained model
#
trained_model_dir <-
    paste(.pipeline_definitions$output_base,
          .pipeline_definitions$collection,
          sep = "/")

trained_model <- readRDS(paste(trained_model_dir, "ml_model.rds", sep = "/"))

#
# Data Cube
#
cube <- sits_cube(
    source = "BDC",
    name = "cube_to_extract_sample",
    collection = .pipeline_definitions$collection,
    start_date = .pipeline_definitions$start_date,
    end_date = .pipeline_definitions$end_date,
    bands = .pipeline_definitions$bands,
    tiles = .pipeline_definitions$tiles
)

#
# Create LULC Map using the data cube
#

# define the classification roi
roi <- readRDS("data/raw_data/roi.rds")

probs <- sits_classify(
    data = cube,
    ml_model = trained_model,
    memsize = .pipeline_definitions$memsize,
    multicores = .pipeline_definitions$multicores,
    output_dir = output_dir,
    roi = roi$classification_roi,
)

#
# Post-processing
#
probs_smoothed <- sits_smooth(
    probs,
    type = "bayes",
    output_dir = output_dir,
    memsize = .pipeline_definitions$memsize,
    multicores = .pipeline_definitions$multicores
)

labels <-
    sits_label_classification(cube = probs_smoothed,
                              output_dir = output_dir)

#
# Saving results
#

# labels
saveRDS(labels, file = paste(output_dir, "labels.rds", sep = "/"))

# probs
saveRDS(probs, file = paste(output_dir, "probs_cube.rds", sep = "/"))

# smoothed probs
saveRDS(probs_smoothed,
        file = paste(output_dir, "probs_smoothed_cube.rds", sep = "/"))

