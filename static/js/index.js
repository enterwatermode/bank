$(document).ready(function() {
    $("button").click(function(event){
        sessionStorage.setItem('id', document.getElementById('id').value)
    });
});