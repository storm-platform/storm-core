set.seed(777)
library(sits)

source("analysis/.pipeline.R")

#
# Samples with time series
#
samples_with_ts <- readRDS(paste(
  .pipeline_definitions$output_base,
  .pipeline_definitions$collection, "samples_with_ts.rds",
  sep = "/"
))

#
# Output directory
#
output_dir <-
  paste(.pipeline_definitions$output_base,
        .pipeline_definitions$collection,
        sep = "/")
dir.create(path         = output_dir,
           showWarnings = FALSE,
           recursive    = TRUE)

#
# Defining the SVM Model
#
svm_model <- sits_svm()

#
# Training the model
#
trained_model <- sits_train(samples_with_ts, svm_model)

#
# Saving the model
#
saveRDS(trained_model, file = paste(output_dir, "ml_model.rds", sep = "/"))
