# Write a tidy dataset: drop latent "."-prefixed helper columns, ISO dates,
# missing values as blank cells (read as missing by both readr and pandas).
write_tidy <- function(df, path) {
  df <- dplyr::select(df, !dplyr::starts_with("."))
  readr::write_csv(df, path, na = "")
  invisible(path)
}

# Record an MD5 for every CSV under `dir` ("<md5>  <path>", the format
# `md5sum -c` reads). CI has no R; tests/python checks the CSVs against this.
write_checksums <- function(dir) {
  files <- sort(list.files(dir, pattern = "[.]csv$", recursive = TRUE))
  sums <- unname(tools::md5sum(file.path(dir, files)))
  writeLines(paste0(sums, "  ", files), file.path(dir, "CHECKSUMS.md5"))
  invisible(file.path(dir, "CHECKSUMS.md5"))
}
