window.URL = window.URL || window.webkitURL;

var userNameElement = document.getElementById("userName"),
    fileInputElement = document.getElementById("fileInput"),
    fileListElement = document.getElementById("fileList");

function handleFiles(files) {  
  var userName = userNameElement.value;

  if (!files.length) {
    fileListElement.innerHTML = "<ul><li>No files selected.</li></ul>";
  } else {
    fileListElement.innerHTML = "";
    
    var list = document.createElement("ul");
    fileListElement.appendChild(list);
    
    for (var i = 0; i < files.length; i++) {
      var file = files[i];
      
      var li = document.createElement("li");
      list.appendChild(li);
      
      var span = document.createElement("span");
      span.classList.add("schematic");
      span.innerHTML = userName + "-" + files[i].name + ": " + files[i].size + " bytes";
      li.appendChild(span);
    }
  }
}