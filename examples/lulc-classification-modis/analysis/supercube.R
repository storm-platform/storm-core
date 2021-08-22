#' Creates a cube of data based on the temporal extent of a sample set. The division for this
#' function considers the initial year of sample collection.
#'
#' @param samples data.table with samples
#' @param temporal_group temporal value used to split the `samples` data
#' @param collection Data Cube collection
make_cube_by_samples_temporal_groups <-
  function(samples,
           temporal_group,
           ...,
           collection) {
    if (!all(c("start_date", "end_date") %in% colnames(samples))) {
      stop(sprintf("samples must have `start_date` and `end_date` attributes"),
           call. = FALSE)
    }

    # select samples by group
    sample_temporal_group <-
      dplyr::filter(samples, start_date == temporal_group)

    # extract temporal extent
    start_date <- min(sample_temporal_group$start_date)
    end_date   <- max(sample_temporal_group$end_date)

    sits::sits_cube(
      source      = "BDC",
      name        = paste(
        "cube_temporal-group",
        temporal_group,
        start_date,
        end_date,
        sep = "_"
      ),
      start_date  = start_date,
      end_date    = end_date,
      collection  = collection,
      ...
    )
  }
