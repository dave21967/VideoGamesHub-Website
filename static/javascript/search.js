function search() {
    var text = $("#searchbar").val();
    var xhttp = new XMLHttpRequest();
    xhttp.open("GET", "/articles?titolo="+text, true);
    xhttp.send();

    xhttp.onreadystatechange = function() {
        if(xhttp.readyState == XMLHttpRequest.DONE) {
            return;
        }
    }
}