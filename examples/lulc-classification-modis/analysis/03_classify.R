set.seed(777)
library(sits)

source("analysis/.pipeline.R")
source("analysis/supercube.R")

#
# CLI (`temporal_group_index`)
#
args <- commandArgs(TRUE)

#
# Validating CLI input
#
temporal_group_index <- as.numeric(args[1])

if (is.na(temporal_group_index)) {
    stop(sprintf("You need to specify a valid `temporal_group_index`"),
         call. = FALSE)
}

#
# Load trained model
#
trained_model_dir <-
    paste(.pipeline_definitions$output_base,
          .pipeline_definitions$collection,
          sep = "/")

trained_model <- readRDS(paste(trained_model_dir, "ml_model.rds", sep = "/"))

#
# Samples with time series
#
samples_with_ts <- readRDS(paste(
    .pipeline_definitions$output_base,
    .pipeline_definitions$collection, "samples_with_ts.rds",
    sep = "/"
))

# Temporal group
temporal_group <-
    sort(unique(samples_with_ts$start_date))[[temporal_group_index]]

#
# Output directory
#
output_dir <-
    paste(
        .pipeline_definitions$output_base,
        .pipeline_definitions$collection,
        "classification",
        paste("temporal_group", temporal_group, sep = "_"),
        sep = "/"
    )
dir.create(path = output_dir,
           showWarnings = FALSE,
           recursive = TRUE)

#
# Create a cube for the temporal group
#
cube <- make_cube_by_samples_temporal_groups(
    samples = samples_with_ts,
    temporal_group = temporal_group,
    collection = .pipeline_definitions$collection,
    bands = .pipeline_definitions$bands,
    tiles = .pipeline_definitions$tiles
)

#
# Create LULC Map using the data cube
#
probs <- sits_classify(
    data = cube,
    ml_model = trained_model,
    memsize = .pipeline_definitions$memsize,
    multicores = .pipeline_definitions$multicores,
    output_dir = output_dir
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
