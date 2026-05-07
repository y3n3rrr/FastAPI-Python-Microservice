param(
    [Parameter(Position = 0)]
    [ValidateSet("up", "down", "new", "history", "current", "heads", "stamp")]
    [string]$Command = "up",

    [Parameter(Position = 1)]
    [string]$Arg1 = "",

    [Parameter(Position = 2)]
    [string]$Arg2 = ""
)

$ErrorActionPreference = "Stop"

function Resolve-Alembic {
    if (Test-Path ".\.venv\Scripts\alembic.exe") {
        return ".\.venv\Scripts\alembic.exe"
    }
    if (Get-Command alembic -ErrorAction SilentlyContinue) {
        return "alembic"
    }
    throw "Alembic is not installed. Run: .\.venv\Scripts\python.exe -m pip install -e ."
}

function Run-Alembic {
    param([string[]]$AlembicArgs)
    $alembic = Resolve-Alembic
    & $alembic @AlembicArgs
    if ($LASTEXITCODE -ne 0) {
        throw "Alembic command failed: alembic $($AlembicArgs -join ' ')"
    }
}

switch ($Command) {
    "up" {
        $target = if ($Arg1) { $Arg1 } else { "head" }
        Run-Alembic -AlembicArgs @("upgrade", $target)
    }
    "down" {
        $target = if ($Arg1) { $Arg1 } else { "-1" }
        Run-Alembic -AlembicArgs @("downgrade", $target)
    }
    "new" {
        if (-not $Arg1) {
            throw "Usage: .\scripts\migrate.ps1 new ""message"" [--autogenerate]"
        }
        $args = @("revision", "-m", $Arg1)
        if ($Arg2 -eq "--autogenerate") {
            $args += "--autogenerate"
        }
        Run-Alembic -AlembicArgs $args
    }
    "history" {
        Run-Alembic -AlembicArgs @("history", "--verbose")
    }
    "current" {
        Run-Alembic -AlembicArgs @("current")
    }
    "heads" {
        Run-Alembic -AlembicArgs @("heads")
    }
    "stamp" {
        $target = if ($Arg1) { $Arg1 } else { "head" }
        Run-Alembic -AlembicArgs @("stamp", $target)
    }
}
