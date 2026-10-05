# Write a tidy dataset: drop latent "."-prefixed helper columns, ISO dates,
# missing values as blank cells (read as missing by both readr and pandas).
write_tidy <- function(df, path) {
  df <- dplyr::select(df, !dplyr::starts_with("."))
  readr::write_csv(df, path, na = "")
  invisible(path)
}
