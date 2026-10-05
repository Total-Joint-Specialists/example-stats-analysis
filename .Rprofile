source("renv/activate.R")

# Point reticulate at this project's uv environment (created by `uv sync`).
# People who only use R, and never ran `uv sync`, are unaffected.
local({
  py <- if (.Platform$OS.type == "windows") {
    file.path(getwd(), ".venv", "Scripts", "python.exe")
  } else {
    file.path(getwd(), ".venv", "bin", "python")
  }
  if (file.exists(py)) Sys.setenv(RETICULATE_PYTHON = py)
})
