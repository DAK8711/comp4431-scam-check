param(
    [Parameter(Mandatory = $true)][string]$TextFile,
    [Parameter(Mandatory = $true)][string]$WaveFile,
    [int]$Rate = -1,
    [string]$Voice = ""
)

# Reads the warning aloud using the voices built into Windows.
# Called from speech.py. Kept as a separate file so no text has to be
# escaped into a command line.

$ErrorActionPreference = "Stop"
Add-Type -AssemblyName System.Speech

$text = Get-Content -LiteralPath $TextFile -Raw -Encoding UTF8

$synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
try {
    if ($Voice -ne "") {
        $synth.SelectVoice($Voice)
    }
    # -1 is slightly slower than normal: elderly listeners need the pause.
    $synth.Rate = $Rate
    $synth.SetOutputToWaveFile($WaveFile)
    $synth.Speak($text)
}
finally {
    $synth.Dispose()
}
