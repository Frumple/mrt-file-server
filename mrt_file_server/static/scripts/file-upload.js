window.URL = window.URL || window.webkitURL;

const userNameElement = document.getElementById("userName"),
      fileInputElement = document.getElementById("fileInput"),
      fileListElement = document.getElementById("fileList");

function handleFiles(files, prependUserName = false) {
  const userName = userNameElement.value;

  removeAllChildElements(fileListElement);

  const list = document.createElement("ul");
  fileListElement.appendChild(list);

  if (files.length === 0) {
    const li = document.createElement("li");
    list.appendChild(li);

    const span = document.createElement("span");
    span.textContent = "No files selected."
    li.appendChild(span);
  } else {
    for (const file of files) {
      const li = document.createElement("li");
      list.appendChild(li);

      const span = document.createElement("span");
      span.classList.add("file");

      let text = file.name.concat(": ", (file.size / 1024).toFixed(2), " kilobytes");
      if (prependUserName) {
        text = userName.concat("-", text);
      }
      span.textContent = text;
      li.appendChild(span);
    }
  }
}

function removeAllChildElements(element) {
  while (element.firstChild) {
    element.firstChild.remove();
  }
}