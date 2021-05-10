function checkUsers() {
  var email = $("#textInput-email").val();
  var username = $("#textInput-username").val();
  var password = $("#textInput-password").val();
  xhttp = new XMLHttpRequest();
  xhttp.open("GET", "/check-users?username="+username+"&password="+password+"&email="+email, true);
  xhttp.send();
  xhttp.onreadystatechange = function() {
    if(xhttp.readyState == 4) {
      console.log(xhttp.responseText);
    }
  }
}

$("#textInput-password").on("change", function() {
  checkUsers();
});