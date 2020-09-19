window.URL = window.URL || window.webkitURL;

const userNameElement = document.getElementById("userName"),
      fileInputElement = document.getElementById("fileInput"),
      fileListElement = document.getElementById("fileList");

function handleFiles(files) {
  const userName = userNameElement.value;

  if (!files.length) {
    fileListElement.innerHTML = "<ul><li>No files selected.</li></ul>";
  } else {
    fileListElement.innerHTML = "";

    const list = document.createElement("ul");
    fileListElement.appendChild(list);

    for (const file of files) {
      const li = document.createElement("li");
      list.appendChild(li);

      const span = document.createElement("span");
      span.classList.add("file");
      span.innerHTML = userName + "-" + file.name + ": " + (file.size / 1024).toFixed(2) + " kilobytes";
      li.appendChild(span);
    }
  }
}