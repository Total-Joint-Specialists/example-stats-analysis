wb_path <- data_path("messy_abstraction_workbook.xlsx")
key <- read_tidy("answer-keys/abstraction_workbook_tidy.csv")

raw_sheet <- function(sheet) {
  readxl::read_excel(wb_path, sheet = sheet, col_names = FALSE, col_types = "text",
                     .name_repair = "minimal")
}

test_that("two site tabs whose columns do not line up", {
  expect_equal(readxl::excel_sheets(wb_path), c("Site A", "Site B"))
  a <- raw_sheet("Site A")
  b <- raw_sheet("Site B")
  expect_equal(ncol(b), ncol(a) + 1)
  expect_true("MUA" %in% unlist(b[4, ]))
  expect_false("MUA" %in% unlist(a[4, ]))
})

test_that("each tab holds its answer-key cases, two duplicates, and a totals row", {
  for (s in c("Site A", "Site B")) {
    raw <- raw_sheet(s)
    ids <- trimws(raw[[3]][-(1:4)])
    case_ids <- ids[!is.na(ids) & grepl("^C\\d{4}$", ids)]
    expect_setequal(unique(case_ids), key$case_id[key$site == s])
    expect_equal(sum(duplicated(case_ids)), 2)
    expect_equal(raw[[1]][nrow(raw)], "TOTAL")
  }
})

test_that("names and MRNs in the workbook are obviously fake", {
  for (s in c("Site A", "Site B")) {
    body <- raw_sheet(s)[-(1:4), ]
    body <- body[!is.na(body[[1]]) & body[[1]] != "TOTAL", ]
    expect_true(all(grepl("^TESTPATIENT, ", body[[1]])))
    expect_true(all(grepl("^SYN-\\d{6}$", body[[2]])))
  }
})

test_that("the answer key matches the cohort and carries no names or MRNs", {
  cohort <- read_tidy("cohort.csv")
  expect_equal(nrow(key), 120)
  expect_true(all(key$case_id %in% cohort$case_id))
  expect_false(any(grepl("TESTPATIENT|SYN-", unlist(key))))
  j <- dplyr::left_join(key, cohort, by = "case_id", suffix = c("", "_cohort"))
  for (col in c("site", "surgery_date", "age", "sex", "procedure", "side", "revised")) {
    expect_equal(j[[col]], j[[paste0(col, "_cohort")]], label = col)
  }
})

test_that("text dates use English month names whatever the computer's locale", {
  env <- new.env()
  sys.source(testthat::test_path("..", "..", "data-raw", "R", "gen_messy_workbook.R"), envir = env)
  withr::local_locale(c(LC_TIME = "de_CH.UTF-8"))
  skip_if_not(grepl("de_CH", Sys.getlocale("LC_TIME")), "de_CH locale not installed")
  withr::local_seed(1)
  out <- env$fmt_date_text(rep(as.Date("2024-03-04"), 50))
  expect_setequal(out, c("3/4/24", "2024-03-04", "March 4 2024"))
})
