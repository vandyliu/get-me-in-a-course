$person=$args[0]
if ($person -eq $null) {
    $person = "vandy"
}
docker build -t courseubc:latest .
docker run -t courseubc:latest $person