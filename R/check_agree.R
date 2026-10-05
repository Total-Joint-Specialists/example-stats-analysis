# check_agree(): the hidden guard at the end of each test section on a
# tutorial page. It stops the render when R and Python disagree.
#
#   r    named list of single numbers, e.g. list(t = 2.41, p = 0.017)
#   py   the same, from Python, e.g. list(t = reticulate::py$t_stat, ...)
#   tol  allowed difference, relative to the larger magnitude
#        (absolute for magnitudes below 1)

check_agree <- function(r, py, tol = 1e-6) {
  if (!is.list(r) || !is.list(py) || is.null(names(r)) || is.null(names(py))) {
    stop("check_agree(): both arguments must be named lists", call. = FALSE)
  }
  if (!setequal(names(r), names(py))) {
    stop(sprintf("check_agree(): R has [%s] but Python has [%s]",
                 paste(sort(names(r)), collapse = ", "),
                 paste(sort(names(py)), collapse = ", ")), call. = FALSE)
  }
  for (nm in names(r)) {
    a <- r[[nm]]
    b <- py[[nm]]
    if (!is.numeric(a) || length(a) != 1 || !is.numeric(b) || length(b) != 1) {
      stop(sprintf("check_agree(): '%s' must be a single number in both languages (wrap Python values in float())", nm),
           call. = FALSE)
    }
    if (!is.finite(a) || !is.finite(b)) {
      stop(sprintf("check_agree(): '%s' is not a finite number (R = %s, Python = %s)", nm, a, b),
           call. = FALSE)
    }
    if (abs(a - b) > tol * max(1, abs(a), abs(b))) {
      stop(sprintf("check_agree(): R and Python disagree on '%s': R = %.10g, Python = %.10g",
                   nm, a, b), call. = FALSE)
    }
  }
  invisible(TRUE)
}
