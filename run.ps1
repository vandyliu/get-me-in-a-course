$person=$args[0]
if ($person -eq $null) {
    $person = "vandy"
}
docker build -t fit4less:latest .
docker run -t fit4less:latest $person